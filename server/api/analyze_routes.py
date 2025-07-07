from flask import Blueprint, request

from server.analysis.enhancer import Enhancer
from server.analysis.log_analysis_pipeline import ManualTrainTestPipeline
from server.analysis.utils.data_filtering import (
    filter_files,
    get_file_name_by_orig_file_name,
    get_prediction_cols,
)
from server.analysis.utils.file_level_analysis import (
    aggregate_file_level,
    unique_terms_count_by_file,
)
from server.analysis.utils.log_distance import measure_distances
from server.analysis.utils.run_level_analysis import (
    aggregate_run_level,
    calculate_zscore_sum_anos,
    files_and_lines_count,
    unique_terms_count_by_run,
)
from server.analysis.utils.umap_analysis import create_umap_df, create_umap_embeddings
from server.api.api_helpers import (
    handle_errors,
    load_data,
    store_and_format_result,
    validate_request_data,
)
from server.api.validator_models.anomaly_detection_params import AnomalyDetectionParams
from server.api.validator_models.high_level_analysis_params import (
    FileCountsParams,
    UmapParams,
    UniqueTermsParams,
)
from server.api.validator_models.log_distance_params import LogDistanceParams

analyze_bp = Blueprint("main", __name__)


@analyze_bp.route("/manual-test-train/<int:project_id>", methods=["POST"])
def manual_test_train(project_id):
    validation_result = validate_request_data(AnomalyDetectionParams, request)
    if isinstance(validation_result, tuple):
        return validation_result

    train_data_path = validation_result.train_data_path
    test_data_path = validation_result.test_data_path
    models = validation_result.models
    item_list_col = validation_result.item_list_col
    log_format = validation_result.log_format
    runs_to_include = validation_result.runs_to_include
    run_level = validation_result.run_level
    files_to_include = validation_result.files_to_include
    file_level = validation_result.file_level
    mask_type = validation_result.mask_type
    vectorizer = validation_result.vectorizer

    results = None
    pipeline = None

    # TODO: Rather than getting boolean values, take str for level
    if file_level:
        level = "file"
    elif run_level:
        level = "directory"
    else:
        level = "line"

    try:
        pipeline = ManualTrainTestPipeline(
            model_names=models,
            item_list_col=item_list_col,
            log_format=log_format,
            vectorizer=vectorizer,
            train_data_path=train_data_path,
            test_data_path=test_data_path,
            runs_to_include=runs_to_include,
            files_to_include=files_to_include,
            mask_type=mask_type,
        )

        pipeline.load()
        pipeline.enhance()

        # TODO: add setting/input to specify if files are analysed against other files with the same file name,
        #  or against all files disregarding file name
        mock_flag = True

        if mock_flag:
            if level == "file":
                pipeline.analyze_file_group_by_filenames()
            elif level == "line":
                pipeline.analyze_line_group_by_filenames()
            else:
                pipeline.aggregate_to_run_level()
                pipeline.analyze()
        else:
            if level == "file":
                pipeline.aggregate_to_file_level()
            elif level == "directory":
                pipeline.aggregate_to_run_level()
            pipeline.analyze()

        results = pipeline.results
        if results is None:
            raise ValueError("No results found")

        # TODO: fix sorting for LO2 data
        if log_format != "raw":
            results = results.sort(["run"])

        if run_level or file_level:
            results = calculate_zscore_sum_anos(
                results, distance_columns=get_prediction_cols(results)
            )
            results = results.drop(item_list_col)

        analysis_type = f"ano-{level}-level"

        metadata = {
            "train_data_path": train_data_path,
            "test_data_path": test_data_path,
            "vectorizer": str(vectorizer),
            "mask_type": mask_type,
            "models": ";".join(models),
            "analysis_level": level,
        }

        return store_and_format_result(results, project_id, analysis_type, metadata)

    except Exception as e:
        return handle_errors(project_id, "anomaly detection", e)


@analyze_bp.route("/unique-terms/<project_id>", methods=["POST"])
def run_unique_terms(project_id):
    validation_result = validate_request_data(UniqueTermsParams, request)
    if isinstance(validation_result, tuple):
        return validation_result

    dir_path = validation_result.directory_path
    item_list_col = validation_result.item_list_col
    file_level = validation_result.file_level

    try:
        df = load_data(dir_path)

        if not file_level:
            unique_terms_count = unique_terms_count_by_run(df, item_list_col)
        else:
            unique_terms_count = unique_terms_count_by_file(df, item_list_col)

        analysis_type = (
            "directory-level-visualisations"
            if not file_level
            else "file-level-visualisations"
        )
        metadata = {
            "analysis_sub_type": "unique-terms",
            "analysis_level": "directory" if not file_level else "file",
            "directory_path": dir_path,
        }
        return store_and_format_result(
            unique_terms_count, project_id, analysis_type, metadata
        )

    except Exception as e:
        return handle_errors(project_id, "unique terms", e)


@analyze_bp.route("/umap/<int:project_id>", methods=["POST"])
def create_umap(project_id):
    validation_result = validate_request_data(UmapParams, request)
    if isinstance(validation_result, tuple):
        return validation_result

    dir_path = validation_result.directory_path
    item_list_col = validation_result.item_list_col
    file_level = validation_result.file_level
    vectorizer = validation_result.vectorizer
    mask_type = validation_result.mask_type

    try:
        df = load_data(dir_path)
        if not file_level:
            df_run = (
                aggregate_run_level(df, item_list_col, mask_type)
                .select(item_list_col)
                .to_series()
                .to_list()
            )
            embeddings = create_umap_embeddings(df_run, vectorizer)
            result = create_umap_df(df, embeddings)
        else:
            df_file = (
                aggregate_file_level(df, item_list_col, mask_type)
                .select(item_list_col)
                .to_series()
                .to_list()
            )
            embeddings = create_umap_embeddings(df_file, vectorizer)
            result = create_umap_df(df, embeddings, group_col="seq_id")

        analysis_type = (
            "directory-level-visualisations"
            if not file_level
            else "file-level-visualisations"
        )
        metadata = {
            "analysis_sub_type": "umap",
            "analysis_level": "directory" if not file_level else "file",
            "mask_type": mask_type,
            "vectorizer": str(vectorizer),
            "directory_path": dir_path,
        }

        return store_and_format_result(result, project_id, analysis_type, metadata)

    except Exception as e:
        return handle_errors(project_id, "UMAP", e)


@analyze_bp.route("/run-file-counts/<int:project_id>", methods=["POST"])
def run_file_counts(project_id):
    validation_result = validate_request_data(FileCountsParams, request)
    if isinstance(validation_result, tuple):
        return validation_result

    dir_path = validation_result.directory_path

    try:
        df = load_data(dir_path)
        result = files_and_lines_count(df)

        metadata = {
            "analysis_level": "directory",
            "directory_path": dir_path,
            "analysis_sub_type": "file-count",
        }

        return store_and_format_result(
            result, project_id, "directory-level-visualisations", metadata
        )

    except Exception as e:
        return handle_errors(project_id, "file counts", e)


@analyze_bp.route("/log-distance/<int:project_id>", methods=["POST"])
def run_distance(project_id):
    validation_result = validate_request_data(LogDistanceParams, request)
    if isinstance(validation_result, tuple):
        return validation_result

    dir_path = validation_result.directory_path
    target_run = validation_result.target_run
    comparison_runs = validation_result.comparison_runs
    item_list_col = validation_result.item_list_col
    file_level = validation_result.file_level
    mask_type = validation_result.mask_type
    vectorizer = validation_result.vectorizer

    try:
        enhancer = Enhancer(load_data(dir_path))
        df = enhancer.enhance_event(item_list_col, mask_type)

        # TODO: Add a setting to change if comparisons are done against matching file names
        if file_level and comparison_runs in (None, []):
            target_file_name = get_file_name_by_orig_file_name(df, target_run)
            df = filter_files(df, [target_file_name], "file_name")

        run_column = "run" if not file_level else "orig_file_name"
        result = measure_distances(
            df,
            item_list_col,
            target_run,
            run_column=run_column,
            comparison_runs=comparison_runs,
            vectorizer=vectorizer,
        )

        metadata = {
            "analysis_level": "directory" if not file_level else "file",
            "mask_type": mask_type,
            "vectorizer": str(vectorizer),
            "directory_path": dir_path,
            "target": target_run,
        }

        analysis_type = (
            "distance-file-level" if file_level else "distance-directory-level"
        )

        return store_and_format_result(result, project_id, analysis_type, metadata)

    except Exception as e:
        return handle_errors(project_id, "log distance", e)

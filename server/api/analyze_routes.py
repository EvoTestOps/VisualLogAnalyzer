from flask import Blueprint, jsonify, request

from server.analysis.enhancer import Enhancer
from server.analysis.log_analysis_pipeline import ManualTrainTestPipeline
from server.analysis.utils.data_filtering import (
    filter_files,
    get_file_name_by_orig_file_name,
    get_prediction_cols,
)
from server.analysis.utils.log_distance import measure_distances
from server.analysis.utils.run_level_analysis import (
    calculate_zscore_sum_anos,
)
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
from server.models.settings import Settings
from server.tasks import (
    async_create_umap,
    async_run_file_counts,
    async_run_unique_terms,
    async_log_distance,
)

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

    settings = Settings.query.filter_by(project_id=project_id).first_or_404()
    match_filenames = settings.match_filenames

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

        if match_filenames:
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
            raise ValueError("Analysis failed to create results")

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
            "analysis_sub_type": "anomaly-detection",
            "test_data_path": test_data_path,
            "vectorizer": str(vectorizer),
            "item_list_col": item_list_col,
            "mask_type": mask_type,
            "models": ";".join(models),
            "analysis_level": level,
        }

        return store_and_format_result(results, project_id, analysis_type, metadata)

    except Exception as e:
        return handle_errors(project_id, "anomaly detection", e)


@analyze_bp.route("/unique-terms/<int:project_id>", methods=["POST"])
def run_unique_terms(project_id: int):
    validation_result = validate_request_data(UniqueTermsParams, request)
    if isinstance(validation_result, tuple):
        return validation_result

    dir_path = validation_result.directory_path
    item_list_col = validation_result.item_list_col
    file_level = validation_result.file_level

    task = async_run_unique_terms.delay(project_id, dir_path, item_list_col, file_level)

    return jsonify({"task_id": task.id}), 202


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

    task = async_create_umap.delay(
        project_id, dir_path, item_list_col, file_level, vectorizer, mask_type
    )

    return jsonify({"task_id": task.id}), 202


@analyze_bp.route("/file-counts/<int:project_id>", methods=["POST"])
def run_file_counts(project_id: int):
    validation_result = validate_request_data(FileCountsParams, request)
    if isinstance(validation_result, tuple):
        return validation_result

    dir_path = validation_result.directory_path

    task = async_run_file_counts.delay(project_id, dir_path)
    return jsonify({"task_id": task.id}), 202


@analyze_bp.route("/log-distance/<int:project_id>", methods=["POST"])
def log_distance(project_id):
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

    task = async_log_distance.delay(
        project_id,
        dir_path,
        target_run,
        comparison_runs,
        item_list_col,
        file_level,
        mask_type,
        vectorizer,
    )
    return jsonify({"task_id": task.id}), 202

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
from server.analysis.utils.line_level_analysis import (
    calculate_moving_average_by_columns,
)
from server.analysis.utils.log_distance import measure_distances
from server.analysis.utils.run_level_analysis import (
    aggregate_run_level,
    calculate_zscore_sum_anos,
    files_and_lines_count,
    unique_terms_count_by_run,
)
from server.analysis.utils.umap_analysis import create_umap_df, create_umap_embeddings
from server.models.settings import Settings
from server.analysis.utils.analysis_helpers import (
    create_vectorizer,
    load_data,
    store_and_format_result,
)


def run_file_count_analysis(
    project_id: int,
    analysis_name: str | None,
    directory_path: str,
    log=lambda msg: None,
) -> dict:
    log(f"Loading data from directory: {directory_path}")
    df = load_data(directory_path)

    log("Counting files and lines")
    result = files_and_lines_count(df)

    log("Storing and formatting results")
    metadata = {
        "analysis_level": "directory",
        "directory_path": directory_path,
        "analysis_sub_type": "file-count",
        "name": analysis_name,
    }
    result = store_and_format_result(
        result, project_id, "directory-level-visualisations", metadata
    )

    log("Analysis complete")
    del df
    return result


def run_unique_terms_analysis(
    project_id: int,
    analysis_name: str | None,
    directory_path: str,
    item_list_col: str,
    file_level: bool,
    mask_type: str | None,
    log=lambda msg: None,
) -> dict:
    log(f"Loading data from directory: {directory_path}")
    df = load_data(directory_path)
    if not file_level:
        log("Counting unique terms by directory")
        unique_terms_count = unique_terms_count_by_run(df, item_list_col, mask_type)
    else:
        log("Counting unique terms by file")
        unique_terms_count = unique_terms_count_by_file(df, item_list_col, mask_type)

    log("Storing and formatting results")
    analysis_type = (
        "directory-level-visualisations"
        if not file_level
        else "file-level-visualisations"
    )
    metadata = {
        "analysis_sub_type": "unique-terms",
        "analysis_level": "directory" if not file_level else "file",
        "directory_path": directory_path,
        "mask_type": mask_type,
        "name": analysis_name,
    }

    result = store_and_format_result(
        unique_terms_count, project_id, analysis_type, metadata
    )

    log("Analysis complete")
    del df
    return result


def run_umap_analysis(
    project_id: int,
    analysis_name: str | None,
    directory_path: str,
    item_list_col: str,
    file_level: bool,
    vectorizer: str,
    mask_type: str | None,
    log=lambda msg: None,
) -> dict:
    log(f"Loading data from directory: {directory_path}")
    df = load_data(directory_path)

    log(f"Creating {vectorizer} vectorizer")
    vectorizer_object = create_vectorizer(vectorizer)

    aggregate_func = aggregate_run_level if not file_level else aggregate_file_level
    group_col = "run" if not file_level else "seq_id"

    log(f"Aggregating data with function: {aggregate_func}")
    df_agg = (
        aggregate_func(df, item_list_col, mask_type)
        .select(item_list_col)
        .to_series()
        .to_list()
    )

    log("Creating umap embeddings")
    embeddings = create_umap_embeddings(df_agg, vectorizer_object)

    log("Creating umap dataframe")
    umap_df = create_umap_df(df, embeddings, group_col=group_col)

    log("Storing and formatting results")
    analysis_type = (
        "directory-level-visualisations"
        if not file_level
        else "file-level-visualisations"
    )
    metadata = {
        "analysis_sub_type": "umap",
        "analysis_level": "directory" if not file_level else "file",
        "mask_type": mask_type,
        "vectorizer": vectorizer,
        "directory_path": directory_path,
        "name": analysis_name,
    }

    result = store_and_format_result(umap_df, project_id, analysis_type, metadata)

    log("Analysis complete")
    del umap_df
    del embeddings

    return result


def run_log_distance_analysis(
    project_id: int,
    analysis_name: str | None,
    directory_path: str,
    target_run: str,
    comparison_runs: list[str] | None,
    item_list_col: str,
    file_level: bool,
    mask_type: str | None,
    vectorizer: str,
    log=lambda msg: None,
) -> dict:
    log("Getting match filenames setting")
    settings = Settings.query.filter_by(project_id=project_id).first_or_404()
    match_filenames = settings.match_filenames

    log(f"Creating {vectorizer} vectorizer")
    vectorizer_object = create_vectorizer(vectorizer)

    log("Loading data")
    enhancer = Enhancer(load_data(directory_path))

    log(f"Enhancing data with enhancement: {item_list_col} and mask: {mask_type}")
    df = enhancer.enhance_event(item_list_col, mask_type)

    match_flag = file_level and comparison_runs in (None, []) and match_filenames
    if match_flag:
        # FIX: not an optimal way to get filename
        log("Matching filenames")
        target_file_name = get_file_name_by_orig_file_name(df, target_run)
        df = filter_files(df, [target_file_name], "file_name")

    run_column = "run" if not file_level else "orig_file_name"

    log("Measuring distances")
    df_distances = measure_distances(
        df,
        item_list_col,
        target_run,
        run_column=run_column,
        comparison_runs=comparison_runs,
        vectorizer=vectorizer_object,
    )

    log("Storing and formatting results")
    metadata = {
        "analysis_level": "directory" if not file_level else "file",
        "analysis_sub_type": "log-distance",
        "mask_type": mask_type,
        "vectorizer": vectorizer,
        "directory_path": directory_path,
        "target": target_run,
        "match_filenames": match_filenames if match_flag else None,
        "name": analysis_name,
    }
    analysis_type = "distance-file-level" if file_level else "distance-directory-level"

    result = store_and_format_result(df_distances, project_id, analysis_type, metadata)

    log("Analysis complete")
    del df
    del df_distances

    return result


def run_anomaly_detection_analysis(
    project_id: int,
    analysis_name: str | None,
    train_data_path: str,
    test_data_path: str,
    models: list[str],
    item_list_col: str,
    runs_to_include: list[str] | None,
    runs_to_include_train: list[str] | None,
    files_to_include: list[str] | None,
    files_to_include_train: list[str] | None,
    file_level: bool,
    directory_level: bool,
    mask_type: str,
    vectorizer: str,
    log=lambda msg: None,
) -> dict:

    # TODO: Rather than getting boolean values, take str for level
    if file_level:
        level = "file"
    elif directory_level:
        level = "directory"
    else:
        level = "line"

    log("Getting match filenames setting")
    settings = Settings.query.filter_by(project_id=project_id).first_or_404()
    match_filenames = settings.match_filenames

    log(f"Creating {vectorizer} vectorizer")
    vectorizer_object = create_vectorizer(vectorizer)
    pipeline = ManualTrainTestPipeline(
        model_names=models,
        item_list_col=item_list_col,
        vectorizer=vectorizer_object,
        train_data_path=train_data_path,
        test_data_path=test_data_path,
        runs_to_include=runs_to_include,
        runs_to_include_train=runs_to_include_train,
        files_to_include=files_to_include,
        files_to_include_train=files_to_include_train,
        mask_type=mask_type,
    )

    log("Loading data")
    pipeline.load()

    log(f"Enhancing data with enhancement: {item_list_col} and mask: {mask_type}")
    pipeline.enhance()

    log("Running anomaly detection")
    log(f"Running with models: {models}")
    if match_filenames:
        log("Match filenames is on")
        if level == "file":
            pipeline.analyze_file_group_by_filenames()
        elif level == "line":
            pipeline.analyze_line_group_by_filenames()
        else:
            log("Not matching filenames since level is directory")
            pipeline.aggregate_to_run_level()
            pipeline.analyze()
    else:
        log("Match filenames is off")
        if level == "file":
            pipeline.aggregate_to_file_level()
        elif level == "directory":
            pipeline.aggregate_to_run_level()
        pipeline.analyze()

    log("Anomaly detection is complete")
    results = pipeline.results
    if results is None:
        raise ValueError("Analysis failed to create results")

    if directory_level or file_level:
        log("Normalizing distance measures")
        results = calculate_zscore_sum_anos(
            results, distance_columns=get_prediction_cols(results)
        )
        results = results.drop(item_list_col)

    if level == "line":
        log("Calculating moving averages")
        prediction_columns = [col for col in results.columns if "pred_ano_proba" in col]
        df_moving_avg_100 = calculate_moving_average_by_columns(
            results, 100, prediction_columns
        )
        df_moving_avg_10 = calculate_moving_average_by_columns(
            results, 10, prediction_columns
        )
        results = results.with_columns(df_moving_avg_100)
        results = results.with_columns(df_moving_avg_10)

    analysis_type = f"ano-{level}-level"
    metadata = {
        "train_data_path": train_data_path,
        "test_data_path": test_data_path,
        "analysis_sub_type": "anomaly-detection",
        "vectorizer": vectorizer,
        "item_list_col": item_list_col,
        "mask_type": mask_type,
        "models": ";".join(models),
        "analysis_level": level,
        "match_filenames": match_filenames if level != "directory" else None,
        "name": analysis_name,
    }

    log("Storing and formatting results")
    result = store_and_format_result(results, project_id, analysis_type, metadata)

    log("Analysis complete")
    del pipeline
    return result

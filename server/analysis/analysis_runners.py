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
) -> dict:
    df = load_data(directory_path)
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
        "directory_path": directory_path,
        "name": analysis_name,
    }

    result = store_and_format_result(
        unique_terms_count, project_id, analysis_type, metadata
    )

    del df

    return result


def run_umap_analysis(
    project_id: int,
    analysis_name: str | None,
    directory_path: str,
    item_list_col: str,
    file_level: bool,
    vectorizer: str,
    mask_type: str,
) -> dict:
    df = load_data(directory_path)

    vectorizer_object = create_vectorizer(vectorizer)
    aggregate_func = aggregate_run_level if not file_level else aggregate_file_level
    group_col = "run" if not file_level else "seq_id"

    df_agg = (
        aggregate_func(df, item_list_col, mask_type)
        .select(item_list_col)
        .to_series()
        .to_list()
    )

    embeddings = create_umap_embeddings(df_agg, vectorizer_object)
    umap_df = create_umap_df(df, embeddings, group_col=group_col)

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
) -> dict:

    settings = Settings.query.filter_by(project_id=project_id).first_or_404()
    match_filenames = settings.match_filenames
    vectorizer_object = create_vectorizer(vectorizer)

    enhancer = Enhancer(load_data(directory_path))
    df = enhancer.enhance_event(item_list_col, mask_type)

    match_flag = file_level and comparison_runs in (None, []) and match_filenames
    if match_flag:
        # FIX: not an optimal way to get filename
        target_file_name = get_file_name_by_orig_file_name(df, target_run)
        df = filter_files(df, [target_file_name], "file_name")

    run_column = "run" if not file_level else "orig_file_name"

    df_distances = measure_distances(
        df,
        item_list_col,
        target_run,
        run_column=run_column,
        comparison_runs=comparison_runs,
        vectorizer=vectorizer_object,
    )

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
    files_to_include: list[str] | None,
    file_level: bool,
    directory_level: bool,
    mask_type: str,
    vectorizer: str,
) -> dict:

    # TODO: Rather than getting boolean values, take str for level
    if file_level:
        level = "file"
    elif directory_level:
        level = "directory"
    else:
        level = "line"

    settings = Settings.query.filter_by(project_id=project_id).first_or_404()
    match_filenames = settings.match_filenames

    vectorizer_object = create_vectorizer(vectorizer)
    pipeline = ManualTrainTestPipeline(
        model_names=models,
        item_list_col=item_list_col,
        vectorizer=vectorizer_object,
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

    if directory_level or file_level:
        results = calculate_zscore_sum_anos(
            results, distance_columns=get_prediction_cols(results)
        )
        results = results.drop(item_list_col)

    if level == "line":
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

    result = store_and_format_result(results, project_id, analysis_type, metadata)

    del pipeline

    return result

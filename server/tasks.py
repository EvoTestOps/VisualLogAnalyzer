from celery import shared_task
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from server.analysis.utils.run_level_analysis import (
    files_and_lines_count,
    unique_terms_count_by_run,
    aggregate_run_level,
)
from server.analysis.utils.file_level_analysis import (
    unique_terms_count_by_file,
    aggregate_file_level,
)
from server.task_helpers import (
    handle_errors,
    load_data,
    store_and_format_result,
)
from server.analysis.utils.umap_analysis import create_umap_df, create_umap_embeddings


@shared_task(ignore_results=False)
def async_run_file_counts(project_id: int, directory_path: str) -> dict:
    try:
        df = load_data(directory_path)
        result = files_and_lines_count(df)

        metadata = {
            "analysis_level": "directory",
            "directory_path": directory_path,
            "analysis_sub_type": "file-count",
        }

        return store_and_format_result(
            result, project_id, "directory-level-visualisations", metadata
        )
    except Exception as e:
        return handle_errors(project_id, "file counts", e)


@shared_task(ignore_results=False)
def async_run_unique_terms(
    project_id: int, directory_path: str, item_list_col: str, file_level: bool
) -> dict:
    try:
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
        }

        return store_and_format_result(
            unique_terms_count, project_id, analysis_type, metadata
        )
    except Exception as e:
        return handle_errors(project_id, "unique terms", e)


@shared_task(ignore_results=False)
def async_create_umap(
    project_id: int,
    directory_path: str,
    item_list_col: str,
    file_level: bool,
    vectorizer: str,
    mask_type: str,
):
    import logging

    logging.warning(file_level)
    try:
        df = load_data(directory_path)

        vectorizer_object = (
            CountVectorizer if vectorizer == "count" else TfidfVectorizer
        )

        aggregate_func = aggregate_run_level if not file_level else aggregate_file_level
        group_col = "run" if not file_level else "seq_id"

        df_agg = (
            aggregate_func(df, item_list_col, mask_type)
            .select(item_list_col)
            .to_series()
            .to_list()
        )

        embeddings = create_umap_embeddings(df_agg, vectorizer_object)
        result = create_umap_df(df, embeddings, group_col=group_col)

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
        }

        return store_and_format_result(result, project_id, analysis_type, metadata)
    except Exception as e:
        return handle_errors(project_id, "UMAP", e)

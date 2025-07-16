from celery import shared_task

from server.analysis.enhancer import Enhancer
from server.analysis.utils.data_filtering import (
    filter_files,
    get_file_name_by_orig_file_name,
)
from server.analysis.utils.file_level_analysis import (
    aggregate_file_level,
    unique_terms_count_by_file,
)
from server.analysis.utils.log_distance import measure_distances
from server.analysis.utils.run_level_analysis import (
    aggregate_run_level,
    files_and_lines_count,
    unique_terms_count_by_run,
)
from server.analysis.utils.umap_analysis import create_umap_df, create_umap_embeddings
from server.models.settings import Settings
from server.task_helpers import (
    create_vectorizer,
    handle_errors,
    load_data,
    store_and_format_result,
)


@shared_task(bind=True, ignore_results=False)
def async_run_file_counts(self, project_id: int, directory_path: str) -> dict:
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
        self.update_state(state="FAILURE", meta={"exc": e})
        return handle_errors(project_id, "file counts", e)


@shared_task(bind=True, ignore_results=False)
def async_run_unique_terms(
    self, project_id: int, directory_path: str, item_list_col: str, file_level: bool
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
        self.update_state(state="FAILURE", meta={"exc": e})
        return handle_errors(project_id, "unique terms", e)


@shared_task(bind=True, ignore_results=False)
def async_create_umap(
    self,
    project_id: int,
    directory_path: str,
    item_list_col: str,
    file_level: bool,
    vectorizer: str,
    mask_type: str,
) -> dict:
    try:
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
        self.update_state(state="FAILURE", meta={"exc": e})
        return handle_errors(project_id, "UMAP", e)


@shared_task(bind=True, ignore_results=False)
def async_log_distance(
    self,
    project_id: int,
    directory_path: str,
    target_run: str,
    comparison_runs: list[str] | None,
    item_list_col: str,
    file_level: bool,
    mask_type: str | None,
    vectorizer: str,
):
    try:
        settings = Settings.query.filter_by(project_id=project_id).first_or_404()
        match_filenames = settings.match_filenames
        vectorizer_object = create_vectorizer(vectorizer)

        enhancer = Enhancer(load_data(directory_path))
        df = enhancer.enhance_event(item_list_col, mask_type)

        # TODO: Refactor, this seems dubious
        if file_level and comparison_runs in (None, []) and match_filenames:
            target_file_name = get_file_name_by_orig_file_name(df, target_run)
            df = filter_files(df, [target_file_name], "file_name")

        run_column = "run" if not file_level else "orig_file_name"
        result = measure_distances(
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
        }
        analysis_type = (
            "distance-file-level" if file_level else "distance-directory-level"
        )

        return store_and_format_result(result, project_id, analysis_type, metadata)

    except Exception as e:
        self.update_state(state="FAILURE", meta={"exc": e})
        return handle_errors(project_id, "log distance", e)

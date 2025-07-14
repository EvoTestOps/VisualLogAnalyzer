from celery import shared_task
from server.analysis.utils.run_level_analysis import (
    files_and_lines_count,
)
from server.task_helpers import (
    handle_errors,
    load_data,
    store_and_format_result,
)


@shared_task(ignore_results=False)
def async_run_file_counts(project_id: int, directory_path: str):
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

import io

import polars as pl
import requests

from dash_app.utils.data_directories import (
    get_all_filenames,
    get_all_root_log_directories,
    get_runs,
)
from dash_app.utils.metadata import format_metadata_rows
from dash_app.utils.plots import (
    create_files_count_plot,
    create_umap_plot,
    create_unique_term_count_plot,
    create_unique_term_count_plot_by_file,
)


def run_high_level_analysis(
    project_id,
    directory_path,
    analysis_type,
    mask_type=None,
    vectorizer_type=None,
    level="directory",
):
    endpoint_map = {
        "files": "file-counts",
        "umap": "umap",
        "terms": "unique-terms",
    }
    endpoint = endpoint_map.get(analysis_type, "unique-terms")
    payload = {
        "dir_path": directory_path,
        "file_level": (level == "file"),
        "mask_type": mask_type,
        "vectorizer": vectorizer_type,
    }

    response, error = make_api_call(payload, f"{endpoint}/{project_id}")
    if error or response is None:
        raise ValueError(
            f"Was not able to run analysis for project {project_id}: {error}"
        )

    return response.json()


def run_log_distance(
    project_id,
    directory_path,
    target_run,
    comparison_runs,
    enhancement,
    vectorizer_type,
    mask_type=None,
    level="directory",
):

    payload = {
        "dir_path": directory_path,
        "target_run": target_run,
        "comparison_runs": comparison_runs,
        "item_list_col": enhancement,
        "mask_type": mask_type,
        "vectorizer": vectorizer_type,
        "file_level": (level == "file"),
    }
    response, error = make_api_call(payload, f"log-distance/{project_id}")
    if error or response is None:
        raise ValueError(
            f"Was not able to run analysis for project {project_id}: {error}"
        )
    return response.json()


def run_anomaly_detection(
    project_id,
    train_data,
    test_data,
    detectors,
    enhancement,
    include_items,
    mask_type,
    vectorizer_type,
    log_format="raw",
    level="directory",
):
    json_payload = _build_test_train_payload(
        train_data,
        test_data,
        log_format,
        detectors,
        enhancement,
        include_items,
        mask_type,
        vectorizer_type,
        level,
    )

    response, error = make_api_call(json_payload, f"manual-test-train/{project_id}")
    if error or response is None:
        raise ValueError(
            f"Was not able to run analysis for project {project_id}: {error}"
        )
    return response.json()


def populate_datatable(analysis_id):
    metadata = _fetch_analysis_metadata(analysis_id)
    project_id = metadata.get("project_id")
    metadata_rows = format_metadata_rows(metadata)

    results_content = _fetch_analysis_results(analysis_id)
    df_dict, columns = _parse_response_as_table(results_content)

    return df_dict, columns, metadata_rows, project_id


def create_high_level_plot(switch_on, analysis_id):
    metadata = _fetch_analysis_metadata(analysis_id)
    analysis_type = metadata.get("analysis_sub_type")
    analysis_level = metadata.get("analysis_level")
    project_id = metadata.get("project_id")

    if project_id is None:
        raise ValueError("Project id not found in metadata")

    try:
        project_id = int(project_id)
    except ValueError:
        raise ValueError("Project id not a valid integer")

    results = _fetch_analysis_results(analysis_id)
    df = pl.read_parquet(io.BytesIO(results))

    settings = _fetch_project_settings(project_id)
    color_by_directory = settings.get("color_by_directory")

    theme = "plotly_white" if switch_on else "plotly_dark"
    style = {
        "resize": "both",
        "overflow": "auto",
        "minHeight": "500px",
        "minWidth": "600px",
        "width": "90%",
    }

    if analysis_type == "file-count":
        fig = create_files_count_plot(df, theme)
    elif analysis_type == "umap":
        group_col = "run" if analysis_level == "directory" else "seq_id"
        fig = create_umap_plot(df, group_col, color_by_directory, theme)
    else:
        if analysis_level == "file":
            fig = create_unique_term_count_plot_by_file(df, color_by_directory, theme)
        else:
            fig = create_unique_term_count_plot(df, theme)

    metadata_rows = format_metadata_rows(metadata)

    return fig, style, metadata_rows, project_id


def make_api_call(json_payload, endpoint, requests_type="POST"):
    base_url = "http://localhost:5000/api"
    http_methods = {
        "POST": requests.post,
        "GET": requests.get,
        "DELETE": requests.delete,
        "PATCH": requests.patch,
    }
    try:
        http_func = http_methods.get(requests_type.upper())
        if not http_func:
            raise ValueError(f"Unsupported http method: {requests_type}")

        response = http_func(f"{base_url}/{endpoint}", json=json_payload)
        response.raise_for_status()
        return response, None

    except requests.exceptions.HTTPError as http_error:
        try:
            error_message = response.json().get("error", str(http_error))
        except Exception:
            error_message = str(http_error)
        return None, error_message
    except requests.exceptions.RequestException as req_error:
        return None, str(req_error)


def get_filter_options(data_path, runs_or_files="runs"):
    if data_path is None:
        return []

    if runs_or_files == "runs":
        items = get_runs(data_path)
    elif runs_or_files == "files":
        items = get_all_filenames(data_path)
    else:
        items = []

    options = [{"label": item, "value": item} for item in items]
    return options


def fetch_project_name(project_id: int) -> str:
    response, error = make_api_call(
        {}, f"projects/{project_id}/name", requests_type="GET"
    )
    if error or response is None:
        raise ValueError(f"Was not able to fetch project name: {error}")

    return response.json().get("name", "404")


def get_log_data_directory_options():
    labels, values = get_all_root_log_directories()
    return [{"label": lab, "value": val} for (lab, val) in zip(labels, values)]


def poll_task_status(task_id: int) -> dict:
    # There shouldn't be any error here unless the task_id is wrong.
    response, error = make_api_call({}, f"task-status/{task_id}", requests_type="GET")
    if error or response is None:
        raise ValueError(f"Was not able to fetch task status: {error}")

    return response.json()


def _fetch_project_settings(project_id: int) -> dict:
    response, error = make_api_call({}, f"projects/{project_id}/settings", "GET")
    if error or response is None:
        raise ValueError(
            f"Was not able to retrieve settings for project id {project_id}: {error}"
        )
    return response.json()


def _fetch_analysis_results(analysis_id: int) -> bytes:
    response, error = make_api_call({}, f"analyses/{analysis_id}", "GET")
    if error or response is None:
        raise ValueError(
            f"Was not able to retrieve results for analysis id {analysis_id}: {error}"
        )
    return response.content


def _fetch_analysis_metadata(analysis_id: int) -> dict:
    response_metadata, error = make_api_call(
        {}, f"analyses/{analysis_id}/metadata", "GET"
    )
    if error or response_metadata is None:
        raise ValueError(
            f"Was not able to retrieve metadata for analysis id {analysis_id}: {error}"
        )
    return response_metadata.json()


def _build_test_train_payload(
    train_data,
    test_data,
    log_format,
    detectors,
    enhancement,
    include_items,
    mask_type,
    vectorizer_type,
    level="directory",
):
    payload = {
        "train_data_path": train_data,
        "test_data_path": test_data,
        "log_format": log_format,
        "models": detectors,
        "item_list_col": enhancement,
        "mask_type": mask_type,
        "vectorizer": vectorizer_type,
    }

    if level == "directory":
        payload["runs_to_include"] = include_items
        payload["run_level"] = True
    elif level == "file":
        payload["files_to_include"] = include_items
        payload["file_level"] = True
    elif level == "line":
        payload["runs_to_include"] = include_items
        payload["file_level"] = False
        payload["run_level"] = False
    else:
        raise ValueError("Level must be either 'file' or 'directory'")

    return payload


def _parse_response_as_table(content):
    df = pl.read_parquet(io.BytesIO(content))
    columns = [{"name": col, "id": col} for col in df.columns]
    return df.to_dicts(), columns

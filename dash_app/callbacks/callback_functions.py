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
    log_format=None,
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
    response_metadata, error = make_api_call(
        {}, f"analyses/{analysis_id}/metadata", "GET"
    )
    if error or response_metadata is None:
        raise ValueError(
            f"Was not able to retrieve metadata for analysis id {analysis_id}: {error}"
        )
    metadata = response_metadata.json()
    project_id = metadata.get("project_id")
    project_name = metadata.get("project_name")
    metadata_rows = format_metadata_rows(metadata)

    response, error = make_api_call({}, f"analyses/{analysis_id}", "GET")
    if error or response is None:
        raise ValueError(
            f"Was not able to retrieve results for analysis id {analysis_id}: {error}"
        )
    df_dict, columns = _parse_response_as_table(response)

    return df_dict, columns, metadata_rows, project_id, project_name


def create_high_level_plot(switch_on, analysis_id):
    response_metadata, error = make_api_call(
        {}, f"analyses/{analysis_id}/metadata", "GET"
    )
    if error or response_metadata is None:
        raise ValueError(
            f"Was not able to retrieve metadata for analysis id {analysis_id}: {error}"
        )

    metadata = response_metadata.json()
    analysis_type = metadata.get("analysis_sub_type")
    analysis_level = metadata.get("analysis_level")
    project_id = metadata.get("project_id")
    project_name = metadata.get("project_name")

    response, error = make_api_call({}, f"analyses/{analysis_id}", "GET")
    if error or response is None:
        raise ValueError(
            f"Was not able to retrieve results for analysis id {analysis_id}: {error}"
        )

    df = pl.read_parquet(io.BytesIO(response.content))

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
        fig = create_umap_plot(df, group_col, theme)
    else:
        if analysis_level == "file":
            fig = create_unique_term_count_plot_by_file(df, theme)
        else:
            fig = create_unique_term_count_plot(df, theme)

    metadata_rows = format_metadata_rows(metadata)

    return fig, style, metadata_rows, project_id, project_name


def make_api_call(json_payload, endpoint, requests_type="POST"):
    try:
        if requests_type == "POST":
            response = requests.post(
                f"http://localhost:5000/api/{endpoint}", json=json_payload
            )
        elif requests_type == "DELETE":
            response = requests.delete(
                f"http://localhost:5000/api/{endpoint}", json=json_payload
            )
        else:
            response = requests.get(
                f"http://localhost:5000/api/{endpoint}", json=json_payload
            )

        response.raise_for_status()
        return response, None

    except requests.exceptions.RequestException as e:
        try:
            return None, response.json().get("error", str(e))
        except Exception:
            return None, str(e)


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


def get_log_data_directory_options():
    labels, values = get_all_root_log_directories()
    return [{"label": lab, "value": val} for (lab, val) in zip(labels, values)]


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


def _parse_response_as_table(response):
    df = pl.read_parquet(io.BytesIO(response.content))
    columns = [{"name": col, "id": col} for col in df.columns]
    return df.to_dicts(), columns

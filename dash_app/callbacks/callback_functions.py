import dash
import requests
import io
import polars as pl
from dash_app.utils.data_directories import get_runs, get_all_filenames
from dash_app.utils.plots import (
    create_unique_term_count_plot,
    create_files_count_plot,
    create_umap_plot,
    create_unique_term_count_plot_by_file,
)


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


def populate_train_test_table(
    n_clicks,
    log_format,
    train_data,
    test_data,
    detectors,
    enhancement,
    include_items,
    mask_type,
    level="run",
):
    if n_clicks == 0:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    json_payload = _build_test_train_payload(
        train_data,
        test_data,
        log_format,
        detectors,
        enhancement,
        include_items,
        mask_type,
        level,
    )

    response, error = _make_api_call(json_payload, "manual-test-train")
    if error:
        return (
            dash.no_update,
            dash.no_update,
            error,
            True,
            dash.no_update,
            False,
        )

    df_dict, columns = _parse_response_as_table(response)

    return (
        df_dict,
        columns,
        "",
        False,
        "Analysis complete.",
        True,
    )


def _build_test_train_payload(
    train_data,
    test_data,
    log_format,
    detectors,
    enhancement,
    include_items,
    mask_type,
    level="run",
):
    payload = {
        "train_data_path": train_data,
        "test_data_path": test_data,
        "log_format": log_format,
        "models": detectors,
        "item_list_col": enhancement,
        "mask_type": mask_type,
    }

    if level == "run":
        payload["runs_to_include"] = include_items
        payload["run_level"] = True
    elif level == "file":
        payload["files_to_include"] = include_items
        payload["file_level"] = True
    else:
        raise ValueError("Level must be either 'file' or 'run'")

    return payload


def populate_distance_table(
    n_clicks,
    directory_path,
    target_run,
    comparision_runs,
    enhancement,
    mask_type=None,
    level="run",
):
    if n_clicks == 0:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    payload = {
        "dir_path": directory_path,
        "target_run": target_run,
        "comparison_runs": comparision_runs,
        "item_list_col": enhancement,
        "mask_type": mask_type,
        "file_level": (level == "file"),
    }
    response, error = _make_api_call(payload, "run-distance")
    if error:
        return (
            dash.no_update,
            dash.no_update,
            error,
            True,
            dash.no_update,
            False,
        )

    df_dict, columns = _parse_response_as_table(response)
    return (
        df_dict,
        columns,
        "",
        False,
        "Analysis complete.",
        True,
    )


def _make_api_call(json_payload, endpoint):
    try:
        response = requests.post(
            f"http://localhost:5000/api/{endpoint}", json=json_payload
        )
        response.raise_for_status()
        return response, None

    except requests.exceptions.RequestException as e:
        try:
            return None, response.json().get("error", str(e))
        except Exception:
            return None, str(e)


def _parse_response_as_table(response):
    df = pl.read_parquet(io.BytesIO(response.content))
    columns = [{"name": col, "id": col} for col in df.columns]
    return df.to_dicts(), columns


def create_high_level_plot(n_clicks, switch_on, directory_path, plot_type, level="run"):
    if n_clicks == 0:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    endpoint_map = {
        "files": "run-file-counts",
        "umap": "umap",
        "terms": "run-unique-terms",
    }

    endpoint = endpoint_map.get(plot_type, "run-unique-terms")
    payload = {"dir_path": directory_path, "file_level": (level == "file")}

    response, error = _make_api_call(payload, endpoint)
    if error:
        return (
            dash.no_update,
            dash.no_update,
            error,
            True,
            dash.no_update,
            False,
        )

    df = pl.read_parquet(io.BytesIO(response.content))  # type: ignore

    theme = "plotly_white" if switch_on else "plotly_dark"
    style = {
        "resize": "both",
        "overflow": "auto",
        "minHeight": "500px",
        "minWidth": "600px",
        "width": "90%",
    }

    if plot_type == "files":
        fig = create_files_count_plot(df, theme)
    elif plot_type == "umap":
        group_col = "run" if level == "run" else "seq_id"
        fig = create_umap_plot(df, group_col, theme)
    else:
        if level == "file":
            fig = create_unique_term_count_plot_by_file(df, theme)
        else:
            fig = create_unique_term_count_plot(df, theme)

    return (
        fig,
        style,
        "",
        False,
        "Analysis complete.",
        True,
    )

import dash
import requests
import io
import polars as pl
from dash_app.utils.data_directories import get_runs, get_all_filenames


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


def populate_table(
    n_clicks,
    log_format,
    train_data,
    test_data,
    detectors,
    enhancement,
    include_items,
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

    try:
        json_payload = _build_test_train_payload(
            train_data,
            test_data,
            log_format,
            detectors,
            enhancement,
            include_items,
            level,
        )
        response = requests.post(
            "http://localhost:5000/api/manual-test-train", json=json_payload
        )
        response.raise_for_status()

        df = pl.read_parquet(io.BytesIO(response.content))
        columns = [{"name": col, "id": col} for col in df.columns]

        return (
            df.to_dicts(),
            columns,
            "",
            False,
            "Analysis complete.",
            True,
        )

    except requests.exceptions.RequestException as e:
        try:
            error_message = response.json().get("error", str(e))
        except Exception:
            error_message = str(e)

        return (
            dash.no_update,
            dash.no_update,
            error_message,
            True,
            dash.no_update,
            False,
        )


def _build_test_train_payload(
    train_data,
    test_data,
    log_format,
    detectors,
    enhancement,
    include_items,
    level="run",
):
    payload = {
        "train_data_path": train_data,
        "test_data_path": test_data,
        "log_format": log_format,
        "models": detectors,
        "item_list_col": enhancement,
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

import dash
import polars as pl
import requests
from dash import Input, Output, State, callback
import io
from dash_app.components.forms import test_train_file_level_form
from dash_app.components.layouts import create_ano_run_level_layout

from dash_app.callbacks.callback_functions import get_filter_options

dash.register_page(
    __name__, path="/ano-file-level", title="File Level Anomaly Detection"
)

form = test_train_file_level_form(
    "submit_fl",
    "log_format_fl",
    "train_data_fl",
    "test_data_fl",
    "detectors_fl",
    "enhancement_fl",
    "files_filter_fl",
)
layout = create_ano_run_level_layout(
    form,
    "error_toast_fl",
    "success_toast_fl",
    "data_table_fl",
)


@callback(
    Output("files_filter_fl", "options"),
    Input("test_data_fl", "value"),
)
def get_file_options(test_data_path):
    return get_filter_options(test_data_path, runs_or_files="files")


@callback(
    Output("data_table_fl", "data"),
    Output("data_table_fl", "columns"),
    Output("error_toast_fl", "children"),
    Output("error_toast_fl", "is_open"),
    Output("success_toast_fl", "children"),
    Output("success_toast_fl", "is_open"),
    Input("submit_fl", "n_clicks"),
    State("log_format_fl", "value"),
    State("train_data_fl", "value"),
    State("test_data_fl", "value"),
    State("detectors_fl", "value"),
    State("enhancement_fl", "value"),
    State("files_filter_fl", "value"),
    prevent_initial_call=True,
)
def populate_table(
    n_clicks,
    log_format,
    train_data,
    test_data,
    detectors,
    enhancement,
    files_to_include,
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
        response = requests.post(
            "http://localhost:5000/api/manual-test-train",
            json={
                "train_data_path": train_data,
                "test_data_path": test_data,
                "log_format": log_format,
                "models": detectors,
                "item_list_col": enhancement,
                "seq": False,
                "files_to_include": files_to_include,
                "file_level": True,
            },
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

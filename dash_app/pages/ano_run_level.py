import dash
import polars as pl
import requests
from dash import Input, Output, State, callback
import io
from dash_app.components.forms import test_train_form
from dash_app.components.layouts import create_ano_run_level_layout

from dash_app.utils.data_directories import get_runs

dash.register_page(__name__, path="/ano-run-level", title="Run Level Anomaly Detection")

form = test_train_form(
    "submit_rl",
    "log_format_rl",
    "train_data_rl",
    "test_data_rl",
    "detectors_rl",
    "enhancement_rl",
    "runs_filter_rl",
)
layout = create_ano_run_level_layout(
    form,
    "error_toast_rl",
    "success_toast_rl",
    "data_table_rl",
)


@callback(
    Output("runs_filter_rl", "options"),
    Input("test_data_rl", "value"),
)
def get_filter_options(test_data_path):
    if test_data_path is None:
        return {}

    runs = get_runs(test_data_path)

    options = [{"label": run, "value": run} for run in runs]
    return options


@callback(
    Output("data_table_rl", "data"),
    Output("data_table_rl", "columns"),
    Output("error_toast_rl", "children"),
    Output("error_toast_rl", "is_open"),
    Output("success_toast_rl", "children"),
    Output("success_toast_rl", "is_open"),
    Input("submit_rl", "n_clicks"),
    State("log_format_rl", "value"),
    State("train_data_rl", "value"),
    State("test_data_rl", "value"),
    State("detectors_rl", "value"),
    State("enhancement_rl", "value"),
    State("runs_filter_rl", "value"),
    prevent_initial_call=True,
)
def populate_table(
    n_clicks,
    log_format,
    train_data,
    test_data,
    detectors,
    enhancement,
    runs_to_include,
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
                "runs_to_include": runs_to_include,
                "run_level": True,
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

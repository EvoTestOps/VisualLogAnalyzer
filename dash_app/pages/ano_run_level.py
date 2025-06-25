import dash
from dash import Input, Output, State, callback
from dash_app.components.forms import test_train_form
from dash_app.components.layouts import create_ano_run_level_layout

from dash_app.callbacks.callback_functions import (
    get_filter_options,
    populate_train_test_table,
)

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
def get_run_options(test_data_path):
    return get_filter_options(test_data_path, runs_or_files="runs")


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
def populate_run_table(
    n_clicks,
    log_format,
    train_data,
    test_data,
    detectors,
    enhancement,
    runs_to_include,
):
    return populate_train_test_table(
        n_clicks,
        log_format,
        train_data,
        test_data,
        detectors,
        enhancement,
        runs_to_include,
        level="run",
    )

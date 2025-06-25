import dash
from dash import Input, Output, State, callback
from dash_app.components.forms import test_train_file_level_form
from dash_app.components.layouts import create_ano_run_level_layout
from dash_app.callbacks.callback_functions import (
    get_filter_options,
    populate_train_test_table,
)

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
def populate_file_table(
    n_clicks,
    log_format,
    train_data,
    test_data,
    detectors,
    enhancement,
    files_to_include,
):
    return populate_train_test_table(
        n_clicks,
        log_format,
        train_data,
        test_data,
        detectors,
        enhancement,
        files_to_include,
        level="file",
    )

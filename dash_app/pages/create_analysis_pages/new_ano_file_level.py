import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html

from dash_app.callbacks.callback_functions import (
    run_anomaly_detection,
    get_filter_options,
    get_log_data_directory_options,
)
from dash_app.components.forms import test_train_file_level_form
from dash_app.components.toasts import error_toast, success_toast
from dash_app.utils.metadata import parse_query_parameter

dash.register_page(
    __name__,
    path="/analysis/ano-file-level/create",
    title="New File Level Anomaly Detection",
)


def layout(**kwargs):
    form = test_train_file_level_form(
        "submit-ano-file",
        "log-format-ano-file",
        "train-data-ano-file",
        "test-data-ano-file",
        "detectors-ano-file",
        "enhancement-ano-file",
        "filter-ano-file",
        "mask-ano-file",
        "vectorizer-ano-file",
    )

    return [
        dbc.Container(
            [
                html.H3("New File Level Anomaly Detection"),
                error_toast("error-toast-ano-file"),
                success_toast("success-toast-ano-file"),
                dcc.Location(id="url", refresh=False),
                dcc.Store(id="project-id-ano-file"),
            ]
        ),
        dbc.Container(
            [
                form,
                dcc.Loading(dcc.Location(id="redirect-ano-file", refresh=True)),
            ]
        ),
    ]


@callback(
    Output("project-id-ano-file", "data"),
    Output("error-toast-ano-file", "children"),
    Output("error-toast-ano-file", "is_open"),
    Input("url", "search"),
)
def get_project_id(search):
    id = parse_query_parameter(search, "project_id")
    if not id:
        return None, "No project id provided. The analysis will fail.", True

    return id, dash.no_update, False


@callback(
    Output("train-data-ano-file", "options"),
    Output("test-data-ano-file", "options"),
    Input("url", "search"),
)
def get_log_data_directories(_):
    options = get_log_data_directory_options()
    return options, options


@callback(
    Output("filter-ano-file", "options"),
    Input("test-data-ano-file", "value"),
)
def get_comparison_options(directory_path):
    options = get_filter_options(directory_path, runs_or_files="files")
    return options


@callback(
    Output("redirect-ano-file", "href"),
    Output("error-toast-ano-file", "children", allow_duplicate=True),
    Output("error-toast-ano-file", "is_open", allow_duplicate=True),
    Output("success-toast-ano-file", "children"),
    Output("success-toast-ano-file", "is_open"),
    Input("submit-ano-file", "n_clicks"),
    State("project-id-ano-file", "data"),
    State("log-format-ano-file", "value"),
    State("train-data-ano-file", "value"),
    State("test-data-ano-file", "value"),
    State("detectors-ano-file", "value"),
    State("enhancement-ano-file", "value"),
    State("filter-ano-file", "value"),
    State("mask-ano-file", "value"),
    State("vectorizer-ano-file", "value"),
    prevent_initial_call=True,
)
def run_analysis(
    n_clicks,
    project_id,
    log_format,
    train_data,
    test_data,
    detectors,
    enhancement,
    filter,
    mask_type,
    vectorizer_type,
):

    try:
        result = run_anomaly_detection(
            project_id,
            train_data,
            test_data,
            detectors,
            enhancement,
            filter,
            mask_type,
            vectorizer_type,
            log_format,
            level="file",
        )

        return (
            f"/dash/analysis/{result['type']}/{result['id']}",
            dash.no_update,
            False,
            "Analysis complete",
            True,
        )
    except ValueError as e:
        return (
            dash.no_update,
            str(e),
            True,
            dash.no_update,
            False,
        )

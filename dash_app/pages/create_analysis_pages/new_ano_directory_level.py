import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html

from dash_app.callbacks.callback_functions import (
    get_filter_options,
    run_anomaly_detection,
    get_log_data_directory_options,
)
from dash_app.components.forms import test_train_form
from dash_app.components.toasts import error_toast, success_toast
from dash_app.utils.metadata import parse_query_parameter

dash.register_page(
    __name__,
    path="/analysis/ano-directory-level/create",
    title="New Directory Level Anomaly Detection",
)


def layout(**kwargs):
    form = test_train_form(
        "submit-ano-dir",
        "train-data-ano-dir",
        "test-data-ano-dir",
        "detectors-ano-dir",
        "enhancement-ano-dir",
        "filter-ano-dir",
        "mask-ano-dir",
        "vectorizer-ano-dir",
    )

    return [
        dbc.Container(
            [
                html.H3("New Directory Level Anomaly Detection"),
                error_toast("error-toast-ano-dir"),
                success_toast("success-toast-ano-dir"),
                dcc.Location(id="url", refresh=False),
                dcc.Store(id="project-id-ano-dir"),
            ]
        ),
        dbc.Container(
            [
                form,
                dcc.Loading(dcc.Location(id="redirect-ano-dir", refresh=True)),
            ]
        ),
    ]


@callback(
    Output("project-id-ano-dir", "data"),
    Output("error-toast-ano-dir", "children"),
    Output("error-toast-ano-dir", "is_open"),
    Input("url", "search"),
)
def get_project_id(search):
    id = parse_query_parameter(search, "project_id")
    if not id:
        return None, "No project id provided. The analysis will fail.", True

    return id, dash.no_update, False


@callback(
    Output("train-data-ano-dir", "options"),
    Output("test-data-ano-dir", "options"),
    Input("url", "search"),
)
def get_log_data_directories(_):
    options = get_log_data_directory_options()
    return options, options


@callback(
    Output("filter-ano-dir", "options"),
    Input("test-data-ano-dir", "value"),
)
def get_comparison_options(directory_path):
    options = get_filter_options(directory_path, runs_or_files="runs")
    return options


@callback(
    Output("redirect-ano-dir", "href"),
    Output("error-toast-ano-dir", "children", allow_duplicate=True),
    Output("error-toast-ano-dir", "is_open", allow_duplicate=True),
    Output("success-toast-ano-dir", "children"),
    Output("success-toast-ano-dir", "is_open"),
    Input("submit-ano-dir", "n_clicks"),
    State("project-id-ano-dir", "data"),
    State("train-data-ano-dir", "value"),
    State("test-data-ano-dir", "value"),
    State("detectors-ano-dir", "value"),
    State("enhancement-ano-dir", "value"),
    State("filter-ano-dir", "value"),
    State("mask-ano-dir", "value"),
    State("vectorizer-ano-dir", "value"),
    prevent_initial_call=True,
)
def run_analysis(
    n_clicks,
    project_id,
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
            "raw",
            level="directory",
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

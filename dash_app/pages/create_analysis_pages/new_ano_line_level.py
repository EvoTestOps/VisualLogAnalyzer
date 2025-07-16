import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html

from dash_app.callbacks.callback_functions import (
    run_anomaly_detection,
    get_filter_options,
    get_log_data_directory_options,
)
from dash_app.components.forms import test_train_form
from dash_app.components.toasts import error_toast, success_toast
from dash_app.utils.metadata import parse_query_parameter

dash.register_page(
    __name__,
    path="/analysis/ano-line-level/create",
    title="New Line Level Anomaly Detection",
)


def layout(**kwargs):
    form = test_train_form(
        "submit-ano-line",
        "train-data-ano-line",
        "test-data-ano-line",
        "detectors-ano-line",
        "enhancement-ano-line",
        "filter-ano-line",
        "mask-ano-line",
        "vectorizer-ano-line",
    )

    return [
        dbc.Container(
            [
                html.H3("New Line Level Anomaly Detection"),
                error_toast("error-toast-ano-line"),
                success_toast("success-toast-ano-line"),
                dcc.Location(id="url", refresh=False),
                dcc.Store(id="project-id-ano-line"),
            ]
        ),
        dbc.Container(
            [
                form,
                dcc.Loading(dcc.Location(id="redirect-ano-line", refresh=True)),
            ]
        ),
    ]


@callback(
    Output("project-id-ano-line", "data"),
    Output("error-toast-ano-line", "children"),
    Output("error-toast-ano-line", "is_open"),
    Input("url", "search"),
)
def get_project_id(search):
    id = parse_query_parameter(search, "project_id")
    if not id:
        return None, "No project id provided. The analysis will fail.", True

    return id, dash.no_update, False


@callback(
    Output("train-data-ano-line", "options"),
    Output("test-data-ano-line", "options"),
    Input("url", "search"),
)
def get_log_data_directories(_):
    options = get_log_data_directory_options()
    return options, options


@callback(
    Output("filter-ano-line", "options"),
    Input("test-data-ano-line", "value"),
)
def get_comparison_options(directory_path):
    options = get_filter_options(directory_path, runs_or_files="runs")
    return options


@callback(
    Output("error-toast-ano-line", "children", allow_duplicate=True),
    Output("error-toast-ano-line", "is_open", allow_duplicate=True),
    Output("success-toast-ano-line", "children"),
    Output("success-toast-ano-line", "is_open"),
    Output("redirect-ano-line", "href"),
    Input("submit-ano-line", "n_clicks"),
    State("project-id-ano-line", "data"),
    State("train-data-ano-line", "value"),
    State("test-data-ano-line", "value"),
    State("detectors-ano-line", "value"),
    State("enhancement-ano-line", "value"),
    State("filter-ano-line", "value"),
    State("mask-ano-line", "value"),
    State("vectorizer-ano-line", "value"),
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
            level="line",
        )

        return (
            dash.no_update,
            False,
            "Analysis complete",
            True,
            f"/dash/project/{project_id}?task_id={result.get('task_id')}",
        )
    except ValueError as e:
        return (
            str(e),
            True,
            dash.no_update,
            False,
            dash.no_update,
        )

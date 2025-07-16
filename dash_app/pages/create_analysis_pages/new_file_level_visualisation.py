import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html

from dash_app.callbacks.callback_functions import (
    run_high_level_analysis,
    get_log_data_directory_options,
)
from dash_app.components.forms import file_level_viz_form
from dash_app.components.toasts import error_toast, success_toast
from dash_app.utils.metadata import parse_query_parameter

dash.register_page(
    __name__,
    path="/analysis/file-level-visualisations/create",
    title="New File Level Visualisation",
)


def layout(**kwargs):
    form = file_level_viz_form(
        "submit-file",
        "directory-file",
        "analysis-type-file",
        "mask-file",
        "vectorizer-file",
    )

    return [
        dbc.Container(
            [
                html.H3("New File Level Visualisation"),
                error_toast("error-toast-file"),
                success_toast("success-toast-file"),
                dcc.Location(id="url", refresh=False),
                dcc.Store(id="project-id-file"),
            ]
        ),
        dbc.Container(
            [
                form,
                dcc.Loading(dcc.Location(id="redirect-file", refresh=True)),
            ]
        ),
    ]


@callback(
    Output("project-id-file", "data"),
    Output("error-toast-file", "children"),
    Output("error-toast-file", "is_open"),
    Input("url", "search"),
)
def get_project_id(search):
    id = parse_query_parameter(search, "project_id")
    if not id:
        return None, "No project id provided. The analysis will fail.", True

    return id, dash.no_update, False


@callback(
    Output("directory-file", "options"),
    Input("url", "search"),
)
def get_log_data_directories(_):
    return get_log_data_directory_options()


@callback(
    Output("error-toast-file", "children", allow_duplicate=True),
    Output("error-toast-file", "is_open", allow_duplicate=True),
    Output("success-toast-file", "children"),
    Output("success-toast-file", "is_open"),
    Output("redirect-file", "href"),
    Input("submit-file", "n_clicks"),
    State("project-id-file", "data"),
    State("directory-file", "value"),
    State("analysis-type-file", "value"),
    State("mask-file", "value"),
    State("vectorizer-file", "value"),
    prevent_initial_call=True,
)
def run_analysis(
    n_clicks, project_id, directory_path, analysis_type, mask_type, vectorizer_type
):
    try:
        result = run_high_level_analysis(
            project_id,
            directory_path,
            analysis_type,
            mask_type,
            vectorizer_type,
            level="file",
        )
        return (
            dash.no_update,
            False,
            "Analysis is running",
            True,
            f"/dash/project/{project_id}?task_id={result.get("task_id")}",
        )
    except ValueError as e:
        return (
            str(e),
            True,
            dash.no_update,
            False,
            dash.no_update,
        )

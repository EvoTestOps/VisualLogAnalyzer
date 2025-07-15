import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html

from dash_app.callbacks.callback_functions import (
    run_high_level_analysis,
    get_log_data_directory_options,
)
from dash_app.components.forms import directory_level_viz_form
from dash_app.components.toasts import error_toast, success_toast
from dash_app.utils.metadata import parse_query_parameter

dash.register_page(
    __name__,
    path="/analysis/directory-level-visualisations/create",
    title="New Directory Level Visualisation",
)


def layout(**kwargs):
    form = directory_level_viz_form(
        "submit-ut", "directory-ut", "analysis-type-ut", "mask-ut", "vectorizer-ut"
    )

    return [
        dbc.Container(
            [
                html.H3("New Directory Level Visualisation"),
                error_toast("error-toast-ut"),
                success_toast("success-toast-ut"),
                dcc.Location(id="url", refresh=False),
                dcc.Store(id="project-id-ut"),
            ]
        ),
        dbc.Container(
            [
                form,
                dcc.Loading(dcc.Location(id="redirect-ut", refresh=True)),
            ]
        ),
    ]


@callback(
    Output("project-id-ut", "data"),
    Output("error-toast-ut", "children"),
    Output("error-toast-ut", "is_open"),
    Input("url", "search"),
)
def get_project_id(search):
    id = parse_query_parameter(search, "project_id")
    if not id:
        return None, "No project id provided. The analysis will fail.", True

    return id, dash.no_update, False


@callback(
    Output("directory-ut", "options"),
    Input("url", "search"),
)
def get_log_data_directories(_):
    return get_log_data_directory_options()


@callback(
    Output("error-toast-ut", "children", allow_duplicate=True),
    Output("error-toast-ut", "is_open", allow_duplicate=True),
    Output("success-toast-ut", "children", allow_duplicate=True),
    Output("success-toast-ut", "is_open", allow_duplicate=True),
    Output("redirect-ut", "href"),
    Input("submit-ut", "n_clicks"),
    State("project-id-ut", "data"),
    State("directory-ut", "value"),
    State("analysis-type-ut", "value"),
    State("mask-ut", "value"),
    State("vectorizer-ut", "value"),
    prevent_initial_call=True,
)
def run_analysis(
    _, project_id, directory_path, analysis_type, mask_type, vectorizer_type
):
    try:
        result = run_high_level_analysis(
            project_id,
            directory_path,
            analysis_type,
            mask_type,
            vectorizer_type,
            level="directory",
        )
        return (
            dash.no_update,
            False,
            f"Analysis is running: {result}",
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

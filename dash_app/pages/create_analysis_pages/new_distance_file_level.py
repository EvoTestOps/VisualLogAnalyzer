import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html

from dash_app.callbacks.callback_functions import (
    run_log_distance,
    get_filter_options,
    get_log_data_directory_options,
)
from dash_app.components.forms import distance_file_level_form
from dash_app.components.toasts import error_toast, success_toast
from dash_app.utils.metadata import parse_query_parameter

dash.register_page(
    __name__,
    path="/analysis/distance-file-level/create",
    title="New File Level Log Distance",
)


def layout(**kwargs):
    form = distance_file_level_form(
        "submit-dis-file",
        "directory-dis-file",
        "enhancement-dis-file",
        "target-dis-file",
        "filter-dis-file",
        "mask-dis-file",
        "vectorizer-dis-file",
    )

    return [
        dbc.Container(
            [
                html.H3("New File Level Log Distance"),
                error_toast("error-toast-dis-file"),
                success_toast("success-toast-dis-file"),
                dcc.Location(id="url", refresh=False),
                dcc.Store(id="project-id-dis-file"),
            ]
        ),
        dbc.Container(
            [
                form,
                dcc.Loading(dcc.Location(id="redirect-dis-file", refresh=True)),
            ]
        ),
    ]


@callback(
    Output("project-id-dis-file", "data"),
    Output("error-toast-dis-file", "children"),
    Output("error-toast-dis-file", "is_open"),
    Input("url", "search"),
)
def get_project_id(search):
    id = parse_query_parameter(search, "project_id")
    if not id:
        return None, "No project id provided. The analysis will fail.", True

    return id, dash.no_update, False


@callback(
    Output("directory-dis-file", "options"),
    Input("url", "search"),
)
def get_log_data_directories(_):
    return get_log_data_directory_options()


@callback(
    Output("filter-dis-file", "options"),
    Output("target-dis-file", "options"),
    Input("directory-dis-file", "value"),
)
def get_comparison_and_target_options(directory_path):
    options = get_filter_options(directory_path, runs_or_files="files")
    return options, options


@callback(
    Output("error-toast-dis-file", "children", allow_duplicate=True),
    Output("error-toast-dis-file", "is_open", allow_duplicate=True),
    Output("success-toast-dis-file", "children"),
    Output("success-toast-dis-file", "is_open"),
    Output("redirect-dis-file", "href"),
    Input("submit-dis-file", "n_clicks"),
    State("project-id-dis-file", "data"),
    State("directory-dis-file", "value"),
    State("target-dis-file", "value"),
    State("filter-dis-file", "value"),
    State("enhancement-dis-file", "value"),
    State("mask-dis-file", "value"),
    State("vectorizer-dis-file", "value"),
    prevent_initial_call=True,
)
def run_analysis(
    n_clicks,
    project_id,
    directory_path,
    target,
    comparison_runs,
    enhancement,
    mask_type,
    vectorizer_type,
):

    try:
        result = run_log_distance(
            project_id,
            directory_path,
            target,
            comparison_runs,
            enhancement,
            vectorizer_type,
            mask_type,
            level="file",
        )

        return (
            dash.no_update,
            False,
            "Analysis is running",
            True,
            f"/dash/project/{project_id}?task_id={result.get('task_id')}",
        )
    except ValueError as e:
        return (
            dash.no_update,
            str(e),
            True,
            dash.no_update,
            False,
            dash.no_update,
        )

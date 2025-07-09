import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html

from dash_app.callbacks.callback_functions import (
    run_log_distance,
    get_filter_options,
    get_log_data_directory_options,
)
from dash_app.components.forms import distance_run_level_form
from dash_app.components.toasts import error_toast, success_toast
from dash_app.utils.metadata import parse_query_parameter


dash.register_page(
    __name__,
    path="/analysis/distance-directory-level/create",
    title="New Directory Level Log Distance",
)


def layout(**kwargs):
    form = distance_run_level_form(
        "submit-dis",
        "directory-dis",
        "enhancement-dis",
        "target-dis",
        "filter-dis",
        "mask-dis",
        "vectorizer-dis",
    )

    return [
        dbc.Container(
            [
                html.H3("New Directory Level Log Distance"),
                error_toast("error-toast-dis"),
                success_toast("success-toast-dis"),
                dcc.Location(id="url", refresh=False),
                dcc.Store(id="project-id-dis"),
            ]
        ),
        dbc.Container(
            [
                form,
                dcc.Loading(dcc.Location(id="redirect-dis", refresh=True)),
            ]
        ),
    ]


@callback(
    Output("project-id-dis", "data"),
    Output("error-toast-dis", "children"),
    Output("error-toast-dis", "is_open"),
    Input("url", "search"),
)
def get_project_id(search):
    id = parse_query_parameter(search, "project_id")
    if not id:
        return None, "No project id provided. The analysis will fail.", True

    return id, dash.no_update, False


# Input does not matter we just want it to calll once on startup
@callback(
    Output("directory-dis", "options"),
    Input("url", "search"),
)
def get_log_data_directories(_):
    return get_log_data_directory_options()


@callback(
    Output("filter-dis", "options"),
    Output("target-dis", "options"),
    Input("directory-dis", "value"),
)
def get_comparison_and_target_options(directory_path):
    options = get_filter_options(directory_path, runs_or_files="runs")
    return options, options


@callback(
    Output("redirect-dis", "href"),
    Output("error-toast-dis", "children", allow_duplicate=True),
    Output("error-toast-dis", "is_open", allow_duplicate=True),
    Output("success-toast-dis", "children"),
    Output("success-toast-dis", "is_open"),
    Input("submit-dis", "n_clicks"),
    State("project-id-dis", "data"),
    State("directory-dis", "value"),
    State("target-dis", "value"),
    State("filter-dis", "value"),
    State("enhancement-dis", "value"),
    State("mask-dis", "value"),
    State("vectorizer-dis", "value"),
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

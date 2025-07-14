import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html, no_update

from dash_app.callbacks.callback_functions import (
    make_api_call,
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
                dcc.Store(id="job-store-ut"),
                dcc.Interval(id="interval-ut", disabled=True),
            ]
        ),
        dbc.Container(
            [
                form,
                # dcc.Loading(dcc.Location(id="redirect-ut", refresh=True)),
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


# We call the backend to run the analysis which returns task_id.
# In general it should not return an error, except on bad user inputs
#  but even those should be rare, since the data inputs are dropdowns.
# After the task_id has been returned we set the dcc.interval disabled to
#  false, which will start polling the task-status endpoint. When task status
#  is ready it will either return a result or an error.
@callback(
    Output("error-toast-ut", "children", allow_duplicate=True),
    Output("error-toast-ut", "is_open", allow_duplicate=True),
    Output("success-toast-ut", "children", allow_duplicate=True),
    Output("success-toast-ut", "is_open", allow_duplicate=True),
    Output("job-store-ut", "data"),
    Output("interval-ut", "disabled", allow_duplicate=True),
    Input("submit-ut", "n_clicks"),
    State("project-id-ut", "data"),
    State("directory-ut", "value"),
    State("analysis-type-ut", "value"),
    State("mask-ut", "value"),
    State("vectorizer-ut", "value"),
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
            level="directory",
        )
        return (
            dash.no_update,
            False,
            f"Analysis is running: {result}",
            True,
            result.get("task_id"),
            False,
        )
    except ValueError as e:
        return (
            str(e),
            True,
            dash.no_update,
            False,
            dash.no_update,
            True,
        )


@callback(
    Output("error-toast-ut", "children", allow_duplicate=True),
    Output("error-toast-ut", "is_open", allow_duplicate=True),
    Output("success-toast-ut", "children", allow_duplicate=True),
    Output("success-toast-ut", "is_open", allow_duplicate=True),
    Output("interval-ut", "disabled", allow_duplicate=True),
    Input("interval-ut", "n_intervals"),
    State("job-store-ut", "data"),
    prevent_initial_call=True,
)
def poll_result(_, task_id):
    if not task_id:
        return (
            dash.no_update,
            False,
            dash.no_update,
            False,
            dash.no_update,
        )

    # There shouldn't be any error here unless the task_id is wrong.
    response, error = make_api_call({}, f"task-status/{task_id}", requests_type="GET")
    if error or response is None:
        return (
            str(error),
            True,
            dash.no_update,
            False,
            True,
        )

    # f"/dash/analysis/{result['type']}/{result['id']}",
    result = response.json()
    if result.get("ready") is True:
        if result.get("successful") is True:
            return (
                dash.no_update,
                dash.no_update,
                str(result),
                True,
                True,
            )
        else:
            return (
                str(result),
                True,
                dash.no_update,
                False,
                True,
            )
    else:
        # The task is not ready yet.
        return (
            dash.no_update,
            False,
            dash.no_update,
            False,
            dash.no_update,
        )

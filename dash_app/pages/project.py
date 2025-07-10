import dash
import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, callback, dcc

from dash_app.callbacks.callback_functions import make_api_call
from dash_app.components.layouts import create_project_layout
from dash_app.utils.metadata import format_analysis_overview, parse_query_parameter

dash.register_page(__name__, path_template="/project/<project_id>")


def layout(project_id=None, **kwargs):
    return [
        dbc.Container(
            [
                dcc.Store(id="project-id", data=project_id),
                dcc.Location(id="url", refresh=False),
                dcc.ConfirmDialog(
                    id="confirm-delete",
                    message="Are you sure you want to delete this analysis. All data related to this analysis will be lost.",
                ),
                dcc.Store(id="delete-analysis-id"),
            ]
        ),
    ] + create_project_layout(
        "group-project",
        "project-name",
        project_id,
        "nav-home",
        "error-toast-project",
        "success-toast-project",
    )


@callback(
    Output("project-name", "children"),
    Input("url", "search"),
)
def get_project_name(search):
    name = parse_query_parameter(search, "project_name")

    return name if name else ""


@callback(
    Output("group-project", "children"),
    Output("error-toast-project", "children"),
    Output("error-toast-project", "is_open"),
    Output("success-toast-project", "children"),
    Output("success-toast-project", "is_open"),
    Input("project-id", "data"),
)
def get_projects(project_id):
    if not project_id:
        return ([], "No project id was provided", True, dash.no_update, False)

    response, error = make_api_call({}, f"projects/{project_id}/analyses", "GET")
    if error or not response:
        return (dash.no_update, error, True, dash.no_update, False)

    analyses_data = response.json()

    if analyses_data:
        group_items = format_analysis_overview(analyses_data)
    else:
        group_items = [dbc.ListGroupItem("No analyses found")]

    return (group_items, dash.no_update, dash.no_update, dash.no_update, False)


@callback(
    Output("confirm-delete", "displayed"),
    Output("delete-analysis-id", "data"),
    Input({"type": "delete-button", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def display_alert(n_clicks):
    ctx = dash.callback_context

    # ALL matching n_clicks return a list of delete buttons that were triggered.
    # Since button ids are generated dynamically it will trigger the callback
    #  on the first page open and will return all the buttons in the callback_context.
    # So we need to manually check that non of the buttons were pressed.
    if all([(btn["value"] == 0) for btn in ctx.triggered]):
        return dash.no_update

    return True, ctx.triggered_id["index"]


@callback(
    Output("error-toast-project", "children", allow_duplicate=True),
    Output("error-toast-project", "is_open", allow_duplicate=True),
    Output("success-toast-project", "children", allow_duplicate=True),
    Output("success-toast-project", "is_open", allow_duplicate=True),
    Input("confirm-delete", "submit_n_clicks"),
    State("delete-analysis-id", "data"),
    prevent_initial_call=True,
)
def delete_analysis(submit_n_clicks, analysis_id):
    if not submit_n_clicks or not analysis_id:
        return dash.no_update, False, dash.no_update, False

    response, error = make_api_call({}, f"analyses/{analysis_id}", "DELETE")
    if error or not response:
        return (error, True, dash.no_update, False)

    return (dash.no_update, False, "Analysis deleted", True)

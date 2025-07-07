import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html
from dash_app.callbacks.callback_functions import make_api_call
from dash_app.components.layouts import create_project_layout
from dash_app.utils.metadata import format_analysis_overview

dash.register_page(__name__, path_template="/project/<project_id>")


def layout(project_id=None, **kwargs):
    return [
        dbc.Container(dcc.Store(id="project-id", data=project_id))
    ] + create_project_layout(
        "group-project",
        project_id,
        "nav-home",
        "error-toast-project",
        "success-toast-project",
    )


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

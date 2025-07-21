import dash
import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, callback, dcc

from dash_app.callbacks.callback_functions import make_api_call
from dash_app.components.forms import project_form
from dash_app.components.layouts import create_home_layout
from dash_app.utils.metadata import format_project_overview

dash.register_page(__name__, path="/", title="Home")

form = project_form("submit-proj", "name-proj")

# dcc.store is needed so that we can easily trigger the get_projects callback
# after a new project has been created

layout = [
    dbc.Container(
        [
            dcc.Store(id="refresh-proj", data=False),
            dcc.ConfirmDialog(
                id="confirm-delete-proj",
                message="Are you sure you want to delete this project. All analysis results related to this project will be lost.",
            ),
            dcc.Store(id="delete-analysis-id-proj"),
        ]
    )
] + create_home_layout(
    form,
    "project-group",
    "error-toast-proj",
    "success-toast-proj",
    "collapse-proj",
    "open-btn-proj",
)


@callback(
    Output("project-group", "children"),
    Output("error-toast-proj", "children"),
    Output("error-toast-proj", "is_open"),
    Output("success-toast-proj", "children"),
    Output("success-toast-proj", "is_open"),
    Input("project-group", "id"),
    Input("refresh-proj", "data"),
)
def get_projects(_1, _2):
    response, error = make_api_call({}, "projects", "GET")
    if error or not response:
        return (dash.no_update, error, True, dash.no_update, False)

    project_data = response.json()

    if project_data:
        group_items = format_project_overview(project_data)
    else:
        group_items = [dbc.ListGroupItem("No projects found")]

    return (group_items, dash.no_update, dash.no_update, dash.no_update, False)


@callback(
    Output("collapse-proj", "is_open"),
    Input("open-btn-proj", "n_clicks"),
    State("collapse-proj", "is_open"),
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output("error-toast-proj", "children", allow_duplicate=True),
    Output("error-toast-proj", "is_open", allow_duplicate=True),
    Output("success-toast-proj", "children", allow_duplicate=True),
    Output("success-toast-proj", "is_open", allow_duplicate=True),
    Output("refresh-proj", "data"),
    Input("submit-proj", "n_clicks"),
    State("name-proj", "value"),
    prevent_initial_call=True,
)
def create_project(_, name):
    _, error = make_api_call({"name": name}, "projects")
    if error:
        return (error, True, dash.no_update, False, False)

    return (dash.no_update, False, "Project created", True, True)


@callback(
    Output("confirm-delete-proj", "displayed"),
    Output("delete-analysis-id-proj", "data"),
    Input({"type": "delete-button", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def display_alert(n_clicks):
    if not n_clicks:
        return dash.no_update, dash.no_update

    ctx = dash.callback_context
    if all([(btn["value"] == 0) for btn in ctx.triggered]):
        return dash.no_update

    triggered_button = ctx.triggered_id

    return True, triggered_button["index"] if triggered_button else None


@callback(
    Output("error-toast-proj", "children", allow_duplicate=True),
    Output("error-toast-proj", "is_open", allow_duplicate=True),
    Output("success-toast-proj", "children", allow_duplicate=True),
    Output("success-toast-proj", "is_open", allow_duplicate=True),
    Output("refresh-proj", "data", allow_duplicate=True),
    Input("confirm-delete-proj", "submit_n_clicks"),
    State("delete-analysis-id-proj", "data"),
    prevent_initial_call=True,
)
def delete_project(submit_n_clicks, analysis_id):
    if not submit_n_clicks or not analysis_id:
        return dash.no_update, False, dash.no_update, False

    response, error = make_api_call({}, f"projects/{analysis_id}", "DELETE")
    if error or not response:
        return (error, True, dash.no_update, False, dash.no_update)

    return (dash.no_update, False, "Project deleted", True, "dummy")

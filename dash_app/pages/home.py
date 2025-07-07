import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html
from dash_app.callbacks.callback_functions import make_api_call
from dash_app.components.layouts import create_home_layout
from dash_app.components.forms import project_form

dash.register_page(__name__, path="/", title="Home")

form = project_form("submit-proj", "name-proj")

# dcc.store is needed so that we can easily trigger the get_projects callback
# after a new project has been created

layout = [dbc.Container(dcc.Store(id="refresh-proj", data=False))] + create_home_layout(
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
def get_projects(id, refresh):
    response, error = make_api_call({}, "projects", "GET")
    if error or not response:
        return (dash.no_update, error, True, dash.no_update, False)

    project_data = response.json()

    if project_data:
        # TODO: Change timestamp format
        group_items = [
            dbc.ListGroupItem(
                html.Div(
                    [
                        html.H4(project["name"], className="mb-0"),
                        html.Small(project["time_created"]),
                    ],
                    className="d-flex justify-content-between align-items-center",
                ),
                href=f"/dash/project/{project['id']}",
                class_name="pb-3 pt-3",
            )
            for project in project_data
        ]
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
def create_project(n_clicks, name):
    response, error = make_api_call({"name": name}, "projects")
    if error:
        return (error, True, dash.no_update, False, False)

    return (dash.no_update, False, "Project created", True, True)

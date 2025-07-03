import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html
from dash_app.callbacks.callback_functions import make_api_call
from dash_app.components.layouts import create_project_layout

dash.register_page(__name__, path="/", title="Home")

layout = dbc.Container([html.H1("Projects"), dbc.ListGroup(id="project-group")])

layout = [dbc.Container(html.H3("Projects"))] + create_project_layout(
    "project-group", "error-toast-proj", "success-toast-proj"
)


@callback(
    Output("project-group", "children"),
    Output("error-toast-proj", "children"),
    Output("error-toast-proj", "is_open"),
    Output("success-toast-proj", "children"),
    Output("success-toast-proj", "is_open"),
    Input("project-group", "id"),
)
def get_projects(id):
    response, error = make_api_call({}, "projects", "GET")
    if error:
        return (dash.no_update, error, True, dash.no_update, False)

    project_data = response.json()

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
            href=f"/dash/projects/{project['id']}",
            class_name="pb-3 pt-3",
        )
        for project in project_data
    ]

    return (group_items, dash.no_update, dash.no_update, dash.no_update, False)

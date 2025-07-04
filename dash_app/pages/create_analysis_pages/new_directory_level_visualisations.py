import dash
import dash_bootstrap_components as dbc
from urllib.parse import parse_qs
from dash import Input, Output, State, callback, html, dcc
from dash_app.components.forms import directory_level_viz_form
from dash_app.callbacks.callback_functions import make_api_call
from dash_app.components.toasts import error_toast, success_toast

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
    query = parse_qs(search.lstrip("?"))

    id = query.get("project_id", [None])[0]
    if not id:
        return None, "No project id provided. The analysis will fail.", True

    return id, dash.no_update, False


@callback(
    Output("redirect-ut", "href"),
    Output("error-toast-ut", "children", allow_duplicate=True),
    Output("error-toast-ut", "is_open", allow_duplicate=True),
    Output("success-toast-ut", "children"),
    Output("success-toast-ut", "is_open"),
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
    endpoint_map = {
        "files": "run-file-counts",
        "umap": "umap",
        "terms": "unique-terms",
    }
    endpoint = endpoint_map.get(analysis_type, "unique-terms")
    payload = {
        "dir_path": directory_path,
        "file_level": False,
        "mask_type": mask_type,
        "vectorizer": vectorizer_type,
    }

    response, error = make_api_call(payload, f"{endpoint}/{project_id}")
    if error:
        return (
            dash.no_update,
            error,
            True,
            dash.no_update,
            False,
        )

    results = response.json()

    return (
        f"/dash/analysis/{results['type']}/{results['id']}",
        dash.no_update,
        False,
        dash.no_update,
        True,
    )

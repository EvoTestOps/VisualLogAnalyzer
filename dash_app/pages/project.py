import dash
import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, callback, dcc
from urllib.parse import urlencode, parse_qs

from dash_app.callbacks.callback_functions import make_api_call, poll_task_status
from dash_app.components.layouts import create_project_layout
from dash_app.components.toasts import error_toast, success_toast
from dash_app.utils.metadata import format_analysis_overview, parse_query_parameter
from dash_app.dash_config import DashConfig

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
                dcc.Store(
                    id="project-task-store",
                    storage_type="session",
                ),
                dcc.Interval(
                    id="project-task-poll",
                    interval=DashConfig.POLL_RATE * 1000,
                    disabled=True,
                ),
                error_toast(id="task-error-toast"),
                success_toast(id="task-success-toast"),
            ]
        ),
    ] + create_project_layout(
        "group-project",
        "project-name",
        project_id,
        "nav-home",
        "error-toast-project",
        "success-toast-project",
        "settings-submit-project",
        "match-filenames-project",
        "task-count-project",
    )


# TODO: Fetch from the database. This is a pain to maintain.
@callback(
    Output("project-name", "children"),
    Input("url", "search"),
)
def get_project_name(search):
    name = parse_query_parameter(search, "project_name")

    return name if name else "Name not found"


# 'task_id' is passed as a query parameter, since there doesn't
# seem to be any good way to access project-task-store directly.
@callback(
    Output("project-task-store", "data"),
    Output("project-task-poll", "disabled"),
    Output("url", "search"),
    Input("url", "search"),
    State("project-task-store", "data"),
)
def get_task_id(search, current_tasks):
    query = parse_qs(search.lstrip("?"))
    task_id = query.get("task_id", [None])[0]

    if not task_id:
        return (
            dash.no_update,
            True if not current_tasks else dash.no_update,
            dash.no_update,
        )

    query.pop("task_id", None)
    new_search = "?" + urlencode(query, doseq=True) if query else ""

    updated_tasks = (current_tasks or []) + [task_id]

    return (
        updated_tasks,
        False,
        new_search,
    )


@callback(
    Output("task-count-project", "children"),
    Input("url", "href"),
    Input("url", "search"),
    State("project-task-store", "data"),
)
def update_running_analyses_count(_1, _2, current_tasks):
    task_count = len(current_tasks or [])
    return (
        f"Amount of running analyses: {task_count}"
        if task_count > 0
        else "No analyses running"
    )


# Callback is triggered by 'url' so that we can easily
#  refresh the component without refreshing the whole page.
@callback(
    Output("group-project", "children"),
    Output("error-toast-project", "children"),
    Output("error-toast-project", "is_open"),
    Output("success-toast-project", "children"),
    Output("success-toast-project", "is_open"),
    Input("url", "href"),
    State("project-id", "data"),
)
def get_analyses(_, project_id):
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
    Output("match-filenames-project", "value"),
    Input("project-id", "data"),
)
def get_settings(project_id):
    if not project_id:
        return True
    response, error = make_api_call({}, f"projects/{project_id}/settings", "GET")
    if error or not response:
        return True

    return response.json().get("match_filenames")


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
    Output("url", "href"),
    Input("confirm-delete", "submit_n_clicks"),
    State("delete-analysis-id", "data"),
    State("url", "href"),
    prevent_initial_call=True,
)
def delete_analysis(submit_n_clicks, analysis_id, url_path):
    if not submit_n_clicks or not analysis_id:
        return dash.no_update, False, dash.no_update, False

    response, error = make_api_call({}, f"analyses/{analysis_id}", "DELETE")
    if error or not response:
        return (error, True, dash.no_update, False, dash.no_update)

    return (dash.no_update, False, "Analysis deleted", True, url_path)


@callback(
    Output("error-toast-project", "children", allow_duplicate=True),
    Output("error-toast-project", "is_open", allow_duplicate=True),
    Output("success-toast-project", "children", allow_duplicate=True),
    Output("success-toast-project", "is_open", allow_duplicate=True),
    Input("settings-submit-project", "n_clicks"),
    Input("match-filenames-project", "value"),
    State("project-id", "data"),
    prevent_initial_call=True,
)
def apply_settings(n_clicks, match_filenames, project_id):
    if not n_clicks:
        return dash.no_update, False, dash.no_update, False

    payload = {"match_filenames": match_filenames}
    response, error = make_api_call(
        payload, f"projects/{project_id}/settings", requests_type="PATCH"
    )
    if error or not response:
        return (error, True, dash.no_update, False)

    return (dash.no_update, False, "Settings updated", True)


@callback(
    Output("task-error-toast", "children"),
    Output("task-error-toast", "is_open"),
    Output("task-success-toast", "children"),
    Output("task-success-toast", "is_open"),
    Output("project-task-store", "data", allow_duplicate=True),
    Output("url", "href", allow_duplicate=True),
    Output("project-task-poll", "disabled", allow_duplicate=True),
    Input("project-task-poll", "n_intervals"),
    State("project-task-store", "data"),
    State("url", "href"),
    prevent_initial_call=True,
)
def poll_project_tasks(_, task_ids, url_path):
    updated_task_store = []
    success_messages = []
    error_messages = []

    for task_id in task_ids or []:
        try:
            result = poll_task_status(task_id)
        except ValueError as e:
            error_messages.append(
                f"Unexpected error occured with task id {task_id}: {e}"
            )
            continue

        if result is None or result.get("ready") is False:
            updated_task_store.append(task_id)
        elif result.get("successful"):
            success_messages.append("Analysis complete")
        else:
            error_messages.append(f"Analysis failed: {result.get("result")}")

    # TODO: what if there is both error messages and success messages
    error_output = "\n".join(error_messages) if error_messages else dash.no_update
    error_open = bool(error_messages)
    success_output = "\n".join(success_messages) if success_messages else dash.no_update
    success_open = bool(success_messages)

    should_refresh = bool(success_messages)
    refresh_path = url_path if should_refresh else dash.no_update

    polling_disabled = False if len(updated_task_store) > 0 else True

    return (
        error_output,
        error_open,
        success_output,
        success_open,
        updated_task_store,
        refresh_path,
        polling_disabled,
    )

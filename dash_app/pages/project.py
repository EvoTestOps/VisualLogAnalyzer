from urllib.parse import parse_qs, urlencode
from datetime import datetime, timezone

import dash
import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, callback, dcc, html

from dash_app.callbacks.callback_functions import (
    make_api_call,
    poll_task_status,
    fetch_project_name,
)
from dash_app.components.layouts import create_project_layout
from dash_app.components.toasts import error_toast, success_toast
from dash_app.dash_config import DashConfig
from dash_app.utils.metadata import format_analysis_overview, format_task_overview_row

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
                dcc.Store(id="edit-analysis-id"),
                dcc.Store(
                    id="project-task-store",
                    storage_type="session",
                ),
                dcc.Store(
                    id="task-error-store",
                    storage_type="session",
                    data=[],
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
        "color-by-directory-project",
        "task-info-project",
        "line-display-mode-project",
        "task-error-modal-project",
        "manual-filename-project",
        "clear-recent-project",
        "edit-name-modal",
        "edit-name-input",
        "submit-edit-name",
    )


@callback(
    Output("project-name", "children"),
    Input("project-id", "data"),
)
def get_project_name(project_id):
    return fetch_project_name(project_id)


# 'task_id' is passed as a query parameter, since there doesn't
# seem to be any good way to access project-task-store directly.
@callback(
    Output("project-task-store", "data"),
    Output("project-task-poll", "disabled"),
    Output("url", "search"),
    Input("url", "search"),
    State("project-task-store", "data"),
    State("project-id", "data"),
)
def get_task_id(search, current_tasks, project_id):
    query = parse_qs(search.lstrip("?"))
    task_id = query.get("task_id", [None])[0]

    if not task_id:
        return (
            dash.no_update,
            True if not current_tasks else False,
            dash.no_update,
        )

    query.pop("task_id", None)
    new_search = "?" + urlencode(query, doseq=True) if query else ""

    updated_tasks = (current_tasks or []) + [
        {"id": task_id, "completed_at": None, "project_id": project_id}
    ]

    return (
        updated_tasks,
        False,
        new_search,
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
    Output("color-by-directory-project", "value"),
    Output("line-display-mode-project", "value"),
    Output("manual-filename-project", "value"),
    Input("project-id", "data"),
)
def get_settings(project_id):
    if not project_id:
        return True

    response, error = make_api_call({}, f"projects/{project_id}/settings", "GET")
    if error or not response:
        return True

    settings = response.json()
    return (
        settings.get("match_filenames"),
        settings.get("color_by_directory"),
        settings.get("line_level_display_mode"),
        settings.get("manual_filename_input"),
    )


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
        return dash.no_update, dash.no_update

    if ctx.triggered_id:
        return True, ctx.triggered_id["index"]

    return dash.no_update, dash.no_update


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
    Output("edit-name-modal", "is_open"),
    Output("edit-analysis-id", "data"),
    Input({"type": "edit-button", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def display_edit_modal(n_clicks):
    ctx = dash.callback_context

    if all([(btn["value"] == 0) for btn in ctx.triggered]):
        return dash.no_update, dash.no_update

    if ctx.triggered_id:
        return True, ctx.triggered_id["index"]

    return dash.no_update, dash.no_update


@callback(
    Output("error-toast-project", "children", allow_duplicate=True),
    Output("error-toast-project", "is_open", allow_duplicate=True),
    Output("success-toast-project", "children", allow_duplicate=True),
    Output("success-toast-project", "is_open", allow_duplicate=True),
    Output("edit-name-modal", "is_open", allow_duplicate=True),
    Output("url", "href", allow_duplicate=True),
    Input("submit-edit-name", "n_clicks"),
    State("edit-name-input", "value"),
    State("edit-analysis-id", "data"),
    State("url", "href"),
    prevent_initial_call=True,
)
def edit_analysis_name(submit_n_clicks, new_name, analysis_id, url_path):
    if not submit_n_clicks or not analysis_id:
        return (
            dash.no_update,
            False,
            dash.no_update,
            False,
            dash.no_update,
            dash.no_update,
        )
    if not new_name:
        return (
            "Analysis name cannot be empty",
            True,
            dash.no_update,
            False,
            False,
            dash.no_update,
        )

    response, error = make_api_call(
        {"name": new_name}, f"analyses/{analysis_id}/name", "PATCH"
    )
    if error or not response:
        return (error, True, dash.no_update, False, False, dash.no_update)

    return (dash.no_update, False, "Name changed successfully", True, False, url_path)


@callback(
    Output("error-toast-project", "children", allow_duplicate=True),
    Output("error-toast-project", "is_open", allow_duplicate=True),
    Output("success-toast-project", "children", allow_duplicate=True),
    Output("success-toast-project", "is_open", allow_duplicate=True),
    Input("settings-submit-project", "n_clicks"),
    State("match-filenames-project", "value"),
    State("color-by-directory-project", "value"),
    State("line-display-mode-project", "value"),
    State("manual-filename-project", "value"),
    State("project-id", "data"),
    prevent_initial_call=True,
)
def apply_settings(
    n_clicks,
    match_filenames,
    color_by_directory,
    line_display_mode,
    manual_filename_input,
    project_id,
):
    if not n_clicks:
        return dash.no_update, False, dash.no_update, False

    payload = {
        "match_filenames": match_filenames,
        "color_by_directory": color_by_directory,
        "line_level_display_mode": line_display_mode,
        "manual_filename_input": manual_filename_input,
    }
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
    Output("task-info-project", "children"),
    Output("task-error-store", "data"),
    Input("project-task-poll", "n_intervals"),
    State("project-task-store", "data"),
    State("task-error-store", "data"),
    State("url", "href"),
    State("task-error-toast", "is_open"),
    State("task-success-toast", "is_open"),
    State("project-id", "data"),
    prevent_initial_call=True,
)
def poll_project_tasks(
    _,
    task_store,
    task_error_store,
    url_path,
    current_error_open,
    current_success_open,
    project_id,
):
    time_now = datetime.now(timezone.utc)
    updated_task_store = []
    success_messages, error_messages, task_errors = [], [], []
    task_rows = []

    task_info_header = [
        html.Thead(
            html.Tr(
                [html.Th("Analysis Type"), html.Th("Status"), html.Th("Time Elapsed")]
            )
        )
    ]

    current_project_tasks = [
        t for t in (task_store or []) if t.get("project_id") == project_id
    ]
    for task_entry in task_store or []:
        if task_entry.get("completed_at") or task_entry.get("cleared"):
            updated_task_store.append(task_entry)
            continue

        try:
            task_id = task_entry["id"]
            result = poll_task_status(task_id)

            if result is None:
                updated_task_store.append(task_id)
                continue

            state = result.get("state", "")
            meta = result.get("meta", {})
            task_entry["state"] = state
            task_entry["meta"] = meta
            task_entry["start_time"] = result.get("start_time", None)

            error_result = result.get("result", {})
            error = error_result.get("error", None) if error_result else None

            if not result.get("ready"):
                updated_task_store.append(task_entry)
                continue

            if state == "SUCCESS":
                success_messages.append("Analysis complete")
            elif state == "FAILURE":
                error_messages.append(error)
                task_errors.append({"id": task_id, "error": error})
            else:
                error_messages.append(f"Task in unexpected state: {state}")

            task_entry["completed_at"] = time_now.isoformat()
            updated_task_store.append(task_entry)

        except ValueError as e:
            error_messages.append(f"Unexpected error occured: {e}")
            continue

    sorted_active_tasks = sorted(
        [t for t in current_project_tasks if not t.get("cleared")],
        key=lambda t: datetime.fromisoformat(t.get("meta", {}).get("start_time")),
        reverse=True,
    )
    task_rows = [
        format_task_overview_row(
            task_entry["id"],
            task_entry.get("meta", {}),
            task_entry.get("state", ""),
        )
        for task_entry in sorted_active_tasks
    ]

    # TODO: what if there is both error messages and success messages
    error_output = "\n".join(error_messages) if error_messages else dash.no_update
    error_open = True if error_messages else current_error_open
    success_output = "\n".join(success_messages) if success_messages else dash.no_update
    success_open = True if success_messages else current_success_open

    refresh_path = url_path if (success_messages or error_messages) else dash.no_update
    polling_disabled = not any(
        not task.get("completed_at") and not task.get("cleared")
        for task in updated_task_store
    )

    task_info_header = [
        html.Thead(
            html.Tr(
                [html.Th("Analysis Type"), html.Th("Status"), html.Th("Time Elapsed")]
            )
        )
    ]
    default_row = [html.Tr([html.Td("No recent analyses"), html.Td(""), html.Td("")])]
    task_rows = task_rows or default_row

    return (
        error_output,
        error_open,
        success_output,
        success_open,
        updated_task_store,
        refresh_path,
        polling_disabled,
        task_info_header + [html.Tbody(task_rows)],
        task_error_store + task_errors,
    )


@callback(
    Output("task-error-modal-project", "is_open"),
    Output("task-error-modal-project", "children"),
    Input({"type": "task-error", "index": ALL}, "n_clicks"),
    State("task-error-store", "data"),
    prevent_initial_call=True,
)
def open_task_error_modal(n_clicks, task_errors):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered_id is None:
        raise dash.exceptions.PreventUpdate

    for i, clicks in enumerate(n_clicks):
        if clicks and clicks > 0:
            task_id = ctx.inputs_list[0][i]["id"]["index"]

            error_msg = next(
                (err["error"] for err in task_errors if err["id"] == task_id), None
            )
            if not error_msg:
                break

            modal_children = [
                dbc.ModalHeader(dbc.ModalTitle("Error")),
                dbc.ModalBody(error_msg),
            ]
            return True, modal_children

    raise dash.exceptions.PreventUpdate


@callback(
    Output("project-task-store", "data", allow_duplicate=True),
    Output("project-task-poll", "disabled", allow_duplicate=True),
    Input("clear-recent-project", "n_clicks"),
    State("project-task-store", "data"),
    State("project-id", "data"),
    prevent_initial_call=True,
)
def clear_completed_tasks(_, task_store, project_id):
    if not task_store or not project_id:
        return dash.no_update, dash.no_update

    for task in task_store:
        if task.get("completed_at") and task.get("project_id") == project_id:
            task["cleared"] = True
    return task_store, False

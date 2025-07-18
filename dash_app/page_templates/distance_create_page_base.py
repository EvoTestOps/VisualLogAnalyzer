import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback

from dash_app.callbacks.callback_functions import (
    run_log_distance,
    get_filter_options,
    get_log_data_directory_options,
)
from dash_app.components.forms import distance_file_level_form, distance_run_level_form
from dash_app.utils.metadata import parse_query_parameter
from dash_app.components.layouts import create_new_analysis_base_layout


# config: {
#     title: <title>,
#     type: eg. distance-file-level
#     level: file or directory
#     base_ids: {
#         error_toast_id: <id>
#         success_toast_id: <id>
#         url_id: <id>
#         redirect_id: <id>
#         project_store_id: <id>,
#     }
#     form_input_ids: {
#         form input ids
#     }
# }


def create_layout(config):
    form_map = {
        "distance-file-level": distance_file_level_form,
        "distance-directory-level": distance_run_level_form,
    }
    form_type = form_map.get(config["type"])
    form = form_type(**config["form_input_ids"])

    base = create_new_analysis_base_layout(**config["base_ids"])
    content = dbc.Container(form)

    return [base, content]


def register_callbacks(config):
    base_ids = config["base_ids"]
    form_ids = config["form_input_ids"]

    @callback(
        Output(base_ids["project_store_id"], "data"),
        Output(base_ids["error_toast_id"], "children"),
        Output(base_ids["error_toast_id"], "is_open"),
        Input(base_ids["url_id"], "search"),
    )
    def get_project_id(search):
        id = parse_query_parameter(search, "project_id")
        if not id:
            return None, "No project id provided. The analysis will fail.", True

        return id, dash.no_update, False

    @callback(
        Output(form_ids["directory_id"], "options"),
        Input(base_ids["url_id"], "search"),
    )
    def get_log_data_directories(_):
        return get_log_data_directory_options()

    @callback(
        Output(form_ids["runs_filter_id"], "options"),
        Output(form_ids["target_run_id"], "options"),
        Input(form_ids["directory_id"], "value"),
    )
    def get_comparison_and_target_options(directory_path):
        runs_or_files = "files" if config["level"] == "file" else "runs"
        options = get_filter_options(directory_path, runs_or_files=runs_or_files)
        return options, options

    @callback(
        Output(base_ids["error_toast_id"], "children", allow_duplicate=True),
        Output(base_ids["error_toast_id"], "is_open", allow_duplicate=True),
        Output(base_ids["success_toast_id"], "children"),
        Output(base_ids["success_toast_id"], "is_open"),
        Output(base_ids["redirect_id"], "href"),
        Input(form_ids["submit_id"], "n_clicks"),
        State(base_ids["project_store_id"], "data"),
        State(form_ids["directory_id"], "value"),
        State(form_ids["target_run_id"], "value"),
        State(form_ids["runs_filter_id"], "value"),
        State(form_ids["enhancement_id"], "value"),
        State(form_ids["mask_id"], "value"),
        State(form_ids["vectorizer_id"], "value"),
        prevent_initial_call=True,
    )
    def run_analysis(
        _,
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
                level="file" if config["level"] == "file" else "directory",
            )

            return (
                dash.no_update,
                False,
                "Analysis is running",
                True,
                f"/dash/project/{project_id}?task_id={result.get('task_id')}",
            )
        except ValueError as e:
            return (
                dash.no_update,
                str(e),
                True,
                dash.no_update,
                False,
                dash.no_update,
            )

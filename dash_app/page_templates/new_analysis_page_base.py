import inspect

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback

from dash_app.callbacks.callback_functions import (
    get_filter_options,
    get_log_data_directory_options,
    poll_task_status,
)
from dash_app.components.forms import (
    directory_level_viz_form,
    distance_file_level_form,
    distance_run_level_form,
    file_level_viz_form,
    test_train_file_level_form,
    test_train_form,
)
from dash_app.components.layouts import create_new_analysis_base_layout
from dash_app.utils.metadata import parse_query_parameter

# Config dictionary expected by the page template and callback registration:
# {
#   "type": <str>,                   # Analysis type, e.g. distance-file-level
#   "level": <str>,                  # Analysis level: 'file', 'line' or 'directory'
#   "base_ids": {                    # Common components' ids
#       title: <str>                 # Title of the page
#       error_toast_id: <str>,
#       success_toast_id: <str>,
#       url_id: <str>,
#       redirect_id: <str>,
#       project_store_id: <str>,
#   }
#   "form_input_ids": {                # IDs for form inputs, specific to the analysis form
#       <input_name_id>: <str>,        #  determined by the 'type'
#       ...
#   }
#   "input_fields": [                  # Ordered list of keys from form_input_ids that
#       <str>,                         # correspond to the inputs passed to the run function.
#       ...
#   ]
#
# }


def create_layout(config):
    form_map = {
        "distance-file-level": distance_file_level_form,
        "distance-directory-level": distance_run_level_form,
        "directory-level-visualisations": directory_level_viz_form,
        "file-level-visualisations": file_level_viz_form,
        "ano-directory-level": test_train_form,
        "ano-file-level": test_train_file_level_form,
        "ano-line-level": test_train_form,
    }
    form_type = form_map.get(config["type"])

    form_function_signarute = inspect.signature(form_type)
    if (
        "manual_filenames" in config
        and "manual_filenames" in form_function_signarute.parameters
    ):
        form = form_type(
            **config["form_input_ids"], manual_filenames=config["manual_filenames"]
        )
    else:
        form = form_type(**config["form_input_ids"])

    manual_filenames = config.get("manual_filenames", False)
    base = create_new_analysis_base_layout(
        **config["base_ids"], manual_filenames=manual_filenames
    )
    content = dbc.Container(form)

    return [base, content]


def register_callbacks(config, run_func):
    base_ids = config["base_ids"]
    form_ids = config["form_input_ids"]

    @callback(
        Output(base_ids["project_store_id"], "data"),
        Output(base_ids["error_toast_id"], "children"),
        Output(base_ids["error_toast_id"], "is_open"),
        Output(base_ids["project_link_id"], "href"),
        Input(base_ids["url_id"], "search"),
    )
    def get_project_id(search):
        id = parse_query_parameter(search, "project_id")
        if not id:
            return (
                None,
                "No project id provided. The analysis will fail.",
                True,
                dash.no_update,
            )

        return id, dash.no_update, False, f"/dash/project/{id}"

    if "directory_id" in form_ids:

        @callback(
            Output(form_ids["directory_id"], "options"),
            Input(base_ids["project_store_id"], "data"),
        )
        def get_log_data_directories(project_id):
            return get_log_data_directory_options(project_id)

    else:

        @callback(
            Output(form_ids["train_data_id"], "options"),
            Output(form_ids["test_data_id"], "options"),
            Input(base_ids["project_store_id"], "data"),
        )
        def get_log_data_directories(project_id):
            options = get_log_data_directory_options(project_id)
            return options, options

    if (
        "directory_id" in form_ids
        and "target_run_id" in form_ids
        and "runs_filter_id" in form_ids
    ):

        @callback(
            Output(form_ids["runs_filter_id"], "options"),
            Output(form_ids["target_run_id"], "options"),
            Input(form_ids["directory_id"], "value"),
            State(base_ids["manual_filenames_id"], "data"),
        )
        def get_comparison_and_target_options(directory_path, manual_filenames):
            if manual_filenames:
                return [], []
            runs_or_files = "files" if config["level"] == "file" else "runs"
            options = get_filter_options(directory_path, runs_or_files=runs_or_files)
            return options, options

    elif (
        "runs_filter_id" in form_ids or "files_filter_id" in form_ids
    ) and "test_data_id" in form_ids:

        @callback(
            Output(form_ids["runs_filter_id"], "options"),
            Output(form_ids["runs_filter_train_id"], "options"),
            Input(form_ids["test_data_id"], "value"),
            Input(form_ids["train_data_id"], "value"),
            State(base_ids["manual_filenames_id"], "data"),
        )
        def get_comparison_options(dir_path_test, dir_path_train, manual_filenames):
            if manual_filenames:
                return [], []
            runs_or_files = "files" if config["level"] == "file" else "runs"

            options_test = get_filter_options(
                dir_path_test, runs_or_files=runs_or_files
            )
            options_train = get_filter_options(
                dir_path_train, runs_or_files=runs_or_files
            )

            return options_test, options_train

    @callback(
        Output(base_ids["error_toast_id"], "children", allow_duplicate=True),
        Output(base_ids["error_toast_id"], "is_open", allow_duplicate=True),
        Output(base_ids["success_toast_id"], "children"),
        Output(base_ids["success_toast_id"], "is_open"),
        Output(base_ids["redirect_id"], "href"),
        Output(base_ids["interval_id"], "disabled"),
        Output(base_ids["task_store_id"], "data"),
        Input(form_ids["submit_id"], "n_clicks"),
        State(base_ids["project_store_id"], "data"),
        *[State(form_ids[field], "value") for field in config["input_fields"]],
        prevent_initial_call=True,
    )
    def run_analysis(
        _,
        project_id,
        *args,
    ):

        redirect_value = None
        try:
            if "results_redirect_id" in config["input_fields"]:
                redirect_index = config["input_fields"].index("results_redirect_id")
                redirect_value = args[redirect_index]

                args = args[:redirect_index] + args[redirect_index + 1 :]

            result = run_func(project_id, *args, level=config["level"])

            if redirect_value is True:
                return (
                    dash.no_update,
                    False,
                    "Analysis is running",
                    True,
                    dash.no_update,
                    False,
                    result.get("task_id"),
                )

            return (
                dash.no_update,
                False,
                "Analysis is running",
                True,
                f"/dash/project/{project_id}?task_id={result.get('task_id')}",
                True,
                dash.no_update,
            )
        except ValueError as e:
            return (
                str(e),
                True,
                dash.no_update,
                False,
                dash.no_update,
                True,
                dash.no_update,
            )

    @callback(
        Output(base_ids["error_toast_id"], "children", allow_duplicate=True),
        Output(base_ids["error_toast_id"], "is_open", allow_duplicate=True),
        Output(base_ids["success_toast_id"], "children", allow_duplicate=True),
        Output(base_ids["success_toast_id"], "is_open", allow_duplicate=True),
        Output(base_ids["redirect_id"], "href", allow_duplicate=True),
        Output(base_ids["interval_id"], "disabled", allow_duplicate=True),
        Input(base_ids["interval_id"], "n_intervals"),
        State(base_ids["task_store_id"], "data"),
        prevent_initial_call=True,
    )
    def poll_result(_, task_id):
        if task_id is None:
            return (
                dash.no_update,
                False,
                dash.no_update,
                False,
                dash.no_update,
                dash.no_update,
            )

        try:
            result = poll_task_status(task_id)
            if result.get("ready"):
                state = result.get("state")
                if state == "SUCCESS":
                    task_result = result.get("result")
                    return (
                        dash.no_update,
                        False,
                        dash.no_update,
                        False,
                        f"/dash/analysis/{task_result["type"]}/{task_result["id"]}",
                        True,
                    )
                elif state == "FAILURE":
                    error_message = result["result"].get("error", "Task failed.")
                    return (
                        error_message,
                        True,
                        dash.no_update,
                        False,
                        dash.no_update,
                        True,
                    )
                else:
                    return (
                        f"Task is in an unexpected state: {state}",
                        True,
                        dash.no_update,
                        False,
                        dash.no_update,
                        True,
                    )

        except ValueError as e:
            return str(e), True, dash.no_update, False, dash.no_update, True

        return dash.no_update, False, dash.no_update, False, dash.no_update, False

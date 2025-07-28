import dash
from dash_app.page_templates.new_analysis_page_base import (
    create_layout,
    register_callbacks,
)
from dash_app.callbacks.callback_functions import (
    run_log_distance,
    fetch_project_settings,
)

config = {
    "type": "distance-file-level",
    "level": "file",
    "path_template": "/analysis/distance-file-level/create",
    "base_ids": {
        "title": "New File Level Log Distance",
        "error_toast_id": "error-toast-dis-file-new",
        "success_toast_id": "success-toast-dis-file-new",
        "url_id": "url-dis-file-new",
        "redirect_id": "analysis-id-dis-file-new",
        "project_store_id": "project-store-dis-file-new",
        "interval_id": "interval-dis-file-new",
        "task_store_id": "task-store-dis-file-new",
        "project_link_id": "project-link-dis-file-new",
        "manual_filenames_id": "manual-filenames-dis-file-new",
    },
    "form_input_ids": {
        "submit_id": "submit-dis-file-new",
        "directory_id": "directory-dis-file-new",
        "enhancement_id": "enhancement-dis-file-new",
        "target_run_id": "target-dis-file-new",
        "runs_filter_id": "filter-dis-file-new",
        "mask_id": "mask-dis-file-new",
        "vectorizer_id": "vectorizer-dis-file-new",
        "results_redirect_id": "results-redirect-dis-file-new",
    },
    "input_fields": [
        "directory_id",
        "target_run_id",
        "runs_filter_id",
        "enhancement_id",
        "vectorizer_id",
        "mask_id",
        "results_redirect_id",
    ],
}

dash.register_page(__name__, path_template=config["path_template"])


def layout(**kwargs):
    project_id = kwargs.get("project_id")

    manual_filenames = False
    if project_id:
        settings = fetch_project_settings(project_id)
        manual_filenames = settings.get("manual_filename_input", False)

    config["manual_filenames"] = manual_filenames

    return create_layout(config)


register_callbacks(config, run_func=run_log_distance)

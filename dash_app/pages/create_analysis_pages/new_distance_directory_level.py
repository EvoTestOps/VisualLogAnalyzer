import dash
from dash_app.page_templates.new_analysis_page_base import (
    create_layout,
    register_callbacks,
)
from dash_app.callbacks.callback_functions import run_log_distance

config = {
    "type": "distance-directory-level",
    "level": "directory",
    "path_template": "/analysis/distance-directory-level/create",
    "base_ids": {
        "title": "New Directory Level Log Distance",
        "error_toast_id": "error-toast-dis-dir-new",
        "success_toast_id": "success-toast-dis-dir-new",
        "url_id": "url-dis-dir-new",
        "redirect_id": "analysis-id-dis-dir-new",
        "project_store_id": "project-store-dis-dir-new",
        "interval_id": "interval-dis-dir-new",
        "task_store_id": "task-store-dis-dir-new",
        "project_link_id": "project-link-dis-dir-new",
        "manual_filenames_id": "manual-filenames-dis-dir-new",
    },
    "form_input_ids": {
        "submit_id": "submit-dis-dir-new",
        "directory_id": "directory-dis-dir-new",
        "enhancement_id": "enhancement-dis-dir-new",
        "target_run_id": "target-dis-dir-new",
        "runs_filter_id": "filter-dis-dir-new",
        "mask_id": "mask-dis-dir-new",
        "vectorizer_id": "vectorizer-dis-dir-new",
        "results_redirect_id": "results-redirect-dis-dir-new",
        "analysis_name_id": "analysis-name-dis-dir-new",
    },
    "input_fields": [
        "directory_id",
        "target_run_id",
        "runs_filter_id",
        "enhancement_id",
        "vectorizer_id",
        "mask_id",
        "results_redirect_id",
        "analysis_name_id",
    ],
}

dash.register_page(__name__, path_template=config["path_template"])


def layout(**kwargs):
    return create_layout(config)


register_callbacks(config, run_func=run_log_distance)

import dash
from dash_app.page_templates.new_analysis_page_base import (
    create_layout,
    register_callbacks,
)
from dash_app.callbacks.callback_functions import run_high_level_analysis

config = {
    "type": "directory-level-visualisations",
    "level": "directory",
    "path_template": "/analysis/directory-level-visualisations/create",
    "base_ids": {
        "title": "New Directory Level Visualisation",
        "error_toast_id": "error-toast-high-dir-new",
        "success_toast_id": "success-toast-high-dir-new",
        "url_id": "url-high-dir-new",
        "redirect_id": "analysis-id-high-dir-new",
        "project_store_id": "project-store-high-dir-new",
        "interval_id": "interval-high-dir-new",
        "task_store_id": "task-store-high-dir-new",
        "project_link_id": "project-link-high-dir-new",
        "manual_filenames_id": "manual-filenames-high-dir-new",
    },
    "form_input_ids": {
        "submit_id": "submit-high-dir-new",
        "directory_id": "directory-high-dir-new",
        "analysis_type_id": "analysis-type-file-new",
        "mask_id": "mask-high-dir-new",
        "vectorizer_id": "vectorizer-high-dir-new",
        "results_redirect_id": "results-redirect-high-dir-new",
    },
    "input_fields": [
        "directory_id",
        "analysis_type_id",
        "mask_id",
        "vectorizer_id",
        "results_redirect_id",
    ],
}

dash.register_page(__name__, path_template=config["path_template"])


def layout(**kwargs):
    return create_layout(config)


register_callbacks(config, run_func=run_high_level_analysis)

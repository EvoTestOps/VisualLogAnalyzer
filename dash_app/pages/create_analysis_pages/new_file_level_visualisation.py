import dash
from dash_app.page_templates.new_analysis_page_base import (
    create_layout,
    register_callbacks,
)
from dash_app.callbacks.callback_functions import run_high_level_analysis

config = {
    "type": "file-level-visualisations",
    "level": "file",
    "path_template": "/analysis/file-level-visualisations/create",
    "base_ids": {
        "title": "New File Level Visualisation",
        "error_toast_id": "error-toast-high-file-new",
        "success_toast_id": "success-toast-high-file-new",
        "url_id": "url-high-file-new",
        "redirect_id": "analysis-id-high-file-new",
        "project_store_id": "project-store-high-file-new",
        "interval_id": "interval-high-file-new",
        "task_store_id": "task-store-high-file-new",
        "project_link_id": "project-link-high-file-new",
    },
    "form_input_ids": {
        "submit_id": "submit-high-file-new",
        "directory_id": "directory-high-file-new",
        "analysis_type_id": "analysis-type-file-new",
        "mask_id": "mask-high-file-new",
        "vectorizer_id": "vectorizer-high-file-new",
        "results_redirect_id": "results-redirect-high-file-new",
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

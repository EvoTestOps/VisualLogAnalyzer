import dash
from dash_app.page_templates.new_analysis_page_base import (
    create_layout,
    register_callbacks,
)
from dash_app.callbacks.callback_functions import run_anomaly_detection

config = {
    "type": "ano-directory-level",
    "level": "directory",
    "path_template": "/analysis/ano-directory-level/create",
    "base_ids": {
        "title": "New Directory Level Anomaly Detection",
        "error_toast_id": "error-toast-ano-dir-new",
        "success_toast_id": "success-toast-ano-dir-new",
        "url_id": "url-ano-dir-new",
        "redirect_id": "analysis-id-ano-dir-new",
        "project_store_id": "project-store-ano-dir-new",
        "interval_id": "interval-ano-dir-new",
        "task_store_id": "task-store-ano-dir-new",
        "project_link_id": "project-link-ano-dir-new",
        "manual_filenames_id": "manual-filenames-ano-dir-new",
    },
    "form_input_ids": {
        "submit_id": "submit-ano-dir-new",
        "train_data_id": "train-data-ano-dir-new",
        "test_data_id": "test-data-dir-dir-new",
        "detectors_id": "detectors-ano-dir-new",
        "enhancement_id": "enhancement-ano-dir-new",
        "runs_filter_id": "filter-ano-dir-new",
        "mask_input_id": "mask-ano-dir-new",
        "vectorizer_id": "vectorizer-ano-dir-new",
        "results_redirect_id": "results-redirect-ano-dir-new",
        "analysis_name_id": "analysis-name-ano-dir-new",
    },
    "input_fields": [
        "train_data_id",
        "test_data_id",
        "detectors_id",
        "enhancement_id",
        "runs_filter_id",
        "mask_input_id",
        "vectorizer_id",
        "results_redirect_id",
        "analysis_name_id",
    ],
}

dash.register_page(__name__, path_template=config["path_template"])


def layout(**kwargs):
    return create_layout(config)


register_callbacks(config, run_func=run_anomaly_detection)

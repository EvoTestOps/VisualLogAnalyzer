import dash
from dash_app.page_templates.new_analysis_page_base import (
    create_layout,
    register_callbacks,
)
from dash_app.callbacks.callback_functions import run_anomaly_detection

config = {
    "type": "ano-line-level",
    "level": "line",
    "path_template": "/analysis/ano-line-level/create",
    "base_ids": {
        "title": "New Line Level Anomaly Detection",
        "error_toast_id": "error-toast-ano-line-new",
        "success_toast_id": "success-toast-ano-line-new",
        "url_id": "url-ano-line-new",
        "redirect_id": "analysis-id-ano-line-new",
        "project_store_id": "project-store-ano-line-new",
        "interval_id": "interval-ano-line-new",
        "task_store_id": "task-store-ano-line-new",
        "project_link_id": "project-link-ano-line-new",
    },
    "form_input_ids": {
        "submit_id": "submit-ano-line-new",
        "train_data_id": "train-data-ano-line-new",
        "test_data_id": "test-data-ano-line-new",
        "detectors_id": "detectors-ano-line-new",
        "enhancement_id": "enhancement-ano-line-new",
        "runs_filter_id": "filter-ano-line-new",
        "mask_input_id": "mask-ano-line-new",
        "vectorizer_id": "vectorizer-ano-line-new",
        "results_redirect_id": "results-redirect-ano-line-new",
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
    ],
}

dash.register_page(__name__, path_template=config["path_template"])


def layout(**kwargs):
    return create_layout(config)


register_callbacks(config, run_func=run_anomaly_detection)

import dash
from dash_app.page_templates.datatable_result_page_base import (
    create_layout,
    register_callback,
)

config = {
    "title": "Anomaly Detection Directory Level",
    "path_template": "/analysis/ano-directory-level/<analysis_id>",
    "ids": {
        "project_link": "project-link-ano-dir-res",
        "analysis_id": "analysis-id-ano-dir-res",
        "datatable": "datatable-ano-dir-res",
        "metadata": "metadata-ano-dir-res",
        "error_toast": "error-toast-ano-dir-res",
        "success_toast": "success-toast-ano-dir-res",
    },
}

dash.register_page(__name__, path_template=config["path_template"])


def layout(analysis_id=None, **kwargs):
    return create_layout(config, analysis_id)


register_callback(config)

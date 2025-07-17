import dash
from dash_app.page_templates.datatable_result_page_base import (
    create_layout,
    register_callback,
)

config = {
    "title": "Anomaly Detection File Level",
    "path_template": "/analysis/ano-file-level/<analysis_id>",
    "ids": {
        "project_link": "project-link-ano-file-res",
        "analysis_id": "analysis-id-ano-file-res",
        "datatable": "datatable-ano-file-res",
        "metadata": "metadata-ano-file-res",
        "error_toast": "error-toast-ano-file-res",
        "success_toast": "success-toast-ano-file-res",
    },
}

dash.register_page(__name__, path_template=config["path_template"])


def layout(analysis_id=None, **kwargs):
    return create_layout(config, analysis_id)


register_callback(config)

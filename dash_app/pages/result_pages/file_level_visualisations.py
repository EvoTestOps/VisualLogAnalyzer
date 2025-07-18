import dash
from dash_app.page_templates.high_level_viz_result_page_base import (
    create_layout,
    register_callback,
)

config = {
    "title": "File Level Visualisation",
    "path_template": "/analysis/file-level-visualisations/<analysis_id>",
    "ids": {
        "project_link": "project-link-high-file-res",
        "analysis_id": "analysis-id-high-file-res",
        "plot_content": "plot-content-high-file-res",
        "metadata": "metadata-high-file-res",
        "error_toast": "error-toast-high-file-res",
        "success_toast": "success-toast-high-file-res",
    },
}

dash.register_page(__name__, path_template=config["path_template"])


def layout(analysis_id=None, **kwargs):
    return create_layout(config, analysis_id)


register_callback(config)

import dash
from dash_app.page_templates.high_level_viz_result_page_base import (
    create_layout,
    register_callback,
)

config = {
    "title": "Directory Level Visualisation",
    "path_template": "/analysis/directory-level-visualisations/<analysis_id>",
    "ids": {
        "project_link": "project-link-high-dir-res",
        "analysis_id": "analysis-id-high-dir-res",
        "plot_content": "plot-content-high-dir-res",
        "metadata": "metadata-high-dir-res",
        "error_toast": "error-toast-high-dir-res",
        "success_toast": "success-toast-high-dir-res",
    },
}

dash.register_page(__name__, path_template=config["path_template"])


def layout(analysis_id=None, **kwargs):
    return create_layout(config, analysis_id)


register_callback(config)

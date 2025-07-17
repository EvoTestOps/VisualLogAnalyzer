import dash
from dash import Input, Output, State, callback, html

from dash_app.callbacks.callback_functions import (
    create_high_level_plot,
)
from dash_app.components.layouts import (
    create_high_level_viz_result_layout,
    create_result_base_layout,
)


def create_layout(config, analysis_id=None):
    config_ids = config["ids"]
    base = create_result_base_layout(
        config["title"],
        analysis_id,
        config_ids["project_link"],
        config_ids["analysis_id"],
    )
    content = create_high_level_viz_result_layout(
        config_ids["plot_content"],
        config_ids["metadata"],
        config_ids["error_toast"],
        config_ids["success_toast"],
    )
    return base + content


def register_callback(config):
    config_ids = config["ids"]

    @callback(
        Output(config_ids["plot_content"], "figure"),
        Output(config_ids["plot_content"], "style"),
        Output(config_ids["metadata"], "children"),
        Output(config_ids["project_link"], "href"),
        Output(config_ids["error_toast"], "children"),
        Output(config_ids["error_toast"], "is_open"),
        Output(config_ids["success_toast"], "children"),
        Output(config_ids["success_toast"], "is_open"),
        Input("switch", "value"),
        State(config_ids["analysis_id"], "data"),
    )
    def populate_table(switch_on, analysis_id):
        try:
            fig, style, metadata_rows, project_id = create_high_level_plot(
                switch_on, analysis_id
            )
            return (
                fig,
                style,
                [html.Tbody(metadata_rows)],
                f"/dash/project/{project_id}",
                dash.no_update,
                False,
                dash.no_update,
                False,
            )
        except ValueError as e:
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                str(e),
                True,
                dash.no_update,
                False,
            )

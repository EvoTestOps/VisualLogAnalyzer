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
        config_ids["group_by"],
        config_ids["separator"],
    )
    return base + content


def register_callback(config):
    config_ids = config["ids"]

    # Part numbers only mean something for the separator they were listed with,
    # so a new separator starts from no grouping.
    @callback(
        Output(config_ids["group_by"], "value"),
        Input(config_ids["separator"], "value"),
        prevent_initial_call=True,
    )
    def reset_group_by(_):
        return []

    # The name parts to group by are offered by the plot callback itself, since
    # the values to pick from are only known once the results have been read.
    @callback(
        Output(config_ids["plot_content"], "figure"),
        Output(config_ids["plot_content"], "style"),
        Output(config_ids["metadata"], "children"),
        Output(config_ids["project_link"], "href"),
        Output(config_ids["group_by"], "options"),
        Output(config_ids["error_toast"], "children"),
        Output(config_ids["error_toast"], "is_open"),
        Output(config_ids["success_toast"], "children"),
        Output(config_ids["success_toast"], "is_open"),
        Input("switch", "value"),
        Input(config_ids["group_by"], "value"),
        Input(config_ids["separator"], "value"),
        State(config_ids["analysis_id"], "data"),
    )
    def create_plot(switch_on, group_by_indices, separator, analysis_id):
        try:
            fig, style, metadata_rows, project_id, group_by_options = (
                create_high_level_plot(
                    switch_on, analysis_id, group_by_indices, separator
                )
            )
            return (
                fig,
                style,
                [html.Tbody(metadata_rows)],
                f"/dash/project/{project_id}",
                group_by_options,
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
                dash.no_update,
                str(e),
                True,
                dash.no_update,
                False,
            )

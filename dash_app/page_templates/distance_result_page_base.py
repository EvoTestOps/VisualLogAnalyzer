import dash
from dash import Input, Output, callback, html
from dash_app.components.layouts import (
    create_datatable_layout,
    create_result_base_layout,
)
from dash_app.callbacks.callback_functions import (
    populate_datatable,
)


def create_layout(config, analysis_id=None):
    config_ids = config["ids"]
    base = create_result_base_layout(
        config["title"],
        analysis_id,
        config_ids["project_link"],
        config_ids["analysis_id"],
    )
    content = create_datatable_layout(
        config_ids["datatable"],
        config_ids["metadata"],
        config_ids["error_toast"],
        config_ids["success_toast"],
    )
    return base + content


def register_callback(config):
    config_ids = config["ids"]

    @callback(
        Output(config_ids["datatable"], "data"),
        Output(config_ids["datatable"], "columns"),
        Output(config_ids["metadata"], "children"),
        Output(config_ids["project_link"], "href"),
        Output(config_ids["error_toast"], "children"),
        Output(config_ids["error_toast"], "is_open"),
        Output(config_ids["success_toast"], "children"),
        Output(config_ids["success_toast"], "is_open"),
        Input(config_ids["analysis_id"], "data"),
    )
    def populate_table(analysis_id):
        try:
            df_dict, columns, metadata_rows, project_id = populate_datatable(
                analysis_id
            )

            return (
                df_dict,
                columns,
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
                str(e),
                True,
                dash.no_update,
                False,
            )

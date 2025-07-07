# import dash
# import dash_bootstrap_components as dbc
# from dash import Input, Output, State, callback, html
# from dash_app.components.forms import distance_file_level_form
# from dash_app.components.layouts import create_datatable_layout
# from dash_app.callbacks.callback_functions import (
#     get_filter_options,
#     populate_distance_table,
# )
#
# dash.register_page(
#     __name__, path="/distance-file-level", title="File Level Log Distance"
# )
#
# form = distance_file_level_form(
#     "submit_dis_file",
#     "directory_dis_file",
#     "enhancement_dis_file",
#     "target_run_dis_file",
#     "runs_filter_dis_file",
#     "mask_dis_file",
#     "vectorizer_dis_file",
# )
# layout = [dbc.Container(html.H3("File Level Log Distance"))] + create_datatable_layout(
#     form,
#     "error_toast_dis_file",
#     "success_toast_dis_file",
#     "data_table_dis_file",
# )
#
#
# @callback(
#     Output("runs_filter_dis_file", "options"),
#     Output("target_run_dis_file", "options"),
#     Input("directory_dis_file", "value"),
# )
# def get_comparison_and_target_options(directory_path):
#     options = get_filter_options(directory_path, runs_or_files="files")
#     return options, options
#
#
# @callback(
#     Output("data_table_dis_file", "data"),
#     Output("data_table_dis_file", "columns"),
#     Output("error_toast_dis_file", "children"),
#     Output("error_toast_dis_file", "is_open"),
#     Output("success_toast_dis_file", "children"),
#     Output("success_toast_dis_file", "is_open"),
#     Input("submit_dis_file", "n_clicks"),
#     State("directory_dis_file", "value"),
#     State("target_run_dis_file", "value"),
#     State("runs_filter_dis_file", "value"),
#     State("enhancement_dis_file", "value"),
#     State("mask_dis_file", "value"),
#     State("vectorizer_dis_file", "value"),
#     prevent_initial_call=True,
# )
# def populate_table(
#     n_clicks,
#     directory_path,
#     target_run,
#     comparision_runs,
#     enhancement,
#     mask_type,
#     vectorizer_type,
# ):
#     return populate_distance_table(
#         n_clicks,
#         directory_path,
#         target_run,
#         comparision_runs,
#         enhancement,
#         vectorizer_type,
#         mask_type,
#         level="file",
#     )

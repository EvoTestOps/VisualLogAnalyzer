import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html
from dash_app.components.forms import distance_run_level_form
from dash_app.components.layouts import create_ano_run_level_layout
from dash_app.callbacks.callback_functions import (
    get_filter_options,
    populate_distance_table,
)

dash.register_page(__name__, path="/distance-run-level", title="Run Level Log Distance")

form = distance_run_level_form(
    "submit_dis",
    "directory_dis",
    "enhancement_dis",
    "target_run_dis",
    "runs_filter_dis",
)
layout = [
    dbc.Container(html.H3("Directory Level Log Distance"))
] + create_ano_run_level_layout(
    form,
    "error_toast_dis",
    "success_toast_dis",
    "data_table_dis",
)


@callback(
    Output("runs_filter_dis", "options"),
    Output("target_run_dis", "options"),
    Input("directory_dis", "value"),
)
def get_comparison_and_target_options(directory_path):
    options = get_filter_options(directory_path, runs_or_files="runs")
    return options, options


@callback(
    Output("data_table_dis", "data"),
    Output("data_table_dis", "columns"),
    Output("error_toast_dis", "children"),
    Output("error_toast_dis", "is_open"),
    Output("success_toast_dis", "children"),
    Output("success_toast_dis", "is_open"),
    Input("submit_dis", "n_clicks"),
    State("directory_dis", "value"),
    State("target_run_dis", "value"),
    State("runs_filter_dis", "value"),
    State("enhancement_dis", "value"),
    prevent_initial_call=True,
)
def populate_table(
    n_clicks,
    directory_path,
    target_run,
    comparision_runs,
    enhancement,
):
    return populate_distance_table(
        n_clicks, directory_path, target_run, comparision_runs, enhancement, level="run"
    )

import dash
import polars as pl
import requests
from dash import Input, Output, State, callback
import io
from dash_app.components.forms import distance_run_level_form
from dash_app.components.layouts import create_ano_run_level_layout

from dash_app.utils.data_directories import get_runs

dash.register_page(__name__, path="/distance-run-level", title="Run Level Log Distance")

form = distance_run_level_form(
    "submit_dis",
    "directory_dis",
    "enhancement_dis",
    "target_run_dis",
    "runs_filter_dis",
)
layout = create_ano_run_level_layout(
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
def get_comparison_options(directory_path):
    if directory_path is None:
        return {}, {}

    runs = get_runs(directory_path)

    options = [{"label": run, "value": run} for run in runs]
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
    if n_clicks == 0:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    try:
        response = requests.post(
            "http://localhost:5000/api/run-distance",
            json={
                "dir_path": directory_path,
                "target_run": target_run,
                "comparison_runs": comparision_runs,
                "item_list_col": enhancement,
            },
        )
        response.raise_for_status()

        df = pl.read_parquet(io.BytesIO(response.content))

        columns = [{"name": col, "id": col} for col in df.columns]

        return (
            df.to_dicts(),
            columns,
            "",
            False,
            "Analysis complete.",
            True,
        )

    except requests.exceptions.RequestException as e:
        try:
            error_message = response.json().get("error", str(e))
        except Exception:
            error_message = str(e)

        return (
            dash.no_update,
            dash.no_update,
            error_message,
            True,
            dash.no_update,
            False,
        )

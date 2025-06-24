import dash
import polars as pl
import requests
from dash import Input, Output, State, callback
import io
from dash_app.components.forms import distance_file_level_form
from dash_app.components.layouts import create_ano_run_level_layout

from dash_app.utils.data_directories import get_all_filenames

dash.register_page(
    __name__, path="/distance-file-level", title="File Level Log Distance"
)

form = distance_file_level_form(
    "submit_dis_file",
    "directory_dis_file",
    "enhancement_dis_file",
    "target_run_dis_file",
    "runs_filter_dis_file",
)
layout = create_ano_run_level_layout(
    form,
    "error_toast_dis_file",
    "success_toast_dis_file",
    "data_table_dis_file",
)


@callback(
    Output("runs_filter_dis_file", "options"),
    Output("target_run_dis_file", "options"),
    Input("directory_dis_file", "value"),
)
def get_comparison_options(directory_path):
    if directory_path is None:
        return {}, {}

    files = get_all_filenames(directory_path)

    options = [{"label": file, "value": file} for file in files]
    return options, options


@callback(
    Output("data_table_dis_file", "data"),
    Output("data_table_dis_file", "columns"),
    Output("error_toast_dis_file", "children"),
    Output("error_toast_dis_file", "is_open"),
    Output("success_toast_dis_file", "children"),
    Output("success_toast_dis_file", "is_open"),
    Input("submit_dis_file", "n_clicks"),
    State("directory_dis_file", "value"),
    State("target_run_dis_file", "value"),
    State("runs_filter_dis_file", "value"),
    State("enhancement_dis_file", "value"),
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
                "file_level": True,
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

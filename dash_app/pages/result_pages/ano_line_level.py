import base64
import io

import dash
import polars as pl
from dash import Input, Output, State, callback, html

from dash_app.callbacks.callback_functions import make_api_call
from dash_app.components.layouts import (
    create_ano_line_level_result_layout,
    create_result_base_layout,
)
from dash_app.utils.metadata import format_metadata_rows
from dash_app.utils.plots import create_line_level_plot, get_options

dash.register_page(
    __name__,
    path_template="/analysis/ano-line-level/<analysis_id>",
)


def layout(analysis_id=None, **kwargs):
    base = create_result_base_layout(
        "Anomaly Detection Line Level",
        analysis_id,
        "project-link-ano-line-res",
        "analysis-id-ano-line-res",
    )
    content = create_ano_line_level_result_layout(
        "stored-data-ano-line-res",
        "plot-selector-ano-line-res",
        "plot-content-ano-line-res",
        "datatable-ano-line-res",
        "metadata-ano-line-res",
        "error-toast-ano-line-res",
        "success-toats-ano-line-res",
    )

    return base + content


@callback(
    Output("stored-data-ano-line-res", "data"),
    Output("error-toast-ano-line-res", "children"),
    Output("error-toast-ano-line-res", "is_open"),
    Input("analysis-id-ano-line-res", "data"),
)
def get_data(analysis_id):
    response, error = make_api_call({}, f"analyses/{analysis_id}", "GET")

    if error or response is None:
        return dash.no_update, str(error), True

    df = pl.read_parquet(io.BytesIO(response.content))

    # This is kind of a hacky way to get the dataframe semi efficiently
    #  to the browsers memory. Converting to json is not really viable.
    # Potential improvements would be to store it server side, since
    #  this might not work so well with really large datasets.
    buffer = io.BytesIO()
    df.write_parquet(buffer)
    buffer.seek(0)

    encoded_df = base64.b64encode(buffer.read()).decode("utf-8")

    return (encoded_df, dash.no_update, False)


@callback(
    Output("plot-selector-ano-line-res", "options"),
    Output("metadata-ano-line-res", "children"),
    Output("project-link-ano-line-res", "href"),
    Output("error-toast-ano-line-res", "children", allow_duplicate=True),
    Output("error-toast-ano-line-res", "is_open", allow_duplicate=True),
    Input("stored-data-ano-line-res", "data"),
    State("analysis-id-ano-line-res", "data"),
    prevent_initial_call=True,
)
def generate_dropdown_and_metadata(encoded_df, analysis_id):
    if not encoded_df:
        return dash.no_update, dash.no_update, dash.no_update, "No results found", True

    decoded_df = base64.b64decode(encoded_df)
    df = pl.read_parquet(io.BytesIO(decoded_df))
    options = get_options(df)

    response, error = make_api_call({}, f"analyses/{analysis_id}/metadata", "GET")

    if error or response is None:
        return dash.no_update, str(error), True

    metadata = response.json()
    project_id = metadata.get("project_id")
    metadata_rows = format_metadata_rows(metadata)

    return (
        options,
        [html.Tbody(metadata_rows)],
        f"/dash/project/{project_id}",
        dash.no_update,
        False,
    )


@callback(
    Output("plot-content-ano-line-res", "figure"),
    Output("plot-content-ano-line-res", "style"),
    Input("plot-selector-ano-line-res", "value"),
    Input("switch", "value"),
    State("stored-data-ano-line-res", "data"),
    prevent_initial_call=True,
)
def render_plot(selected_plot, switch_on, encoded_df):
    if not encoded_df or not selected_plot:
        return dash.no_update, dash.no_update

    decoded_df = base64.b64decode(encoded_df)
    df = pl.read_parquet(io.BytesIO(decoded_df))

    theme = "plotly_white" if switch_on else "plotly_dark"
    style = {
        "resize": "both",
        "overflow": "auto",
        "minHeight": "500px",
        "minWidth": "600px",
        "width": "90%",
    }
    fig = create_line_level_plot(df, selected_plot, theme)

    return fig, style


@callback(
    Output("datatable-ano-line-res", "data"),
    Output("datatable-ano-line-res", "columns"),
    Input("stored-data-ano-line-res", "data"),
    Input("plot-selector-ano-line-res", "value"),
    prevent_initial_call=True,
)
def populate_table(encoded_df, selected_plot):
    if not encoded_df or not selected_plot:
        return [], []

    df = pl.read_parquet(io.BytesIO(base64.b64decode(encoded_df))).filter(
        pl.col("seq_id") == selected_plot
    )

    # df clean up
    df = df.drop(["seq_id", "orig_file_name", "run", "file_name"])
    df = df.select(
        ["line_number"] + [col for col in df.columns if col != "line_number"]
    )

    columns = [{"name": col, "id": col} for col in df.columns]
    return df.to_dicts(), columns


@callback(
    Output("datatable-ano-line-res", "selected_rows"),
    Output("datatable-ano-line-res", "selected_cells"),
    Output("datatable-ano-line-res", "active_cell"),
    Output("datatable-ano-line-res", "page_current"),
    Input("plot-content-ano-line-res", "clickData"),
    State("stored-data-ano-line-res", "data"),
    State("datatable-ano-line-res", "page_size"),
    prevent_initial_call=True,
)
def highlight_row_on_click(clickData, encoded_df, page_size):
    if not clickData or not encoded_df:
        return [], [], None, dash.no_update

    decoded_df = base64.b64decode(encoded_df)
    df = pl.read_parquet(io.BytesIO(decoded_df))

    clicked_x = clickData["points"][0]["x"]

    if "line_number" in df.columns or "index" in df.columns:
        selected_idx = clicked_x - 1
    else:
        selected_idx = None

    if selected_idx is None:
        return [], [], None, dash.no_update

    page = selected_idx // page_size

    selected_cells = []
    for i, col in enumerate(df.columns):
        cell = {
            "row": selected_idx % page_size,
            "column": i,
            "column_id": col,
        }
        selected_cells.append(cell)

    return [selected_idx], selected_cells, selected_cells[0], page

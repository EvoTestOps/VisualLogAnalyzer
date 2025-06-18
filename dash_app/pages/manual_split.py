import dash
import dash_bootstrap_components as dbc
import polars as pl
import requests
from dash import Input, Output, State, callback, html
import io
import base64
from dash_app.components.forms import test_train_form
from dash_app.components.layouts import create_default_layout

from dash_app.utils.plots import get_options, create_plot

dash.register_page(__name__, path="/manual-split", title="Manual Split Analysis")

form = test_train_form()
layout = create_default_layout(
    form, "stored_data_tr", "plot_selector_tr", "plot_content_tr"
)


@callback(
    Output("stored_data_tr", "data"),
    Output("plot_selector_tr", "options"),
    Input("submit_tr", "n_clicks"),
    State("log_format_tr", "value"),
    State("train_data_tr", "value"),
    State("test_data_tr", "value"),
    State("detectors_tr", "value"),
    State("enhancement_tr", "value"),
    prevent_initial_call=True,
)
def get_and_generate_dropdown(
    n_clicks,
    log_format,
    train_data,
    test_data,
    detectors,
    enhancement,
):
    if n_clicks == 0:
        return dash.no_update, dash.no_update

    buffer = None
    try:
        response = requests.post(
            "http://localhost:5000/api/manual-test-train",
            json={
                "train_data_path": train_data,
                "test_data_path": test_data,
                "log_format": log_format,
                "models": detectors,
                "item_list_col": enhancement,
                "seq": False,
            },
        )
        response.raise_for_status()

        parquet_bytes = io.BytesIO(response.content)
        df = pl.read_parquet(parquet_bytes)

        options = get_options(df)

        buffer = io.BytesIO()
        df.write_parquet(buffer)
        buffer.seek(0)

        encoded_df = base64.b64encode(buffer.read()).decode("utf-8")

        return encoded_df, options

    except Exception as e:
        return {"error": str(e)}, [{"label": str(e), "value": "error"}]

    finally:
        if buffer:
            buffer.close()


@callback(
    Output("plot_content_tr", "figure"),
    Input("plot_selector_tr", "value"),
    State("stored_data_tr", "data"),
    prevent_initial_call=True,
)
def render_plot(selected_plot, data):
    if not data or not selected_plot:
        return html.Div("Select a plot to display.")

    decoded_df = base64.b64decode(data)
    df = pl.read_parquet(io.BytesIO(decoded_df))

    fig = create_plot(df, selected_plot)

    return fig


@callback(
    Output("data_table_tr", "data"),
    Output("data_table_tr", "columns"),
    Input("stored_data_tr", "data"),
    Input("plot_selector_tr", "value"),
    prevent_initial_call=True,
)
def populate_table(data, selected_plot):
    if not data:
        return [], []

    df = pl.read_parquet(io.BytesIO(base64.b64decode(data))).filter(
        pl.col("seq_id") == selected_plot
    )
    columns = [{"name": col, "id": col} for col in df.columns]
    return df.to_dicts(), columns


@callback(
    Output("data_table_tr", "selected_rows"),
    Output("data_table_tr", "selected_cells"),
    Output("data_table_tr", "active_cell"),
    Output("data_table_tr", "page_current"),
    Input("plot_content_tr", "clickData"),
    State("stored_data_tr", "data"),
    State("data_table_tr", "page_size"),
    prevent_initial_call=True,
)
def highlight_table_on_click(clickData, data, page_size):
    if not clickData or not data:
        return [], [], None, dash.no_update

    decoded_df = base64.b64decode(data)
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

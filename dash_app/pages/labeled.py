import dash
import dash_bootstrap_components as dbc
import polars as pl
import requests
from dash import Input, Output, State, callback, html
import io
import base64
from dash_app.components.forms import labeled_form
from dash_app.components.layouts import create_default_layout
from dash_app.utils.plots import get_options, create_plot

dash.register_page(__name__, path="/labeled", title="Labeled Data Analysis")

form = labeled_form()
layout = create_default_layout(
    form, "stored_data", "plot_selector", "plot_content", "error_toast", "success_toast"
)


@callback(
    Output("stored_data", "data"),
    Output("plot_selector", "options"),
    Input("submit", "n_clicks"),
    State("log_format", "value"),
    State("directory", "value"),
    State("detectors", "value"),
    State("enhancement", "value"),
    State("sequence", "value"),
    State("test_frac", "value"),
    prevent_initial_call=True,
)
def get_and_generate_dropdown(
    n_clicks, log_format, directory, detectors, enhancement, sequence, test_frac
):
    if n_clicks == 0:
        return dash.no_update, dash.no_update

    buffer = None
    try:
        response = requests.post(
            "http://localhost:5000/api/analyze",
            json={
                "dir_path": directory,
                "log_format": log_format,
                "models": detectors,
                "item_list_col": enhancement,
                "test_frac": test_frac,
                "seq": sequence,
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
    Output("plot_content", "figure"),
    Input("plot_selector", "value"),
    State("stored_data", "data"),
    prevent_initial_call=True,
)
def render_plot(selected_plot, data):
    if not data or not selected_plot:
        return html.Div("Select a plot to display.")

    decoded_df = base64.b64decode(data)
    df = pl.read_parquet(io.BytesIO(decoded_df))

    fig = create_plot(df, selected_plot)

    return fig

import dash
import dash_bootstrap_components as dbc
import polars as pl
import requests
from dash import Input, Output, State, callback, dcc, html
import io
import base64
from dash_app.components.form_inputs import (
    log_format_input,
    detectors_input,
    enhancement_input,
    sequence_input,
    train_data_input,
    test_data_input,
)

from dash_app.utils.plots import get_options, create_plot

dash.register_page(__name__, path="/manual-split", title="Manual Split Analysis")

plot_tr = html.Div(dcc.Graph(id="plot_area_tr"))
submit_btn_tr = dbc.Button("Analyze", id="submit_tr", n_clicks=0)

form_tr = dbc.Form(
    [
        dbc.Row(
            [
                log_format_input("log_format_tr"),
                train_data_input("train_data_tr"),
                test_data_input("test_data_tr"),
            ],
            class_name="mb-3",
        ),
        dbc.Row(
            [
                detectors_input("detectors_tr"),
                enhancement_input("enhancement_tr"),
                sequence_input("sequence_tr"),
            ],
            class_name="mb-3",
        ),
        dbc.Row(dbc.Col(submit_btn_tr, class_name="text-end")),
    ],
    class_name="border border-primary-subtle p-3",
)

layout = dbc.Container(
    [
        form_tr,
        dcc.Loading(
            type="circle",
            id="loading-default-2",
            children=[
                dcc.Store(id="stored_data_tr"),
                dcc.Dropdown(
                    id="plot_selector_tr",
                    placeholder="Select plot to display",
                    searchable=True,
                    className="dbc mt-3 border border-primary-subtle",
                ),
            ],
        ),
        dcc.Loading(
            type="default",
            children=[
                dcc.Graph(
                    id="plot_content_tr",
                    config={"responsive": True},
                    style={
                        "resize": "both",
                        "overflow": "auto",
                        "minHeight": "400px",
                        "minWidth": "600px",
                    },
                    className="dbc mt-3",
                ),
            ],
        ),
    ],
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
    State("sequence_tr", "value"),
    prevent_initial_call=True,
)
def get_and_generate_dropdown(
    n_clicks, log_format, train_data, test_data, detectors, enhancement, sequence
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

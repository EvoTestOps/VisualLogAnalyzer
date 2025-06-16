import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import polars as pl
import requests
from dash import Input, Output, State, callback, dcc, html
import io
import base64
from dash_app.components.form_inputs import (
    log_format_input,
    directory_input,
    detectors_input,
    enhancement_input,
    sequence_input,
    test_frac_input,
)

dash.register_page(__name__, path="/", title="home")

submit_btn = dbc.Button("Submit", id="submit", n_clicks=0, class_name="mb-3")
plot = html.Div(dcc.Graph(id="plot_area"))

form = dbc.Form(
    [
        dbc.Row(
            [log_format_input("log_format"), directory_input("directory")],
            class_name="mb-3",
        ),
        dbc.Row(
            [
                detectors_input("detectors"),
                enhancement_input("enhancement"),
                sequence_input("sequence"),
            ],
            class_name="mb-3",
        ),
        test_frac_input("test_frac"),
        submit_btn,
    ],
    class_name="border border-primary-subtle p-3 mb-3",
)

layout = dbc.Container(
    [
        form,
        dcc.Store(id="stored_data"),
        dcc.Dropdown(
            id="plot_selector", placeholder="Select plot to display", searchable=True
        ),
        html.Div(id="plot_content"),
    ]
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

        seq_ids = df["seq_id"].unique().to_list()[:5]
        options = [{"label": seq_id, "value": seq_id} for seq_id in seq_ids]

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
    Output("plot_content", "children"),
    Input("plot_selector", "value"),
    State("stored_data", "data"),
    prevent_initial_call=True,
)
def render_plot(selected_plot, data):
    if not data or not selected_plot:
        return html.Div("Select a plot to display.")

    decoded_df = base64.b64decode(data)
    df = pl.read_parquet(io.BytesIO(decoded_df))

    prediction_columns = [col for col in df.columns if "pred_ano_proba" in col]
    df = df.filter(pl.col("seq_id") == selected_plot).with_row_index()

    fig = px.scatter(df, x="index", y=prediction_columns[0])  # change later

    return dcc.Graph(figure=fig)

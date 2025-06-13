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

# layout = dbc.Container([form, plot])

layout = dbc.Container(
    [
        form,
        dcc.Store(id="stored_data"),
        dcc.Tabs(id="tabs_container", value=None),
        html.Div(id="tab_content"),
    ]
)


@callback(
    Output("stored_data", "data"),
    Output("tabs_container", "children"),
    Input("submit", "n_clicks"),
    State("log_format", "value"),
    State("directory", "value"),
    State("detectors", "value"),
    State("enhancement", "value"),
    State("sequence", "value"),
    State("test_frac", "value"),
    prevent_initial_call=True,
)
def get_and_generate_tabs(
    n_clicks, log_format, directory, detectors, enhancement, sequence, test_frac
):
    if n_clicks == 0:
        return dash.no_update, dash.no_update

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
        print(log_format, directory, detectors, enhancement, sequence, test_frac)
        response.raise_for_status()
        parquet_bytes = io.BytesIO(response.content)
        df = pl.read_parquet(parquet_bytes)

        seq_ids = df["seq_id"].unique().to_list()[:5]
        tabs = [dcc.Tab(label=seq_id, value=seq_id) for seq_id in seq_ids]
        try:
            df_json = df.write_json()
        except Exception as e:
            return {"error": str(e)}, [dcc.Tab(label="Error", value="error")]

        return df_json, tabs

    except Exception as e:
        return {"error": str(e)}, [dcc.Tab(label="Error", value="error")]


@callback(
    Output("tab_content", "children"),
    Input("tabs_container", "value"),
    State("stored_data", "data"),
    prevent_initial_call=True,
)
def render_tab(active_tab, data):
    if not data or not active_tab:
        return html.Div("No data or tab selected.")
    # if "error" in data.keys():
    #     return html.Div(f"Error: {data['error']}")

    df = pl.read_json(io.StringIO(data))

    prediction_columns = [col for col in df.columns if "pred_ano_proba" in col]
    df = df.filter(pl.col("seq_id") == active_tab).with_row_index()

    fig = px.scatter(df, x="index", y=prediction_columns[0])  # change later

    return dcc.Graph(figure=fig)


# @callback(
#     Output("plot_area", "figure"),
#     Input("submit", "n_clicks"),
#     State("log_format", "value"),
#     State("directory", "value"),
#     State("detectors", "value"),
#     State("enhancement", "value"),
#     State("sequence", "value"),
#     State("test_frac", "value"),
#     prevent_initial_call=True,
# )
# def update_plot(
#     n_clicks, log_format, directory, detectors, enhancement, sequence, test_frac
# ):
#     try:
#         response = requests.post(
#             "http://localhost:5000/api/analyze",
#             json={
#                 "dir_path": directory,
#                 "log_format": log_format,
#                 "models": detectors,
#                 "item_list_col": enhancement,
#                 "test_frac": test_frac,
#                 "seq": sequence,
#             },
#         )
#         response.raise_for_status()
#         parquet_bytes = io.BytesIO(response.content)
#         df = pl.read_parquet(parquet_bytes)

#         return px.scatter(title="OK")

#     except Exception as e:
#         return px.scatter(title=f"Error loading data: {e}")

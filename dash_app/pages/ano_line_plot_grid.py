import base64
import io

import dash
import dash_bootstrap_components as dbc
import polars as pl
from dash import Input, Output, State, callback, dcc, html
from PIL import Image

from dash_app.callbacks.callback_functions import make_api_call
from dash_app.components.forms import plot_grid_image_form
from dash_app.components.toasts import error_toast, success_toast
from dash_app.utils.plots import create_line_level_plot_minimal, get_options

dash.register_page(
    __name__,
    path_template="/analysis/ano-line-level/<analysis_id>/grid",
)


def layout(analysis_id=None, **kwargs):

    form = plot_grid_image_form("submit-grid", "files-to-include", "cols-to-include")
    base = [
        dbc.Row(html.H3("Multi-plot")),
        dbc.Row(form),
        success_toast("success-toast-grid"),
        error_toast("error-toast-grid"),
        dcc.Store(id="analysis-id-grid", data=analysis_id),
        dcc.Store(id="stored-data-grid"),
    ]

    image_preview = dbc.Row(
        dcc.Loading(
            type="default",
            children=[
                html.Div(
                    html.Div(id="image-preview-grid", className="m-3"),
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                    },
                ),
            ],
        ),
    )

    return [dbc.Container(base), dbc.Container(image_preview, fluid=True)]


@callback(
    Output("stored-data-grid", "data"),
    Output("error-toast-grid", "children"),
    Output("error-toast-grid", "is_open"),
    Input("analysis-id-grid", "data"),
)
def get_data(analysis_id):
    response, error = make_api_call({}, f"analyses/{analysis_id}", "GET")

    if error or response is None:
        return dash.no_update, str(error), True

    df = pl.read_parquet(io.BytesIO(response.content))

    buffer = io.BytesIO()
    df.write_parquet(buffer)
    buffer.seek(0)

    encoded_df = base64.b64encode(buffer.read()).decode("utf-8")

    return (encoded_df, dash.no_update, False)


@callback(
    Output("files-to-include", "options"),
    Output("cols-to-include", "options"),
    Output("error-toast-grid", "children", allow_duplicate=True),
    Output("error-toast-grid", "is_open", allow_duplicate=True),
    Input("stored-data-grid", "data"),
    prevent_initial_call=True,
)
def get_dropdown_options(encoded_df):
    if not encoded_df:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    decoded_df = base64.b64decode(encoded_df)
    df = pl.read_parquet(io.BytesIO(decoded_df))
    file_options = get_options(df)

    pred_columns = sorted([col for col in df.columns if "pred_ano_proba" in col])
    col_options = [{"label": col, "value": col} for col in pred_columns]

    return file_options, col_options, dash.no_update, False


@callback(
    Output("image-preview-grid", "children"),
    Output("error-toast-grid", "children", allow_duplicate=True),
    Output("error-toast-grid", "is_open", allow_duplicate=True),
    Output("success-toast-grid", "children", allow_duplicate=True),
    Output("success-toast-grid", "is_open", allow_duplicate=True),
    Input("submit-grid", "n_clicks"),
    State("stored-data-grid", "data"),
    State("files-to-include", "value"),
    State("cols-to-include", "value"),
    prevent_initial_call=True,
)
def generate_image(_, encoded_df, files_to_include, cols_to_include):
    if not encoded_df or not files_to_include or not cols_to_include:
        return dash.no_update, "Check your form inputs.", True, dash.no_update, False

    if len(files_to_include) > 8:
        return (
            dash.no_update,
            "Maximum of 8 files can be used.",
            True,
            dash.no_update,
            False,
        )

    decoded_df = base64.b64decode(encoded_df)
    df = pl.read_parquet(io.BytesIO(decoded_df))

    figs = [
        create_line_level_plot_minimal(df, seq_id, cols_to_include)
        for seq_id in files_to_include
    ]
    base64_img = _create_image(figs)

    img_element = html.Img(
        src=f"data:image/png;base64,{base64_img}",
        style={"width": "100%"},
    )

    return img_element, dash.no_update, False, "Image created", False


def _plot_to_pil_image(fig, width=600, height=400):
    img_bytes = fig.to_image(format="png", width=width, height=height)
    return Image.open(io.BytesIO(img_bytes))


def _get_grid_shape(n):
    if n == 1:
        return 1, 1
    elif n == 2:
        return 2, 1
    elif n <= 4:
        return 2, 2
    elif n <= 6:
        return 3, 2
    else:
        return 4, 2


def _create_image(figs):
    images = []
    for fig in figs:
        img = _plot_to_pil_image(fig)
        images.append(img)

    images = [_plot_to_pil_image(fig) for fig in figs]

    img_w, img_h = images[0].size
    cols, rows = _get_grid_shape(len(images))

    grid_img = Image.new("RGB", (img_w * cols, img_h * rows), color=(255, 255, 255))

    for idx, img in enumerate(images):
        row = idx // cols
        col = idx % cols
        grid_img.paste(img, (col * img_w, row * img_h))

    buffer = io.BytesIO()
    grid_img.save(buffer, format="PNG")
    buffer.seek(0)

    base64_img = base64.b64encode(buffer.read()).decode("utf-8")
    return base64_img

import dash
import dash_bootstrap_components as dbc
from dash import Dash, html

from dash_app.callbacks.color_switch_callback import color_switch_callback
from dash_app.components.layouts import create_root_layout

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"


def create_dash_app(server):
    dash_app = Dash(
        __name__,
        server=server,
        url_base_pathname="/dash/",
        use_pages=True,
        # pages_folder="dash_app/pages",
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc_css],
        # TODO: check if this can be removed later. Harder to detect undefined behaviour.
        suppress_callback_exceptions=True,
    )

    dash_app.layout = html.Div(
        [
            create_root_layout(),
            dash.page_container,
        ]
    )
    color_switch_callback()

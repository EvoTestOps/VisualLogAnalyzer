import dash
import dash_bootstrap_components as dbc
from dash import Dash, html

from dash_app.callbacks.color_switch_callback import color_switch_callback
from dash_app.components.layouts import create_root_layout
from dash_app.dash_config import DashConfig

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"


def create_dash_app(server):
    dash_app = Dash(
        __name__,
        server=server,
        url_base_pathname="/dash/",
        use_pages=True,
        # pages_folder="dash_app/pages",
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc_css],
    )

    dash_app.layout = html.Div(
        [
            create_root_layout(
                DashConfig.TASK_STORE_ID,
            ),
            dash.page_container,
        ]
    )
    color_switch_callback()

import dash
import dash_bootstrap_components as dbc
from dash import Dash, html
from flask import Flask

from server.api.routes import analyze_bp
from server.api.dash_redirects import dash_redirects_bp
from dash_app.callbacks.color_switch_callback import color_switch_callback
from dash_app.components.layouts import create_root_layout


dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

server = Flask(__name__)
server.register_blueprint(analyze_bp, url_prefix="/api")
server.register_blueprint(dash_redirects_bp)

dash_app = Dash(
    __name__,
    server=server,
    url_base_pathname="/dash/",
    use_pages=True,
    pages_folder="dash_app/pages",
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc_css],
)

dash_app.layout = html.Div(
    [
        create_root_layout(),
        dash.page_container,
    ]
)

color_switch_callback()


if __name__ == "__main__":
    server.run(debug=True)

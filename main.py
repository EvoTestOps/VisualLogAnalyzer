import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from flask import Flask

from api.routes import analyze_bp
from dash_app.components.color_mode_switch import color_mode_switch
from dash_app.callbacks.color_switch_callback import color_switch_callback
from dash_app.components.nav import nav


dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

server = Flask(__name__)
server.register_blueprint(analyze_bp, url_prefix="/api")

dash_app = Dash(
    __name__,
    server=server,
    url_base_pathname="/dash/",
    use_pages=True,
    pages_folder="dash_app/pages",
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc_css],
)

dash_app.layout = dbc.Container(
    [
        dbc.Row(
            [
                html.H1("Visual Log Analyzer", style={"textAlign": "center"}),
            ],
            class_name="p-3",
        ),
        dbc.Row(
            [
                dbc.Col(nav()),
                dbc.Col(),
                dbc.Col(color_mode_switch(), class_name="d-flex justify-content-end"),
            ]
        ),
        dash.page_container,
    ]
)

color_switch_callback()

if __name__ == "__main__":
    server.run(debug=True)

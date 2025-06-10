import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from flask import Flask

from api.analyze import analyze_bp

server = Flask(__name__)
server.register_blueprint(analyze_bp, url_prefix="/api/analyze")

dash_app = Dash(
    __name__,
    server=server,
    url_base_pathname="/dash/",
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

dash_app.layout = dbc.Container(
    [
        html.H1("Visual Log Analyzer"),
        html.Div([dcc.Location(id="url", refresh=False)]),
        dash.page_container,
    ]
)

if __name__ == "__main__":
    server.run(debug=True)

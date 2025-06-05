from dash import Dash, html
from flask import Flask

server = Flask(__name__)

from routes import main_routes

server.register_blueprint(main_routes)

dash_app = Dash(server=server, url_base_pathname="/dash/")

dash_app.layout = html.Div(
    [
        html.H1("Visual Log Analyzer"),
    ]
)

if __name__ == "__main__":
    server.run(debug=True)

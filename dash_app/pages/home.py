import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", title="Home")

layout = dbc.Container(html.H1("Nothing here yet."))

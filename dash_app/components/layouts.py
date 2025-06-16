import dash_bootstrap_components as dbc
from dash import dcc, html


def create_default_layout(form, stored_data_id, plot_selector_id, plot_content_id):

    form_row = dbc.Row(form)

    plot_selector_row = dbc.Row(
        dcc.Loading(
            type="circle",
            children=[
                dcc.Store(id=stored_data_id),
                dcc.Dropdown(
                    id=plot_selector_id,
                    placeholder="Select plot to display",
                    searchable=True,
                    className="dbc mt-3 border border-primary-subtle",
                ),
            ],
        ),
    )

    plot_row = dbc.Row(
        dcc.Loading(
            type="default",
            children=[
                html.Div(
                    dcc.Graph(
                        id=plot_content_id,
                        config={"responsive": True},
                        style={
                            "resize": "both",
                            "overflow": "auto",
                            "minHeight": "500px",
                            "minWidth": "600px",
                            "width": "90%",
                        },
                        className="dbc mt-3 ps-4 pe-4",
                    ),
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                        "overflow": "visible",
                    },
                ),
            ],
        ),
    )

    layout = [
        dbc.Container([form_row, plot_selector_row]),
        dbc.Container(plot_row, fluid=True),
    ]

    return layout

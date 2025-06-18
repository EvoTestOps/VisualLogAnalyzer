import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table


def create_default_layout(
    form,
    stored_data_id,
    plot_selector_id,
    plot_content_id,
    error_toast_id,
    success_toast_id,
):

    form_row = dbc.Row(form)

    error_toast = dbc.Row(
        dbc.Toast(
            id=error_toast_id,
            header="Error",
            icon="danger",
            is_open=False,
            dismissable=True,
            duration=15000,
            style={"position": "fixed", "top": 40, "right": 10, "width": 400},
        ),
    )

    success_toast = dbc.Row(
        dbc.Toast(
            id=success_toast_id,
            header="Success",
            icon="success",
            is_open=False,
            dismissable=True,
            duration=10000,
            style={"position": "fixed", "top": 40, "right": 10, "width": 400},
        ),
    )

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
                        # style={
                        #     "resize": "both",
                        #     "overflow": "auto",
                        #     "minHeight": "500px",
                        #     "minWidth": "600px",
                        #     "width": "90%",
                        # },
                        style={
                            "display": "none",
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

    data_table_row = dbc.Row(
        html.Div(
            dash_table.DataTable(
                id="data_table_tr",
                row_selectable="single",
                selected_rows=[],
                active_cell=None,
                selected_cells=[],
                fixed_rows={"headers": True},
                style_table={
                    "overflowY": "auto",
                    "overflowX": "auto",
                    "height": 600,
                },
                style_cell={
                    "textAlign": "left",
                    "minWidth": "100px",
                },
                style_header={
                    "whiteSpace": "normal",
                    "height": "auto",
                    "textAlign": "left",
                },
                page_action="native",
                page_current=0,
                page_size=250,
            ),
        ),
        className="dbc mt-3 ms-4 me-4",
    )

    layout = [
        dbc.Container([form_row, plot_selector_row, error_toast, success_toast]),
        dbc.Container(plot_row, fluid=True),
        dbc.Container(data_table_row, fluid=True),
    ]

    return layout

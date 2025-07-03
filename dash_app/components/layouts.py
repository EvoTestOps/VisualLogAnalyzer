import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash_app.components.color_mode_switch import color_mode_switch
from dash_app.components.nav import nav
from dash_app.components.toasts import error_toast, success_toast


# TODO: naming is all over the place at the moment
def create_root_layout():
    return dbc.Container(
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2(
                            "Visual Log Analyzer",
                            style={"textAlign": "center"},
                        ),
                    ],
                    class_name="p-3",
                ),
                dbc.Col(nav(), width=6, class_name="d-flex align-items-center"),
                dbc.Col(
                    color_mode_switch(),
                    class_name="d-flex justify-content-end align-items-center",
                ),
            ],
        ),
    )


def create_default_layout(
    form,
    stored_data_id,
    plot_selector_id,
    plot_content_id,
    error_toast_id,
    success_toast_id,
    datatable_id,
):

    form_row = dbc.Row(form)

    error_toast_row = dbc.Row(error_toast(error_toast_id))

    success_toast_row = dbc.Row(success_toast(success_toast_id))

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
                id=datatable_id,
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
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                    "whiteSpace": "nowrap",
                    "textAlign": "left",
                    "minWidth": "100px",
                },
                page_action="native",
                page_current=0,
                page_size=250,
            ),
        ),
        className="dbc mt-3 ms-4 me-4",
    )

    layout = [
        dbc.Container(
            [form_row, plot_selector_row, error_toast_row, success_toast_row]
        ),
        dbc.Container(plot_row, fluid=True),
        dbc.Container(data_table_row, fluid=True),
    ]

    return layout


def create_unique_term_count_layout(
    form, plot_content_id, error_toast_id, success_toast_id
):

    form_row = dbc.Row(form)

    error_toast_row = dbc.Row(error_toast(error_toast_id))
    success_toast_row = dbc.Row(success_toast(success_toast_id))

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

    layout = [
        dbc.Container([form_row, error_toast_row, success_toast_row]),
        dbc.Container(plot_row, fluid=True),
    ]

    return layout


def create_ano_run_level_layout(
    form,
    error_toast_id,
    success_toast_id,
    datatable_id,
):

    form_row = dbc.Row(form)

    error_toast_row = dbc.Row(error_toast(error_toast_id))

    success_toast_row = dbc.Row(success_toast(success_toast_id))

    data_table_row = dbc.Row(
        dcc.Loading(
            type="default",
            children=html.Div(
                dash_table.DataTable(
                    id=datatable_id,
                    sort_action="native",
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
                        "overflow": "hidden",
                        "textOverflow": "ellipsis",
                        "whiteSpace": "nowrap",
                        "textAlign": "left",
                        "minWidth": "100px",
                    },
                    page_action="native",
                    page_current=0,
                    page_size=250,
                ),
            ),
        ),
        className="dbc mt-3 ms-4 me-4",
    )

    layout = [
        dbc.Container([form_row, error_toast_row, success_toast_row]),
        dbc.Container(data_table_row, fluid=True),
    ]

    return layout


def create_project_layout(group_id, error_toast_id, success_toast_id):
    error_toast_row = dbc.Row(error_toast(error_toast_id))
    success_toast_row = dbc.Row(success_toast(success_toast_id))

    group_row = dbc.Row(dbc.ListGroup(id=group_id), class_name="mb-3 mt-3")

    layout = [dbc.Container([group_row, error_toast_row, success_toast_row])]

    return layout

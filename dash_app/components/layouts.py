import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from dash_app.components.color_mode_switch import color_mode_switch
from dash_app.components.form_inputs import submit_button
from dash_app.components.forms import project_settings_form
from dash_app.components.nav import crate_analysis_nav, nav
from dash_app.components.toasts import error_toast, success_toast


def create_root_layout():
    return dbc.Container(
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2(
                            "Visual Log Analyzer",
                        ),
                        nav(),
                    ],
                    class_name="d-flex align-items-center",
                    width="auto",
                ),
                dbc.Col(
                    color_mode_switch(),
                    class_name="d-flex justify-content-end align-items-center",
                ),
            ],
            class_name="border-bottom border-primary mb-3 mt-3",
        ),
    )


def create_ano_line_level_result_layout(
    stored_data_id,
    plot_selector_id,
    plot_content_id,
    datatable_id,
    metadata_table_id,
    error_toast_id,
    success_toast_id,
):

    error_toast_row = dbc.Row(error_toast(error_toast_id))
    success_toast_row = dbc.Row(success_toast(success_toast_id))

    metadata_row = dbc.Row(dbc.Table(id=metadata_table_id, hover=True, responsive=True))

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
        dbc.Container([metadata_row, error_toast_row, success_toast_row]),
        dbc.Container(plot_selector_row),
        dbc.Container(plot_row, fluid=True),
        dbc.Container(data_table_row, fluid=True),
    ]

    return layout


def create_datatable_layout(
    datatable_id,
    metadata_table_id,
    error_toast_id,
    success_toast_id,
):

    metadata_row = dbc.Row(dbc.Table(id=metadata_table_id, hover=True, responsive=True))

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
                        "fontWeight": "bold",
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
        dbc.Container([metadata_row, error_toast_row, success_toast_row]),
        dbc.Container(data_table_row, fluid=True),
    ]

    return layout


def create_high_level_viz_layout(
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


def create_home_layout(
    form, group_id, error_toast_id, success_toast_id, collapse_id, open_btn_id
):
    error_toast_row = dbc.Row(error_toast(error_toast_id))
    success_toast_row = dbc.Row(success_toast(success_toast_id))

    group_row = dbc.Row(dbc.ListGroup(id=group_id), class_name="mb-3 mt-3")

    open_btn = submit_button(open_btn_id, "Create a new project")

    form_row = dbc.Row(
        [
            html.Div(
                [
                    dbc.Collapse(
                        dbc.Card(form, body=True),
                        id=collapse_id,
                        is_open=False,
                        class_name="mt-3",
                    ),
                ]
            ),
        ]
    )

    layout = [
        dbc.Container(
            dbc.Row(
                [
                    dbc.Col(html.H3("Projects", className="mb-0"), class_name="p-0"),
                    dbc.Col(open_btn, class_name="text-end"),
                ],
            )
        ),
        dbc.Container(form_row),
        dbc.Container([group_row, error_toast_row, success_toast_row]),
    ]

    return layout


def create_project_layout(
    group_id,
    project_name_id,
    project_id,
    nav_id,
    error_toast_id,
    success_toast_id,
    settings_submit_id,
    match_filenames_id,
    color_by_directory_id,
    tasks_count_id,
):

    error_toast_row = dbc.Row(error_toast(error_toast_id))
    success_toast_row = dbc.Row(success_toast(success_toast_id))

    header_row = dbc.Row(
        [
            dbc.Col(
                html.H3(id=project_name_id, className="mb-0"), width=4, class_name="p-0"
            ),
            dbc.Col(html.H3("Analyses", className="text-end mb-0"), width=4),
        ]
    )

    group_col = dbc.Col(
        dbc.ListGroup(id=group_id), class_name="mb-3 mt-3 ps-0 ms-0", width=8
    )

    nav_col = dbc.Col(
        [
            crate_analysis_nav(project_id, nav_id),
            html.Div(
                [
                    html.H4("Settings"),
                    dbc.Card(
                        project_settings_form(
                            settings_submit_id,
                            match_filenames_id,
                            color_by_directory_id,
                        ),
                        body=True,
                    ),
                ],
                className="mt-3",
            ),
            html.Div(id=tasks_count_id, className="mt-3"),
        ],
        class_name="pt-3",
    )

    layout = [
        dbc.Container(
            [
                error_toast_row,
                success_toast_row,
                header_row,
                dbc.Row([group_col, nav_col]),
            ]
        ),
    ]

    return layout


def create_high_level_viz_result_layout(
    plot_content_id, metadata_table_id, error_toast_id, success_toast_id
):
    error_toast_row = dbc.Row(error_toast(error_toast_id))
    success_toast_row = dbc.Row(success_toast(success_toast_id))

    table_row = dbc.Row(dbc.Table(id=metadata_table_id, hover=True, responsive=True))

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
        dbc.Container([table_row, error_toast_row, success_toast_row]),
        dbc.Container(plot_row, fluid=True),
    ]

    return layout


def create_result_base_layout(title, analysis_id, project_link_id, analysis_store_id):
    return [
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(html.H3(title)),
                        dbc.Col(
                            dcc.Link(
                                "Back to project",
                                id=project_link_id,
                                href="/dash/project",
                            ),
                            className="d-flex justify-content-end",
                        ),
                    ],
                    class_name="border-bottom border-secondary-subtle",
                ),
                dcc.Store(id=analysis_store_id, data=analysis_id),
            ],
        )
    ]

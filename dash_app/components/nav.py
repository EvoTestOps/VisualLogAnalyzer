from dash import html
import dash_bootstrap_components as dbc


def nav():
    return dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink("Home", href="/dash/")),
            dbc.DropdownMenu(
                [
                    dbc.DropdownMenuItem(
                        "Directory Level", href="/dash/ano-directory-level"
                    ),
                    dbc.DropdownMenuItem("File Level", href="/dash/ano-file-level"),
                    dbc.DropdownMenuItem("Line Level", href="/dash/ano-line-level"),
                ],
                label="Anomaly Detection",
                nav=True,
            ),
            dbc.DropdownMenu(
                [
                    dbc.DropdownMenuItem(
                        "Directory Level", href="/dash/directory-level-visualisations"
                    ),
                    dbc.DropdownMenuItem(
                        "File Level", href="/dash/file-level-visualisations"
                    ),
                ],
                label="High level Visualisations",
                nav=True,
            ),
            dbc.DropdownMenu(
                [
                    dbc.DropdownMenuItem(
                        "Directory Level", href="/dash/distance-directory-level"
                    ),
                    dbc.DropdownMenuItem(
                        "File Level", href="/dash/distance-file-level"
                    ),
                ],
                label="Log Distance",
                nav=True,
            ),
        ],
        class_name="h5",
    )


def crate_analysis_nav(project_id, nav_id):
    return html.Div(
        [
            dbc.Label(html.H4("Create a new analysis"), html_for=nav_id),
            dbc.Nav(
                [
                    dbc.DropdownMenu(
                        [
                            dbc.DropdownMenuItem(
                                "Directory Level",
                                href=f"/dash/analysis/ano-directory-level/create?project_id={project_id}",
                            ),
                            dbc.DropdownMenuItem(
                                "File Level",
                                href=f"/dash/analysis/ano-file-level/create?project_id={project_id}",
                            ),
                            dbc.DropdownMenuItem(
                                "Line Level",
                                href="/dash/analysis/ano-line-level/create?project_id={project_id}",
                            ),
                        ],
                        label="Anomaly Detection",
                        nav=True,
                    ),
                    dbc.DropdownMenu(
                        [
                            dbc.DropdownMenuItem(
                                "Directory Level",
                                href=f"/dash/analysis/directory-level-visualisations/create?project_id={project_id}",
                            ),
                            dbc.DropdownMenuItem(
                                "File Level",
                                href=f"/dash/analysis/file-level-visualisations/create?project_id={project_id}",
                            ),
                        ],
                        label="High level Visualisations",
                        nav=True,
                    ),
                    dbc.DropdownMenu(
                        [
                            dbc.DropdownMenuItem(
                                "Directory Level",
                                href=f"/dash/analysis/distance-directory-level/create?project_id={project_id}",
                            ),
                            dbc.DropdownMenuItem(
                                "File Level",
                                href=f"/dash/analysis/distance-file-level/create?project_id={project_id}",
                            ),
                        ],
                        label="Log Distance",
                        nav=True,
                    ),
                ],
                id=nav_id,
                vertical=True,
                class_name="h5",
            ),
        ]
    )

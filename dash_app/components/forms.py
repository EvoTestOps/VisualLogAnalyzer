import dash_bootstrap_components as dbc
from dash import dcc

from dash_app.components.form_inputs import (
    detectors_unsupervised_input,
    directory_dropdown_input,
    enhancement_input,
    files_filter_input,
    mask_input,
    name_input,
    runs_filter_input,
    submit_button,
    target_run_input,
    terms_files_input,
    terms_umap_input,
    vectorizer_input,
    match_file_names_input,
    color_by_directory_input,
    redirect_to_results_input,
    line_display_mode_input,
    manual_filename_input,
    files_to_include_input,
    columns_to_include_input,
    analysis_name_input,
    base_path_input,
)


def test_train_form(
    submit_id,
    train_data_id,
    test_data_id,
    detectors_id,
    enhancement_id,
    runs_filter_id,
    runs_filter_train_id,
    mask_input_id,
    vectorizer_id,
    results_redirect_id,
    analysis_name_id,
):
    submit_btn_tr = submit_button(submit_id, "Analyze")

    if results_redirect_id:
        submit_row = dbc.Row(
            [
                redirect_to_results_input(results_redirect_id),
                dbc.Col(submit_btn_tr, class_name="text-end"),
            ]
        )
    else:
        submit_row = dbc.Row(dbc.Col(submit_btn_tr, class_name="text-end"))

    form_tr = dbc.Form(
        [
            dbc.Row(analysis_name_input(analysis_name_id), class_name="mb-3"),
            dbc.Row(
                [
                    directory_dropdown_input(train_data_id, "Train data directory"),
                    directory_dropdown_input(test_data_id, "Test data directory"),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    runs_filter_input(
                        id=runs_filter_train_id,
                        label="Directories to include in train data",
                    ),
                    runs_filter_input(runs_filter_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    detectors_unsupervised_input(detectors_id),
                    vectorizer_input(vectorizer_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    enhancement_input(enhancement_id),
                    mask_input(mask_input_id),
                ],
                class_name="mb-3",
            ),
            submit_row,
            # dbc.Row(dbc.Col(submit_btn_tr, class_name="text-end")),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form_tr


def test_train_file_level_form(
    submit_id,
    train_data_id,
    test_data_id,
    detectors_id,
    enhancement_id,
    runs_filter_id,
    runs_filter_train_id,
    mask_input_id,
    vectorizer_id,
    results_redirect_id,
    analysis_name_id,
    manual_filenames=False,
):
    submit_btn_tr = submit_button(submit_id, "Analyze")

    form = dbc.Form(
        [
            dbc.Row(analysis_name_input(analysis_name_id), class_name="mb-3"),
            dbc.Row(
                [
                    directory_dropdown_input(train_data_id, "Train data directory"),
                    directory_dropdown_input(test_data_id, "Test data directory"),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    detectors_unsupervised_input(detectors_id),
                    enhancement_input(enhancement_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    mask_input(mask_input_id),
                    vectorizer_input(vectorizer_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                dcc.Loading(
                    type="circle",
                    overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                    children=[
                        files_filter_input(
                            runs_filter_train_id,
                            label="Files to include in train data",
                            manual=manual_filenames,
                        ),
                    ],
                ),
                class_name="mb-3",
            ),
            dbc.Row(
                dcc.Loading(
                    type="circle",
                    overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                    children=[
                        files_filter_input(runs_filter_id, manual=manual_filenames),
                    ],
                ),
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    redirect_to_results_input(results_redirect_id),
                    dbc.Col(submit_btn_tr, class_name="text-end"),
                ]
            ),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form


def directory_level_viz_form(
    submit_id,
    directory_id,
    analysis_type_id,
    mask_id,
    vectorizer_id,
    results_redirect_id,
    analysis_name_id,
):
    submit_btn_ut = submit_button(submit_id, "Analyze")

    form = dbc.Form(
        [
            dbc.Row(analysis_name_input(analysis_name_id), class_name="mb-3"),
            dbc.Row(
                [
                    directory_dropdown_input(directory_id),
                    terms_files_input(analysis_type_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    mask_input(mask_id),
                    vectorizer_input(vectorizer_id),
                ],
            ),
            dbc.FormText(
                "Mask type and vectorizer are optional inputs for UMAP analysis.",
                color="secondary",
            ),
            dbc.Row(
                [
                    redirect_to_results_input(results_redirect_id),
                    dbc.Col(submit_btn_ut, class_name="text-end"),
                ]
            ),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form


def file_level_viz_form(
    submit_id,
    directory_id,
    analysis_type_id,
    mask_id,
    vectorizer_id,
    results_redirect_id,
    analysis_name_id,
):
    submit_btn_ut_file = submit_button(submit_id, "Analyze")

    form = dbc.Form(
        [
            dbc.Row(analysis_name_input(analysis_name_id), class_name="mb-3"),
            dbc.Row(
                [
                    directory_dropdown_input(directory_id),
                    terms_umap_input(analysis_type_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    mask_input(mask_id),
                    vectorizer_input(vectorizer_id),
                ],
            ),
            dbc.FormText(
                "Mask type and vectorizer are optional inputs for UMAP analysis.",
                color="secondary",
            ),
            dbc.Row(
                [
                    redirect_to_results_input(results_redirect_id),
                    dbc.Col(submit_btn_ut_file, class_name="text-end"),
                ]
            ),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form


def distance_run_level_form(
    submit_id,
    directory_id,
    enhancement_id,
    target_run_id,
    runs_filter_id,
    mask_id,
    vectorizer_id,
    results_redirect_id,
    analysis_name_id,
):
    submit_btn = submit_button(submit_id, "Analyze")

    form = dbc.Form(
        [
            dbc.Row(analysis_name_input(analysis_name_id), class_name="mb-3"),
            dbc.Row(
                [
                    directory_dropdown_input(directory_id),
                    enhancement_input(enhancement_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [mask_input(mask_id), vectorizer_input(vectorizer_id)],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    target_run_input(target_run_id),
                    runs_filter_input(runs_filter_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    redirect_to_results_input(results_redirect_id),
                    dbc.Col(submit_btn, class_name="text-end"),
                ]
            ),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form


def distance_file_level_form(
    submit_id,
    directory_id,
    enhancement_id,
    target_run_id,
    runs_filter_id,
    mask_id,
    vectorizer_id,
    results_redirect_id,
    analysis_name_id,
    manual_filenames=False,
):
    submit_btn = submit_button(submit_id, "Analyze")

    form = dbc.Form(
        [
            dbc.Row(analysis_name_input(analysis_name_id), class_name="mb-3"),
            dbc.Row(
                [
                    directory_dropdown_input(directory_id),
                    enhancement_input(enhancement_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    mask_input(mask_id),
                    vectorizer_input(vectorizer_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                dcc.Loading(
                    type="circle",
                    overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                    children=[
                        dbc.Row(
                            target_run_input(target_run_id, manual=manual_filenames),
                            class_name="mb-3",
                        ),
                        dbc.Row(
                            runs_filter_input(runs_filter_id, manual=manual_filenames),
                            class_name="mb-3",
                        ),
                    ],
                )
            ),
            dbc.Row(
                [
                    redirect_to_results_input(results_redirect_id),
                    dbc.Col(submit_btn, class_name="text-end"),
                ]
            ),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form


def project_form(submit_id, name_id, base_path_id):
    submit_btn = submit_button(submit_id, "Create")
    form = dbc.Form(
        [
            dbc.Row(
                [
                    dbc.Col(name_input((name_id))),
                    dbc.Col(base_path_input((base_path_id))),
                    dbc.Col(
                        submit_btn,
                        class_name="d-flex justify-content-end align-middle align-items-end",
                    ),
                ]
            )
        ]
    )

    return form


def project_settings_form(
    submit_id,
    match_filenames_id,
    color_by_directory_id,
    line_display_mode_id,
    manual_filename_id,
):
    submit_btn = submit_button(submit_id, "Apply")
    form = dbc.Form(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            match_file_names_input(match_filenames_id),
                            color_by_directory_input(color_by_directory_id),
                            manual_filename_input(manual_filename_id),
                            line_display_mode_input(line_display_mode_id),
                        ],
                        width=8,
                    ),
                    dbc.Col(
                        submit_btn,
                        class_name="d-flex justify-content-end align-middle align-items-end",
                    ),
                ]
            )
        ],
    )
    return form


def plot_grid_image_form(submit_id, files_to_include_id, columns_to_include_id):
    submit_btn = submit_button(submit_id, "Create")
    form = dbc.Form(
        [
            dcc.Loading(
                type="circle",
                delay_show=400,
                overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                children=[
                    dbc.Row(
                        files_to_include_input(files_to_include_id), class_name="mb-3"
                    ),
                    dbc.Row(
                        columns_to_include_input(columns_to_include_id),
                        class_name="mb-3",
                    ),
                ],
            ),
            dbc.Row(
                dbc.Col(submit_btn, class_name="text-end"),
            ),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form

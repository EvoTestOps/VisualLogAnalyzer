import dash_bootstrap_components as dbc
from dash_app.components.form_inputs import (
    log_format_input,
    directory_input,
    detectors_unsupervised_input,
    enhancement_input,
    submit_button,
    train_data_input,
    test_data_input,
    runs_filter_input,
    terms_files_input,
    terms_umap_input,
    files_filter_input,
    target_run_input,
    mask_input,
)


def test_train_form(
    submit_id,
    log_format_id,
    train_data_id,
    test_data_id,
    detectors_id,
    enhancement_id,
    runs_filter_id,
    mask_input_id,
):
    submit_btn_tr = submit_button(submit_id, "Analyze")

    form_tr = dbc.Form(
        [
            dbc.Row(
                [
                    log_format_input(log_format_id),
                    train_data_input(train_data_id),
                    test_data_input(test_data_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    detectors_unsupervised_input(detectors_id),
                    runs_filter_input(runs_filter_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    enhancement_input(enhancement_id),
                    mask_input(mask_input_id),
                ]
            ),
            dbc.Row(dbc.Col(submit_btn_tr, class_name="text-end")),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form_tr


def test_train_file_level_form(
    submit_id,
    log_format_id,
    train_data_id,
    test_data_id,
    detectors_id,
    enhancement_id,
    files_filter_id,
    mask_input_id,
):
    submit_btn_tr = submit_button(submit_id, "Analyze")

    form = dbc.Form(
        [
            dbc.Row(
                [
                    log_format_input(log_format_id),
                    train_data_input(train_data_id),
                    test_data_input(test_data_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    detectors_unsupervised_input(detectors_id),
                    enhancement_input(enhancement_id),
                    mask_input(mask_input_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    files_filter_input(files_filter_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(dbc.Col(submit_btn_tr, class_name="text-end")),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form


def unique_terms_form():
    submit_btn_ut = submit_button("submit_ut", "Analyze")

    form = dbc.Form(
        [
            dbc.Row(
                [
                    directory_input("directory_ut"),
                    terms_files_input("terms_files_ut"),
                ],
                class_name="mb-3",
            ),
            dbc.Row(dbc.Col(submit_btn_ut, class_name="text-end")),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form


def unique_terms_by_file_form():
    submit_btn_ut_file = submit_button("submit_ut_file", "Analyze")

    form = dbc.Form(
        [
            dbc.Row(
                [
                    directory_input("directory_ut_file"),
                    terms_umap_input("terms_umap_ut_file"),
                ],
                class_name="mb-3",
            ),
            dbc.Row(dbc.Col(submit_btn_ut_file, class_name="text-end")),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form


def distance_run_level_form(
    submit_id, directory_id, enhancement_id, target_run_id, runs_filter_id
):
    submit_btn = submit_button(submit_id, "Analyze")

    form = dbc.Form(
        [
            dbc.Row(
                [
                    directory_input(directory_id),
                    enhancement_input(enhancement_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    target_run_input(target_run_id),
                    runs_filter_input(runs_filter_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(dbc.Col(submit_btn, class_name="text-end")),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form


def distance_file_level_form(
    submit_id, directory_id, enhancement_id, target_run_id, runs_filter_id
):
    submit_btn = submit_button(submit_id, "Analyze")

    form = dbc.Form(
        [
            dbc.Row(
                [
                    directory_input(directory_id),
                    enhancement_input(enhancement_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    target_run_input(target_run_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    runs_filter_input(runs_filter_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(dbc.Col(submit_btn, class_name="text-end")),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form

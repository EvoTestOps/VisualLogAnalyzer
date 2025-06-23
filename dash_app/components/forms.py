import dash_bootstrap_components as dbc
from dash_app.components.form_inputs import (
    log_format_input,
    directory_input,
    detectors_input,
    detectors_unsupervised_input,
    enhancement_input,
    sequence_input,
    test_frac_input,
    submit_button,
    train_data_input,
    test_data_input,
    runs_filter_input,
    terms_files_input,
    terms_umap_input,
)


# TODO: Currently hardcoded id values
def labeled_form():
    submit_btn = submit_button("submit", "Analyze")

    form = dbc.Form(
        [
            dbc.Row(
                [log_format_input("log_format"), directory_input("directory")],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    detectors_input("detectors"),
                    enhancement_input("enhancement"),
                    sequence_input("sequence"),
                ],
                class_name="mb-3",
            ),
            test_frac_input("test_frac"),
            dbc.Row(dbc.Col(submit_btn, class_name="text-end")),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form


def test_train_form(
    submit_id,
    log_format_id,
    train_data_id,
    test_data_id,
    detectors_id,
    enhancement_id,
    runs_filter_id,
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
                    enhancement_input(enhancement_id),
                    runs_filter_input(runs_filter_id),
                ],
                class_name="mb-3",
            ),
            dbc.Row(dbc.Col(submit_btn_tr, class_name="text-end")),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form_tr


def unique_terms_form():
    submit_btn_ut = submit_button("submit_ut", "Analyze")

    form_tr = dbc.Form(
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

    return form_tr


def unique_terms_by_file_form():
    submit_btn_ut_file = submit_button("submit_ut_file", "Analyze")

    form_tr = dbc.Form(
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

    return form_tr

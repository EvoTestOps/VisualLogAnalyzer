import pytest
from unittest.mock import MagicMock, patch

import server.analysis.analysis_runners as ar


# Test data paths
HIDDEN_GROUP = "./tests/datasets/hidden_group_1"
LABELED = "./tests/datasets/labeled"
ONLY_CORRECT_CASES = "./tests/datasets/only_correct_cases"


@patch("server.analysis.utils.analysis_helpers._add_result")
def test_run_file_count_valid_inputs(mock_add_result):
    mock_add_result.return_value = 42

    result = ar.run_file_count_analysis(project_id=123, directory_path=LABELED)

    assert result["id"] == 42
    assert result["type"] == "directory-level-visualisations"


@patch("server.analysis.utils.analysis_helpers._add_result")
def test_async_run_file_counts_invalid_path(mock_add_result):
    mock_add_result.return_value = 42
    invalid_path = ".tests/datasets/this-does-not-exists"

    with pytest.raises(FileNotFoundError):
        ar.run_file_count_analysis(project_id=123, directory_path=invalid_path)


@patch("server.analysis.utils.analysis_helpers._add_result")
def test_run_umap_analysis_file_level_valid_inputs(mock_add_result):
    mock_add_result.return_value = 6

    result = ar.run_umap_analysis(
        project_id=7,
        directory_path=HIDDEN_GROUP,
        item_list_col="e_words",
        file_level=True,
        vectorizer="count",
        mask_type="myllari",
    )

    assert result["id"] == 6
    assert result["type"] == "file-level-visualisations"


@patch("server.analysis.utils.analysis_helpers._add_result")
def test_run_umap_analysis_directory_level_valid_inputs(mock_add_result):
    mock_add_result.return_value = 6

    result = ar.run_umap_analysis(
        project_id=7,
        directory_path=HIDDEN_GROUP,
        item_list_col="e_words",
        file_level=False,
        vectorizer="count",
        mask_type="myllari",
    )

    assert result["id"] == 6
    assert result["type"] == "directory-level-visualisations"


@patch("server.analysis.utils.analysis_helpers._add_result")
def test_run_umap_analysis_file_level_mask_none(mock_add_result):
    mock_add_result.return_value = 7

    result = ar.run_umap_analysis(
        project_id=7,
        directory_path=HIDDEN_GROUP,
        item_list_col="e_words",
        file_level=True,
        vectorizer="count",
        mask_type=None,
    )

    assert result["id"] == 7
    assert result["type"] == "file-level-visualisations"


@patch("server.analysis.utils.analysis_helpers._add_result")
def test_run_umap_analysis_file_level_invalid_vectorizer(mock_add_result):
    mock_add_result.return_value = 7

    with pytest.raises(ValueError):
        ar.run_umap_analysis(
            project_id=7,
            directory_path=HIDDEN_GROUP,
            item_list_col="e_words",
            file_level=True,
            vectorizer="vec",
            mask_type="myllari",
        )


@patch("server.analysis.utils.analysis_helpers._add_result")
def test_run_unique_terms_analysis_valid_inputs(mock_add_result):
    mock_add_result.return_value = 50

    result = ar.run_unique_terms_analysis(
        project_id=1, directory_path=LABELED, item_list_col="e_words", file_level=False
    )

    assert result["id"] == 50
    assert result["type"] == "directory-level-visualisations"


@patch("server.analysis.utils.analysis_helpers._add_result")
def test_run_unique_terms_analysis_invalid_item_list_col(mock_add_result):
    mock_add_result.return_value = 50

    with pytest.raises(ValueError):
        ar.run_unique_terms_analysis(
            project_id=1,
            directory_path=LABELED,
            item_list_col="bad_col",
            file_level=False,
        )


@patch("server.analysis.analysis_runners.store_and_format_result")
@patch("server.analysis.analysis_runners.unique_terms_count_by_file")
@patch("server.analysis.analysis_runners.unique_terms_count_by_run")
@patch("server.analysis.analysis_runners.load_data")
def test_run_unique_terms_analysis_directory_level(
    mock_load_data, mock_count_by_run, mock_count_by_file, mock_store_result
):

    mock_load_data.return_value = "dummy_df"
    mock_count_by_run.return_value = {"some": "result"}
    mock_store_result.return_value = {"id": 1, "type": "directory-level-visualisations"}

    _ = ar.run_unique_terms_analysis(
        project_id=123,
        directory_path="some/path",
        item_list_col="field",
        file_level=False,
    )

    mock_count_by_run.assert_called_once_with("dummy_df", "field")
    mock_count_by_file.assert_not_called()

    mock_store_result.assert_called_once()


@patch("server.analysis.analysis_runners.store_and_format_result")
@patch("server.analysis.analysis_runners.unique_terms_count_by_file")
@patch("server.analysis.analysis_runners.unique_terms_count_by_run")
@patch("server.analysis.analysis_runners.load_data")
def test_run_unique_terms_analysis_file_level(
    mock_load_data, mock_count_by_run, mock_count_by_file, mock_store_result
):

    mock_load_data.return_value = "dummy_df"
    mock_count_by_file.return_value = {"some": "result"}
    mock_store_result.return_value = {"id": 2, "type": "file-level-visualisations"}

    _ = ar.run_unique_terms_analysis(
        project_id=321,
        directory_path="some/path",
        item_list_col="field",
        file_level=True,
    )

    mock_count_by_file.assert_called_once_with("dummy_df", "field")
    mock_count_by_run.assert_not_called()

    mock_store_result.assert_called_once()


@patch("server.analysis.analysis_runners.Settings")
@patch("server.analysis.utils.analysis_helpers._add_result")
def test_run_log_distance_analysis_directory_level_valid_inputs(
    mock_add_result, mock_settings_class
):

    mock_settings = MagicMock()
    mock_settings.match_filenames = False
    mock_settings_class.query.filter_by.return_value.first_or_404.return_value = (
        mock_settings
    )

    mock_add_result.return_value = 6

    result = ar.run_log_distance_analysis(
        project_id=7,
        directory_path=LABELED,
        target_run="./tests/datasets/labeled/correct_1/light-oauth2-oauth2-code-1.log",
        comparison_runs=[],
        item_list_col="e_words",
        file_level=False,
        vectorizer="count",
        mask_type="myllari",
    )

    assert result["id"] == 6
    assert result["type"] == "distance-directory-level"


@patch("server.analysis.analysis_runners.Settings")
@patch("server.analysis.utils.analysis_helpers._add_result")
def test_run_log_distance_analysis_file_level_valid_inputs(
    mock_add_result, mock_settings_class
):

    mock_settings = MagicMock()
    mock_settings.match_filenames = False
    mock_settings_class.query.filter_by.return_value.first_or_404.return_value = (
        mock_settings
    )

    mock_add_result.return_value = 6

    result = ar.run_log_distance_analysis(
        project_id=7,
        directory_path=LABELED,
        target_run="./tests/datasets/labeled/correct_1/light-oauth2-oauth2-code-1.log",
        comparison_runs=[],
        item_list_col="e_words",
        file_level=True,
        vectorizer="count",
        mask_type="myllari",
    )

    assert result["id"] == 6
    assert result["type"] == "distance-file-level"


@patch("server.analysis.analysis_runners.Settings")
@patch("server.analysis.utils.analysis_helpers._add_result")
def test_run_log_distance_analysis_file_level_invalid_comparison(
    mock_add_result, mock_settings_class
):

    mock_settings = MagicMock()
    mock_settings.match_filenames = False
    mock_settings_class.query.filter_by.return_value.first_or_404.return_value = (
        mock_settings
    )

    mock_add_result.return_value = 6

    with pytest.raises(ValueError):
        ar.run_log_distance_analysis(
            project_id=7,
            directory_path=LABELED,
            target_run="./tests/datasets/labeled/correct_1/light-oauth2-oauth2-code-1.log",
            comparison_runs=[
                "./tests/datasets/labeled/correct_2/does-not-exists-1.log"
            ],
            item_list_col="e_words",
            file_level=True,
            vectorizer="count",
            mask_type="myllari",
        )

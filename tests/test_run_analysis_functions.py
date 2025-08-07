from unittest.mock import MagicMock, patch

import polars as pl
import pytest

import server.analysis.analysis_runners as ar

# Test data paths
HIDDEN_GROUP = "./tests/datasets/hidden_group_1"
LABELED = "./tests/datasets/labeled"
ONLY_CORRECT_CASES = "./tests/datasets/only_correct_cases"


class TestRunFileCountsAnalysis:
    @patch("server.analysis.utils.analysis_helpers._add_result")
    def test_run_file_count_valid_inputs(self, mock_add_result):
        mock_add_result.return_value = 42

        result = ar.run_file_count_analysis(
            project_id=123, analysis_name="test-1", directory_path=LABELED
        )

        assert result["id"] == 42
        assert result["type"] == "directory-level-visualisations"

    @patch("server.analysis.utils.analysis_helpers._add_result")
    def test_async_run_file_counts_invalid_path(self, mock_add_result):
        mock_add_result.return_value = 42
        invalid_path = ".tests/datasets/this-does-not-exists"

        with pytest.raises(FileNotFoundError):
            ar.run_file_count_analysis(
                project_id=123, analysis_name="test 123", directory_path=invalid_path
            )


class TestRunUmapAnalysis:

    @pytest.mark.parametrize(
        "file_level,expected_type",
        [
            (False, "directory-level-visualisations"),
            (True, "file-level-visualisations"),
        ],
    )
    @patch("server.analysis.utils.analysis_helpers._add_result")
    def test_run_umap_analysis_file_level_valid_inputs(
        self, mock_add_result, file_level, expected_type
    ):
        mock_add_result.return_value = 6

        result = ar.run_umap_analysis(
            project_id=7,
            analysis_name="test",
            directory_path=LABELED,
            item_list_col="e_words",
            file_level=file_level,
            vectorizer="count",
            mask_type="myllari",
        )

        assert result["id"] == 6
        assert result["type"] == expected_type

    @patch("server.analysis.utils.analysis_helpers._add_result")
    def test_run_umap_analysis_file_level_mask_none(self, mock_add_result):
        mock_add_result.return_value = 7

        result = ar.run_umap_analysis(
            project_id=7,
            analysis_name="test 0",
            directory_path=HIDDEN_GROUP,
            item_list_col="e_words",
            file_level=True,
            vectorizer="count",
            mask_type=None,
        )

        assert result["id"] == 7
        assert result["type"] == "file-level-visualisations"

    @patch("server.analysis.utils.analysis_helpers._add_result")
    def test_run_umap_analysis_file_level_invalid_vectorizer(self, mock_add_result):
        mock_add_result.return_value = 7

        with pytest.raises(ValueError):
            ar.run_umap_analysis(
                project_id=7,
                analysis_name="testing",
                directory_path=HIDDEN_GROUP,
                item_list_col="e_words",
                file_level=True,
                vectorizer="vec",
                mask_type="myllari",
            )


class TestRunUniqueTermsAnalysis:
    @pytest.mark.parametrize(
        "file_level,expected_type",
        [
            (False, "directory-level-visualisations"),
            (True, "file-level-visualisations"),
        ],
    )
    @patch("server.analysis.utils.analysis_helpers._add_result")
    def test_run_unique_terms_analysis_valid_inputs(
        self, mock_add_result, file_level, expected_type
    ):
        mock_add_result.return_value = 50

        result = ar.run_unique_terms_analysis(
            project_id=1,
            analysis_name="test",
            directory_path=LABELED,
            item_list_col="e_words",
            file_level=file_level,
        )

        assert result["id"] == 50
        assert result["type"] == expected_type

    @patch("server.analysis.utils.analysis_helpers._add_result")
    def test_run_unique_terms_analysis_invalid_item_list_col(self, mock_add_result):
        mock_add_result.return_value = 50

        with pytest.raises(ValueError):
            ar.run_unique_terms_analysis(
                project_id=1,
                analysis_name="test",
                directory_path=LABELED,
                item_list_col="bad_col",
                file_level=False,
            )

    @patch("server.analysis.analysis_runners.store_and_format_result")
    @patch("server.analysis.analysis_runners.unique_terms_count_by_file")
    @patch("server.analysis.analysis_runners.unique_terms_count_by_run")
    @patch("server.analysis.analysis_runners.load_data")
    def test_run_unique_terms_analysis_directory_level(
        self, mock_load_data, mock_count_by_run, mock_count_by_file, mock_store_result
    ):

        mock_load_data.return_value = "dummy_df"
        mock_count_by_run.return_value = {"some": "result"}
        mock_store_result.return_value = {
            "id": 1,
            "type": "directory-level-visualisations",
        }

        _ = ar.run_unique_terms_analysis(
            project_id=123,
            analysis_name="test",
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
        self, mock_load_data, mock_count_by_run, mock_count_by_file, mock_store_result
    ):

        mock_load_data.return_value = "dummy_df"
        mock_count_by_file.return_value = {"some": "result"}
        mock_store_result.return_value = {"id": 2, "type": "file-level-visualisations"}

        _ = ar.run_unique_terms_analysis(
            project_id=321,
            analysis_name="test",
            directory_path="some/path",
            item_list_col="field",
            file_level=True,
        )

        mock_count_by_file.assert_called_once_with("dummy_df", "field")
        mock_count_by_run.assert_not_called()

        mock_store_result.assert_called_once()


class TestRunLogDistanceAnalysis:

    @patch("server.analysis.analysis_runners.Settings")
    @patch("server.analysis.utils.analysis_helpers._add_result")
    def test_run_log_distance_analysis_directory_level_valid_inputs(
        self, mock_add_result, mock_settings_class
    ):

        mock_settings = MagicMock()
        mock_settings.match_filenames = False
        mock_settings_class.query.filter_by.return_value.first_or_404.return_value = (
            mock_settings
        )

        mock_add_result.return_value = 6

        result = ar.run_log_distance_analysis(
            project_id=7,
            analysis_name="test",
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
        self, mock_add_result, mock_settings_class
    ):

        mock_settings = MagicMock()
        mock_settings.match_filenames = False
        mock_settings_class.query.filter_by.return_value.first_or_404.return_value = (
            mock_settings
        )

        mock_add_result.return_value = 6

        result = ar.run_log_distance_analysis(
            project_id=7,
            analysis_name="test",
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
        self, mock_add_result, mock_settings_class
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
                analysis_name="test",
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


class TestRunAnomalyDetectionAnalysis:
    @pytest.mark.parametrize(
        "file_level,directory_level,match_filenames,expected_type",
        [
            (True, False, True, "ano-file-level"),
            (False, True, True, "ano-directory-level"),
            (False, False, True, "ano-line-level"),
            (True, False, False, "ano-file-level"),
            (False, True, False, "ano-directory-level"),
            (False, False, False, "ano-line-level"),
        ],
        ids=[
            "file+match",
            "dir+match",
            "line+match",
            "file+no-match",
            "dir+no-match",
            "line+no-match",
        ],
    )
    @patch("server.analysis.analysis_runners.Settings")
    @patch("server.analysis.utils.analysis_helpers._add_result")
    def test_run_anomaly_detection_analysis_valid_inputs(
        self,
        mock_add_result,
        mock_settings_class,
        file_level,
        directory_level,
        match_filenames,
        expected_type,
    ):

        mock_settings = MagicMock()
        mock_settings.match_filenames = match_filenames
        mock_settings_class.query.filter_by.return_value.first_or_404.return_value = (
            mock_settings
        )

        mock_add_result.return_value = 42

        result = ar.run_anomaly_detection_analysis(
            project_id=7,
            analysis_name="test",
            train_data_path=ONLY_CORRECT_CASES,
            test_data_path=HIDDEN_GROUP,
            models=["kmeans", "oovd"],
            item_list_col="e_words",
            runs_to_include=None,
            files_to_include=None,
            file_level=file_level,
            directory_level=directory_level,
            mask_type="myllari",
            vectorizer="count",
        )

        assert result["id"] == 42
        assert result["type"] == expected_type

    @pytest.mark.parametrize(
        "file_level,directory_level,match_filenames,expected_calls",
        [
            (True, False, True, ["analyze_file_group_by_filenames"]),
            (False, False, True, ["analyze_line_group_by_filenames"]),
            (False, True, True, ["aggregate_to_run_level", "analyze"]),
            (True, False, False, ["aggregate_to_file_level", "analyze"]),
            (False, True, False, ["aggregate_to_run_level", "analyze"]),
            (False, False, False, ["analyze"]),
        ],
        ids=[
            "file+match",
            "line+match",
            "dir+match",
            "file+no-match",
            "dir+no-match",
            "line+no-match",
        ],
    )
    @patch("server.analysis.analysis_runners.Settings")
    @patch("server.analysis.analysis_runners.store_and_format_result")
    @patch("server.analysis.analysis_runners.ManualTrainTestPipeline")
    def test_run_anomaly_detection_analysis_branching(
        self,
        mock_pipeline_class,
        mock_store_result,
        mock_settings_class,
        file_level,
        directory_level,
        match_filenames,
        expected_calls,
    ):

        mock_settings = MagicMock()
        mock_settings.match_filenames = match_filenames
        mock_settings_class.query.filter_by.return_value.first_or_404.return_value = (
            mock_settings
        )

        mock_pipeline = MagicMock()
        # mock_pipeline.results = MagicMock()
        mock_pipeline.results = pl.DataFrame(
            {"e_words": [["a", "b"]], "kmeans_pred_ano_proba": [0.2]}
        )
        mock_pipeline_class.return_value = mock_pipeline
        mock_store_result.return_value = {
            "id": 1,
            "type": f"ano-{'file' if file_level else 'directory' if directory_level else 'line'}-level",
        }

        _ = ar.run_anomaly_detection_analysis(
            project_id=456,
            analysis_name="test",
            train_data_path="some/train/path",
            test_data_path="some/test/path",
            models=["kmeans"],
            item_list_col="e_words",
            runs_to_include=None,
            files_to_include=None,
            file_level=file_level,
            directory_level=directory_level,
            mask_type="myllari",
            vectorizer="count",
        )

        methods = [
            "analyze_file_group_by_filenames",
            "analyze_line_group_by_filenames",
            "aggregate_to_run_level",
            "aggregate_to_file_level",
            "analyze",
        ]

        for method in methods:
            method_mock = getattr(mock_pipeline, method)
            if method in expected_calls:
                method_mock.assert_called_once()
            else:
                method_mock.assert_not_called()

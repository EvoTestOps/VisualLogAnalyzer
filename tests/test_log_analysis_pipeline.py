import polars as pl
import pytest

import server.analysis.log_analysis_pipeline as pipeline_module
from server.analysis.log_analysis_pipeline import ManualTrainTestPipeline
from server.analysis.log_analyzer import LogAnalyzer
from server.analysis.utils.analysis_helpers import create_vectorizer


def make_df(runs: dict[str, str]) -> pl.DataFrame:
    """Log lines for the given runs, each run holding one word only it has."""
    rows = [
        {
            "run": run,
            "file_name": file_name,
            "seq_id": f"{run}_{file_name}",
            "line_number": line,
            "e_words": ["shared", "words", f"line{line}"] + ([own_word] if line else []),
        }
        for run, own_word in runs.items()
        for file_name in ("a", "b")
        for line in range(4)
    ]
    return pl.DataFrame(rows)


def make_pipeline(df_train, df_test, models=None):
    pipeline = ManualTrainTestPipeline(
        model_names=models or ["oovd"],
        item_list_col="e_words",
        vectorizer=create_vectorizer("count"),
    )
    pipeline._df_train = df_train
    pipeline._df_test = df_test
    return pipeline


@pytest.fixture
def recorded_train_splits(monkeypatch):
    """The (train, test) frames handed to the analyzer for each model fit."""
    splits = []

    class RecordingLogAnalyzer(LogAnalyzer):
        def manual_train_split(self, train_df, test_df, vectorizer):
            splits.append((train_df, test_df))
            super().manual_train_split(train_df, test_df, vectorizer)

    monkeypatch.setattr(pipeline_module, "LogAnalyzer", RecordingLogAnalyzer)
    return splits


class TestTargetRunHoldOut:
    def test_target_run_is_never_in_its_own_training_data(self, recorded_train_splits):
        df = make_df({"run_1": "alpha", "run_2": "beta", "run_3": "gamma"})

        pipeline = make_pipeline(df, df)
        pipeline.aggregate_to_run_level()
        pipeline.analyze()

        assert recorded_train_splits
        for train_df, test_df in recorded_train_splits:
            scored_runs = set(test_df["run"].to_list())
            training_runs = set(train_df["run"].to_list())
            assert not scored_runs & training_runs

    def test_oov_detector_finds_the_words_only_the_scored_run_has(self):
        df = make_df({"run_1": "alpha", "run_2": "beta", "run_3": "gamma"})

        pipeline = make_pipeline(df, df)
        pipeline.aggregate_to_run_level()
        pipeline.analyze()

        # Without the hold-out every run would score 0: its own words would have
        # been part of the vocabulary it is compared against.
        assert pipeline.results.filter(pl.col("oovd_pred_ano_proba") == 0).is_empty()

    def test_results_keep_the_order_of_the_test_data(self):
        df = make_df({"run_1": "alpha", "run_2": "beta", "run_3": "gamma"})

        pipeline = make_pipeline(df, df)
        pipeline.aggregate_to_run_level()
        pipeline.analyze()

        assert pipeline.results["run"].to_list() == ["run_1", "run_2", "run_3"]

    def test_runs_missing_from_the_training_data_share_one_model(
        self, recorded_train_splits
    ):
        df_train = make_df({"train_1": "alpha", "train_2": "beta"})
        df_test = make_df({"test_1": "gamma", "test_2": "delta"})

        pipeline = make_pipeline(df_train, df_test)
        pipeline.aggregate_to_run_level()
        pipeline.analyze()

        assert len(recorded_train_splits) == 1
        train_df, test_df = recorded_train_splits[0]
        assert sorted(test_df["run"].to_list()) == ["test_1", "test_2"]
        assert sorted(train_df["run"].unique().to_list()) == ["train_1", "train_2"]

    def test_only_the_overlapping_runs_get_their_own_model(
        self, recorded_train_splits
    ):
        df_train = make_df({"run_1": "alpha", "run_2": "beta"})
        df_test = make_df({"run_2": "beta", "run_3": "gamma"})

        pipeline = make_pipeline(df_train, df_test)
        pipeline.aggregate_to_run_level()
        pipeline.analyze()

        # One model for run_3, which the training data does not contain, and one
        # trained without run_2 to score run_2.
        assert len(recorded_train_splits) == 2
        held_out = [
            (sorted(test_df["run"].to_list()), sorted(train_df["run"].to_list()))
            for train_df, test_df in recorded_train_splits
        ]
        assert (["run_3"], ["run_1", "run_2"]) in held_out
        assert (["run_2"], ["run_1"]) in held_out

    def test_file_level_holds_out_the_whole_run(self, recorded_train_splits):
        df = make_df({"run_1": "alpha", "run_2": "beta"})

        pipeline = make_pipeline(df, df)
        pipeline.aggregate_to_file_level()
        pipeline.analyze()

        for train_df, test_df in recorded_train_splits:
            scored_runs = set(test_df["run"].to_list())
            training_runs = set(train_df["run"].to_list())
            assert not scored_runs & training_runs

    def test_single_run_on_both_sides_raises(self):
        df = make_df({"only_run": "alpha"})

        pipeline = make_pipeline(df, df)
        pipeline.aggregate_to_run_level()

        with pytest.raises(ValueError, match="No comparison data left"):
            pipeline.analyze()

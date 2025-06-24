import io
import os
import gc

import polars as pl
from flask import Blueprint, Response, jsonify, request

import logging
import traceback

from services.loader import Loader
from services.enhancer import Enhancer
from services.log_analysis_pipeline import LogAnalysisPipeline, ManualTrainTestPipeline
from utils.run_level_analysis import (
    unique_terms_count_by_run,
    files_and_lines_count,
    calculate_zscore_sum_anos,
    aggregate_run_level,
)
from utils.file_level_analysis import unique_terms_count_by_file, aggregate_file_level
from utils.data_filtering import get_prediction_cols
from utils.umap_analysis import create_umap_embeddings, create_umap_df
from utils.log_distance import measure_distances

analyze_bp = Blueprint("main", __name__)


# TODO: add masking option
@analyze_bp.route("/analyze", methods=["POST"])
def analyze():
    params = request.get_json()

    dir_path = params.get("dir_path")
    models = params.get("models", ["lr"])
    test_frac = float(params.get("test_frac", 0.9))
    item_list_col = params.get("item_list_col", "e_words")
    log_format = params.get("log_format", "lo2")
    sequence_enhancement = params.get("seq", False)

    if not dir_path or not os.path.exists(dir_path):
        return (
            jsonify({"error": "No directory specified or directory does not exist"}),
            400,
        )

    results = None
    pipeline = None
    buffer = None

    try:
        pipeline = LogAnalysisPipeline(
            directory_path=dir_path,
            model_names=models,
            item_list_col=item_list_col,
            test_frac=test_frac,
            log_format=log_format,
            sequence_enhancement=sequence_enhancement,
        )
        pipeline.load()
        pipeline.enhance()
        pipeline.analyze()

        if log_format == "raw":
            results = pipeline.results
        elif not sequence_enhancement:
            results = pipeline.results.sort(["run", "m_timestamp"])
        else:
            results = pipeline.results.sort(["seq_id"])

        buffer = io.BytesIO()
        results.write_parquet(buffer, compression="zstd")  # zstd lz4
        buffer.seek(0)

        return Response(buffer.getvalue(), mimetype="application/octet-stream")

    except Exception as e:
        trace = traceback.format_exc()
        logging.error(trace)

        return jsonify({"error": str(e)}), 500

    finally:
        if buffer:
            buffer.close()

        # Might help with some memory issues, if python
        # for whatever reason doesn't drop them automatically
        if results is not None:
            del results
        if pipeline is not None:
            del pipeline

        gc.collect()


@analyze_bp.route("/manual-test-train", methods=["POST"])
def manual_test_train():
    params = request.get_json()

    train_data_path = params.get("train_data_path")
    test_data_path = params.get("test_data_path")
    models = params.get("models", ["kmeans"])
    item_list_col = params.get("item_list_col", "e_words")
    log_format = params.get("log_format", "raw")
    sequence_enhancement = params.get("seq", False)
    runs_to_include = params.get("runs_to_include", None)
    run_level = params.get("run_level", False)
    files_to_include = params.get("files_to_include", None)
    file_level = params.get("file_level", False)

    if (
        not train_data_path
        or not os.path.exists(train_data_path)
        or not test_data_path
        or not os.path.exists(test_data_path)
    ):
        return (
            jsonify({"error": "No directory specified or directory does not exist"}),
            400,
        )

    if len(models) < 1:
        return (
            jsonify(
                {
                    "error": "No detectors selected. Select atleast one model to run analysis."
                }
            ),
            400,
        )

    if runs_to_include is not None and len(runs_to_include) == 0:
        runs_to_include = None

    if files_to_include is not None and len(files_to_include) == 0:
        files_to_include = None

    results = None
    pipeline = None
    buffer = None

    try:
        pipeline = ManualTrainTestPipeline(
            model_names=models,
            item_list_col=item_list_col,
            log_format=log_format,
            sequence_enhancement=sequence_enhancement,
            train_data_path=train_data_path,
            test_data_path=test_data_path,
            runs_to_include=runs_to_include,
            files_to_include=files_to_include,
        )

        pipeline.load()
        pipeline.enhance()

        if run_level:
            pipeline.aggregate_to_run_level()
        elif file_level:
            pipeline.aggregate_to_file_level()

        pipeline.analyze()

        if log_format == "raw":
            results = pipeline.results
        elif not sequence_enhancement:
            results = pipeline.results.sort(["run", "m_timestamp"])
        else:
            results = pipeline.results.sort(["seq_id"])

        if run_level or file_level:
            results = calculate_zscore_sum_anos(
                results, distance_columns=get_prediction_cols(results)
            )
            results = results.drop(item_list_col)

        buffer = io.BytesIO()
        results.write_parquet(buffer, compression="zstd")
        buffer.seek(0)

        return Response(buffer.getvalue(), mimetype="application/octet-stream")

    except Exception as e:
        trace = traceback.format_exc()
        logging.error(trace)

        return jsonify({"error": str(e)}), 500

    finally:
        if buffer:
            buffer.close()

        if results is not None:
            del results
        if pipeline is not None:
            del pipeline

        gc.collect()


@analyze_bp.route("/run-unique-terms", methods=["POST"])
def run_unique_terms():
    params = request.get_json()

    dir_path = params.get("dir_path")
    item_list_col = params.get("item_list_col", "e_words")
    file_level = params.get("file_level", False)

    if not dir_path or not os.path.exists(dir_path):
        return (
            jsonify({"error": "No directory specified or directory does not exist"}),
            400,
        )

    buffer = None
    try:
        loader = Loader(dir_path, "raw")
        loader.load()
        df = loader.df

        if not file_level:
            unique_terms_count = unique_terms_count_by_run(df, item_list_col)
        else:
            unique_terms_count = unique_terms_count_by_file(df, item_list_col)

        buffer = io.BytesIO()
        unique_terms_count.write_parquet(buffer, compression="zstd")
        buffer.seek(0)

        return Response(buffer.getvalue(), mimetype="application/octet-stream")

    except Exception as e:
        trace = traceback.format_exc()
        logging.error(trace)

        return jsonify({"error": str(e)}), 500
    finally:
        if buffer:
            buffer.close()


@analyze_bp.route("/umap", methods=["POST"])
def create_umap():
    params = request.get_json()

    dir_path = params.get("dir_path")
    item_list_col = params.get("item_list_col", "e_words")
    file_level = params.get("file_level", False)

    if not dir_path or not os.path.exists(dir_path):
        return (
            jsonify({"error": "No directory specified or directory does not exist"}),
            400,
        )

    buffer = None
    try:
        loader = Loader(dir_path, "raw")
        loader.load()
        df = loader.df

        if not file_level:
            df_run = (
                aggregate_run_level(df, item_list_col)
                .select(item_list_col)
                .to_series()
                .to_list()
            )
            embeddings = create_umap_embeddings(df_run)
            result = create_umap_df(df, embeddings)
        else:
            df_file = (
                aggregate_file_level(df, item_list_col)
                .select(item_list_col)
                .to_series()
                .to_list()
            )
            embeddings = create_umap_embeddings(df_file)
            result = create_umap_df(df, embeddings, group_col="seq_id")

        buffer = io.BytesIO()
        result.write_parquet(buffer, compression="zstd")
        buffer.seek(0)

        return Response(buffer.getvalue(), mimetype="application/octet-stream")

    except Exception as e:
        trace = traceback.format_exc()
        logging.error(trace)

        return jsonify({"error": str(e)}), 500
    finally:
        if buffer:
            buffer.close()


@analyze_bp.route("/run-file-counts", methods=["POST"])
def run_file_counts():
    params = request.get_json()

    dir_path = params.get("dir_path")

    if not dir_path or not os.path.exists(dir_path):
        return (
            jsonify({"error": "No directory specified or directory does not exist"}),
            400,
        )

    buffer = None
    try:
        loader = Loader(dir_path, "raw")
        loader.load()
        df = loader.df

        result = files_and_lines_count(df)

        buffer = io.BytesIO()
        result.write_parquet(buffer, compression="zstd")
        buffer.seek(0)

        return Response(buffer.getvalue(), mimetype="application/octet-stream")

    except Exception as e:
        trace = traceback.format_exc()
        logging.error(trace)

        return jsonify({"error": str(e)}), 500
    finally:
        if buffer:
            buffer.close()


@analyze_bp.route("/run-distance", methods=["POST"])
def run_distance():
    params = request.get_json()

    dir_path = params.get("dir_path")
    target_run = params.get("target_run")
    comparison_runs = params.get("comparison_runs", None)
    item_list_col = params.get("item_list_col", "e_words")

    if not dir_path or not os.path.exists(dir_path):
        return (
            jsonify({"error": "No directory specified or directory does not exist"}),
            400,
        )

    if not target_run:
        return (
            jsonify({"error": "No target run specified."}),
            400,
        )

    buffer = None
    try:
        loader = Loader(dir_path, "raw")
        loader.load()

        enhancer = Enhancer(loader.df)
        df = enhancer.enhance_event(item_list_col)

        result = measure_distances(df, item_list_col, target_run, comparison_runs)

        buffer = io.BytesIO()
        result.write_parquet(buffer, compression="zstd")
        buffer.seek(0)

        return Response(buffer.getvalue(), mimetype="application/octet-stream")

    except Exception as e:
        trace = traceback.format_exc()
        logging.error(trace)

        return jsonify({"error": str(e)}), 500
    finally:
        if buffer:
            buffer.close()


@analyze_bp.route("/run-line-counts", methods=["POST"])
def run_line_lens():
    params = request.get_json()

    dir_path = params.get("dir_path")
    log_format = params.get("log_format", "lo2")

    if not dir_path or not os.path.exists(dir_path):
        return (
            jsonify({"error": "No directory specified or directory does not exist"}),
            400,
        )

    buffer = None
    try:
        loader = Loader(dir_path, log_format)
        loader.load()
        df = loader.df

        line_counts = df.group_by("run").agg(
            [
                pl.len().alias("line_count"),
                pl.col("seq_id").n_unique().alias("file_count"),
            ]
        )

        buffer = io.BytesIO()
        line_counts.write_parquet(buffer, compression="zstd")
        buffer.seek(0)

        return Response(buffer.getvalue(), mimetype="application/octet-stream")

    except Exception as e:
        trace = traceback.format_exc()
        logging.error(trace)

        return jsonify({"error": str(e)}), 500
    finally:
        if buffer:
            buffer.close()


@analyze_bp.route("/loader-test", methods=["POST"])
def loader_test():
    params = request.get_json()

    dir_path = params.get("dir_path")

    if not dir_path or not os.path.exists(dir_path):
        return (
            jsonify({"error": "No directory specified or directory does not exist"}),
            400,
        )

    buffer = None
    try:
        loader = Loader(dir_path, "raw")
        loader.load()
        df = loader.df

        buffer = io.BytesIO()
        df.write_parquet(buffer, compression="zstd")
        buffer.seek(0)

        return Response(buffer.getvalue(), mimetype="application/octet-stream")

    except Exception as e:
        trace = traceback.format_exc()
        logging.error(trace)

        return jsonify({"error": str(e)}), 500
    finally:
        if buffer:
            buffer.close()

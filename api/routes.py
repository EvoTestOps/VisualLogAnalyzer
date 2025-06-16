import io
import os
import gc

import polars as pl
from flask import Blueprint, Response, jsonify, redirect, request

import logging
import traceback

from services.loader import Loader
from services.log_analysis_pipeline import LogAnalysisPipeline

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
    labels_file_name = params.get("labels_file_name", None)
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
            labels_file_name=labels_file_name,
            sequence_enhancement=sequence_enhancement,
        )
        pipeline.load()
        pipeline.enhance()
        pipeline.analyze()

        if not sequence_enhancement:
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


@analyze_bp.route("/manual_test_train", methods=["POST"])
def manual_test_train():
    params = request.get_json()

    train_data_path = params.get("train_data_path")
    test_data_path = params.get("test_data_path")
    models = params.get("models", ["lr"])
    item_list_col = params.get("item_list_col", "e_words")
    log_format = params.get("log_format", "lo2")
    labels_file_name = params.get("labels_file_name", None)
    sequence_enhancement = params.get("seq", False)

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

    results = None
    pipeline = None
    buffer = None

    try:
        pipeline = LogAnalysisPipeline(
            model_names=models,
            item_list_col=item_list_col,
            log_format=log_format,
            labels_file_name=labels_file_name,
            sequence_enhancement=sequence_enhancement,
            manual_split=True,
            train_data_path=train_data_path,
            test_data_path=test_data_path,
        )
        pipeline.load()
        pipeline.enhance()
        pipeline.analyze()

        results = pipeline.results.sort(["run", "m_timestamp"])

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


@analyze_bp.route("/run_line_counts", methods=["POST"])
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
        line_counts.write_parquet(buffer, compression="zstd")  # zstd lz4
        buffer.seek(0)

        return Response(buffer.getvalue(), mimetype="application/octet-stream")

    except Exception as e:
        trace = traceback.format_exc()
        logging.error(trace)

        return jsonify({"error": str(e)}), 500
    finally:
        if buffer:
            buffer.close()


# @analyze_bp.route("/")
# def home():
#     return redirect("/dash")

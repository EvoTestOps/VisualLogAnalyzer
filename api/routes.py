import io
import os
import gc

import polars as pl
from flask import Blueprint, Response, jsonify, redirect, request

import logging
import traceback

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
            dir_path,
            models,
            item_list_col,
            test_frac,
            log_format,
            labels_file_name,
            sequence_enhancement,
        )
        pipeline.load()
        pipeline.enhance()
        pipeline.analyze()

        results = pipeline.results

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


# @analyze_bp.route("/")
# def home():
#     return redirect("/dash")

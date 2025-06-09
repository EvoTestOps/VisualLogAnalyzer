import io
import os

import polars as pl
from flask import Blueprint, Response, jsonify, redirect, request

from log_analyzer import LogAnalyzer

main_routes = Blueprint("main", __name__)


# TODO: fix to get multiple models
@main_routes.route("/api/analyze", methods=["POST"])
def analyze():
    analyzer = LogAnalyzer()

    params = request.get_json()

    dir_path = params.get("dir_path")
    models = params.get("models", ["lr"])
    test_frac = float(params.get("test_frac", 0.9))
    item_list_col = params.get("item_list_col", "e_words")
    log_format = params.get("log_format", "lo2")
    labels_file_name = params.get("labels_file_name", None)

    if not dir_path or not os.path.exists(dir_path):
        return (
            jsonify({"error": "No directory specified or directory does not exist"}),
            400,
        )

    if not models:
        return (
            jsonify({"error": "No models specified"}),
            400,
        )

    try:
        analyzer.load(
            dir_path=dir_path, log_format=log_format, labels_file_name=labels_file_name
        )
        analyzer.enhance(item_list_col=item_list_col)
        analyzer.train_split(item_list_col=analyzer.item_list_col, test_frac=test_frac)
        results = analyzer.run_models(models)

        avg_scores = results["avg_scores"]
        model_result = results[models[0]]  # first one for testing

        buffer = io.BytesIO()
        model_result.write_parquet(buffer, compression="lz4")  # zstd
        buffer.seek(0)

        return Response(buffer.getvalue(), mimetype="application/octet-stream")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_routes.route("/")
def home():
    return redirect("/dash")

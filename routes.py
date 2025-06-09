import os

import polars as pl
from flask import Blueprint, jsonify, redirect, request

from log_analyzer import LogAnalyzer

main_routes = Blueprint("main", __name__)


@main_routes.route("/api/analyze", methods=["POST"])
def analyze():
    analyzer = LogAnalyzer()

    dir_path = request.form.get("dir_path")
    models = request.form.getlist("models")
    test_frac = float(request.form.get("test_frac", 0.9))
    item_list_col = request.form.get("item_list_col", "e_words")
    log_format = request.form.get("log_format", "lo2")
    labels_file_name = request.form.get("labels_file_name", None)

    if not dir_path or not os.path.exists(dir_path):
        return jsonify({"error": "No directory specified"}), 400

    try:
        analyzer.load(
            dir_path=dir_path, log_format=log_format, labels_file_name=labels_file_name
        )

        analyzer.enhance(item_list_col=item_list_col)

        analyzer.train_split(item_list_col=analyzer.item_list_col, test_frac=test_frac)

        data, avg_scores = analyzer.run_models(models)

        return jsonify(avg_scores.to_dict())

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# @main_routes.route("/api/simple_plot", methods=["POST"])
# def simple_plot():
#
#     analyzer = LogAnalyzer()
#
#     dir_path = request.form.get("directory")
#     log_format = request.form.get("dataset", "lo2")
#
#     if not dir_path or not os.path.exists(dir_path):
#         return jsonify({"error": "No directory specified"}), 400
#
#     if log_format == "lo2":
#         analyzer.load_lo2(dir_path)
#     else:
#         return ""
#
#     line_counts = analyzer.df.group_by("run").agg(
#         [
#             pl.count().alias("line_count"),
#             pl.col("seq_id").n_unique().alias("file_count"),
#         ]
#     )
#     print(line_counts)
#
#     return jsonify(line_counts.to_dicts())
#


@main_routes.route("/")
def home():
    return redirect("/dash")

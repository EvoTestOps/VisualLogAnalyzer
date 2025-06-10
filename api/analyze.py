import io
import os
import gc

import polars as pl
from flask import Blueprint, Response, jsonify, redirect, request

from services.loader import Loader
from services.log_analyzer import LogAnalyzer

analyze_bp = Blueprint("main", __name__)


# TODO: add masking option
@analyze_bp.route("/", methods=["POST"])
def analyze():
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

    buffer = None
    loader = None
    analyzer = None
    results = None

    try:
        loader = Loader(
            dir_path, log_format=log_format, labels_file_name=labels_file_name
        )
        loader.load()

        analyzer = LogAnalyzer(loader.df, loader.df_seq)
        analyzer.enhance(item_list_col)
        analyzer.train_split(test_frac=test_frac)
        results = analyzer.run_models(models)

        if results is None:
            return (
                jsonify({"error": "Results are null"}),
                400,
            )

        buffer = io.BytesIO()
        results.write_parquet(buffer, compression="zstd")  # zstd lz4
        buffer.seek(0)

        return Response(buffer.getvalue(), mimetype="application/octet-stream")

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
    finally:
        if buffer:
            buffer.close()

        # Might help with some memory issues
        if results is not None:
            del results
        if analyzer is not None:
            del analyzer
        if loader is not None:
            del loader

        gc.collect()



# @main_routes.route("/")
# def home():
#     return redirect("/dash")

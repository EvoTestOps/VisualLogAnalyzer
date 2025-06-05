import os

from flask import Blueprint, jsonify, request

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
        if log_format == "lo2":
            analyzer.load_lo2(dir_path)
        elif log_format == "hadoop":
            analyzer.load_hadoop(dir_path, labels_file_name)

        analyzer.train_split(item_list_col=item_list_col, test_frac=test_frac)

        results = analyzer.run_models(models)

        data = results[0]  # make plots (store data some where)
        avg_scores = results[1].to_dict()

        return jsonify(avg_scores)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

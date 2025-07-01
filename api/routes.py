import gc
import io
import logging
import os
import traceback

from flask import Blueprint, Response, jsonify, request
from pydantic import ValidationError

from api.models.anomaly_detection_params import AnomalyDetectionParams
from api.models.high_level_analysis_params import (
    FileCountsParams,
    UmapParams,
    UniqueTermsParams,
)
from api.models.log_distance_params import LogDistanceParams
from services.enhancer import Enhancer
from services.loader import Loader
from services.log_analysis_pipeline import ManualTrainTestPipeline
from utils.data_filtering import (
    get_prediction_cols,
    filter_files,
    get_file_name_by_orig_file_name,
)
from utils.file_level_analysis import aggregate_file_level, unique_terms_count_by_file
from utils.log_distance import measure_distances
from utils.run_level_analysis import (
    aggregate_run_level,
    calculate_zscore_sum_anos,
    files_and_lines_count,
    unique_terms_count_by_run,
)
from utils.umap_analysis import create_umap_df, create_umap_embeddings

analyze_bp = Blueprint("main", __name__)


@analyze_bp.route("/manual-test-train", methods=["POST"])
def manual_test_train():
    try:
        validated_data = AnomalyDetectionParams(**request.get_json())
    except ValidationError as e:
        error = e.errors()[0]  # take the first one
        return jsonify({"error": f"{error['loc'][0]}: {error['msg']}"}), 400

    train_data_path = validated_data.train_data_path
    test_data_path = validated_data.test_data_path
    models = validated_data.models
    item_list_col = validated_data.item_list_col
    log_format = validated_data.log_format
    runs_to_include = validated_data.runs_to_include
    run_level = validated_data.run_level
    files_to_include = validated_data.files_to_include
    file_level = validated_data.file_level
    mask_type = validated_data.mask_type
    vectorizer = validated_data.vectorizer

    results = None
    pipeline = None
    buffer = None

    # TODO: Rather than getting boolean values, take str for level
    if file_level:
        level = "file"
    elif run_level:
        level = "run"
    else:
        level = "line"

    try:
        pipeline = ManualTrainTestPipeline(
            model_names=models,
            item_list_col=item_list_col,
            log_format=log_format,
            vectorizer=vectorizer,
            train_data_path=train_data_path,
            test_data_path=test_data_path,
            runs_to_include=runs_to_include,
            files_to_include=files_to_include,
            mask_type=mask_type,
        )

        pipeline.load()
        pipeline.enhance()

        # TODO: add setting/input to specify if files are analysed against other files with the same file name,
        #  or against all files disregarding file name
        mock_flag = True

        if mock_flag:
            if level == "file":
                pipeline.analyze_file_group_by_filenames()
            elif level == "line":
                pipeline.analyze_line_group_by_filenames()
            else:
                pipeline.aggregate_to_run_level()
                pipeline.analyze()
        else:
            if level == "file":
                pipeline.aggregate_to_file_level()
            elif level == "run":
                pipeline.aggregate_to_run_level()
            pipeline.analyze()

        results = pipeline.results
        if results is None:
            raise ValueError("No results found")

        # TODO: fix sorting for LO2 data
        if log_format != "raw":
            results = results.sort(["run"])

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

        # Might help with some memory issues, if python
        # for whatever reason doesn't drop them automatically
        if results is not None:
            del results
        if pipeline is not None:
            del pipeline

        gc.collect()


@analyze_bp.route("/unique-terms", methods=["POST"])
def run_unique_terms():
    try:
        validated_data = UniqueTermsParams(**request.get_json())
    except ValidationError as e:
        error = e.errors()[0]
        return jsonify({"error": f"{error['loc'][0]}: {error['msg']}"}), 400

    dir_path = validated_data.directory_path
    item_list_col = validated_data.item_list_col
    file_level = validated_data.file_level

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
    try:
        validated_data = UmapParams(**request.get_json())
    except ValidationError as e:
        error = e.errors()[0]
        return jsonify({"error": f"{error['loc'][0]}: {error['msg']}"}), 400

    dir_path = validated_data.directory_path
    item_list_col = validated_data.item_list_col
    file_level = validated_data.file_level
    vectorizer = validated_data.vectorizer
    mask_type = validated_data.mask_type

    buffer = None
    try:
        loader = Loader(dir_path, "raw")
        loader.load()
        df = loader.df

        if not file_level:
            df_run = (
                aggregate_run_level(df, item_list_col, mask_type)
                .select(item_list_col)
                .to_series()
                .to_list()
            )
            embeddings = create_umap_embeddings(df_run, vectorizer)
            result = create_umap_df(df, embeddings)
        else:
            df_file = (
                aggregate_file_level(df, item_list_col, mask_type)
                .select(item_list_col)
                .to_series()
                .to_list()
            )
            embeddings = create_umap_embeddings(df_file, vectorizer)
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
    try:
        validated_data = FileCountsParams(**request.get_json())
    except ValidationError as e:
        error = e.errors()[0]
        return jsonify({"error": f"{error['loc'][0]}: {error['msg']}"}), 400

    dir_path = validated_data.directory_path

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
    try:
        validated_data = LogDistanceParams(**request.get_json())
    except ValidationError as e:
        error = e.errors()[0]
        return jsonify({"error": f"{error['loc'][0]}: {error['msg']}"}), 400

    dir_path = validated_data.directory_path
    target_run = validated_data.target_run
    comparison_runs = validated_data.comparison_runs
    item_list_col = validated_data.item_list_col
    file_level = validated_data.file_level
    mask_type = validated_data.mask_type
    vectorizer = validated_data.vectorizer

    buffer = None
    try:
        loader = Loader(dir_path, "raw")
        loader.load()

        enhancer = Enhancer(loader.df)
        df = enhancer.enhance_event(item_list_col, mask_type)

        run_column = "run" if not file_level else "orig_file_name"

        # TODO: Add a setting to change if comparisons are done against matching file names
        if file_level and comparison_runs in (None, []):
            target_file_name = get_file_name_by_orig_file_name(df, target_run)
            df = filter_files(df, [target_file_name], "file_name")

        result = measure_distances(
            df,
            item_list_col,
            target_run,
            run_column=run_column,
            comparison_runs=comparison_runs,
            vectorizer=vectorizer,
        )

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
        if df is None:
            raise ValueError("No results found")

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

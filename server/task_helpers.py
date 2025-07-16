import logging
import os

from flask import current_app
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from server.analysis.loader import Loader
from server.extensions import db
from server.models.analysis import Analysis


def load_data(directory_path):
    loader = Loader(directory_path, "raw")
    loader.load()
    return loader.df


def create_vectorizer(vectorizer_type: str) -> object:
    if vectorizer_type == "count":
        return CountVectorizer
    elif vectorizer_type == "tfidf":
        return TfidfVectorizer
    else:
        raise ValueError(f"Unsupported vectorizer type: {vectorizer_type}")


def store_and_format_result(result, project_id, analysis_type, metadata):
    result_id = _add_result(result, project_id, analysis_type, **metadata)
    return {"id": result_id, "type": analysis_type}


def handle_errors(project_id, context, error):
    logging.error(
        f"Error processing {context} for project {project_id}: {str(error)}",
        exc_info=True,
    )
    return {"error": str(error)}


def _add_result(df, project_id: int, analysis_type: str, **kwargs):
    analysis = Analysis(
        results_path="",
        analysis_type=analysis_type,
        project_id=project_id,
        **kwargs,
    )

    db.session.add(analysis)
    db.session.commit()

    result_path = os.path.join(
        current_app.config["RESULTS_PATH"], f"{analysis.id}.parquet"
    )
    analysis.results_path = result_path
    db.session.commit()

    df.write_parquet(result_path)

    del df

    return analysis.id

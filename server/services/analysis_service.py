import os
from flask import current_app
from server.extensions import db
from server.models.analysis import Analysis


def add_result(df, path: str, analysis_type: str, analysis_level: str):
    result_path = os.path.join(current_app.config["RESULTS_PATH"], path)
    df.write_parquet(result_path)

    analysis = Analysis(
        results_path=path, analysis_type=analysis_type, analysis_level=analysis_level
    )

    db.session.add(analysis)
    db.session.commit()

    return analysis.id


# TODO: Get result by id

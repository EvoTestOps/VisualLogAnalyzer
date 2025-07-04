import os
from flask import current_app
from server.extensions import db
from server.models.analysis import Analysis


def add_result(df, project_id: int, analysis_type: str, analysis_level: str):

    analysis = Analysis(
        results_path="",
        analysis_type=analysis_type,
        analysis_level=analysis_level,
        project_id=project_id,
    )

    db.session.add(analysis)
    db.session.commit()

    result_path = os.path.join(
        current_app.config["RESULTS_PATH"], f"{analysis.id}.parquet"
    )
    analysis.results_path = result_path
    db.session.commit()

    df.write_parquet(result_path)

    return analysis.id


# TODO: Get result by id

from server.extensions import db
from sqlalchemy.sql import func


class Analysis(db.Model):
    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True)
    results_path = db.Column(db.String, nullable=False)
    analysis_type = db.Column(db.String, nullable=False)
    analysis_level = db.Column(db.String)

    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    project = db.relationship("Project", back_populates="analyses")

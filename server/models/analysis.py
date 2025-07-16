from sqlalchemy.sql import func

from server.extensions import db


class Analysis(db.Model):
    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True)

    results_path = db.Column(db.String, nullable=False)
    analysis_type = db.Column(db.String, nullable=False)
    analysis_sub_type = db.Column(db.String, nullable=False)
    analysis_level = db.Column(db.String, nullable=False)

    mask_type = db.Column(db.String)
    vectorizer = db.Column(db.String)
    enhancement = db.Column(db.String)
    models = db.Column(db.String)

    directory_path = db.Column(db.String)
    train_data_path = db.Column(db.String)
    test_data_path = db.Column(db.String)

    target = db.Column(db.String)

    item_list_col = db.Column(db.String)

    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    project = db.relationship("Project", back_populates="analyses")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "analysis_type": self.analysis_type,
            "analysis_sub_type": self.analysis_sub_type,
            "analysis_level": self.analysis_level,
            "directory_path": self.directory_path,
            "train_data_path": self.train_data_path,
            "test_data_path": self.test_data_path,
            "models": self.models,
            "enhancement": self.enhancement,
            "target": self.target,
            "field": self.item_list_col,
            "mask_type": self.mask_type,
            "vectorizer": self.vectorizer,
            "results_path": self.results_path,
            "time_created": (
                self.time_created.isoformat() if self.time_created else None
            ),
            "time_updated": (
                self.time_updated.isoformat() if self.time_updated else None
            ),
        }

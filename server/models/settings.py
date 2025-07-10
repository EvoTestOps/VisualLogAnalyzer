from server.extensions import db


class Settings(db.Model):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    match_filenames = db.Column(db.Boolean, default=True)

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    project = db.relationship("Project", back_populates="settings")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "match_filenames": self.match_filenames,
        }

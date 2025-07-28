from server.extensions import db


class Settings(db.Model):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    match_filenames = db.Column(db.Boolean, default=True)
    color_by_directory = db.Column(db.Boolean, default=False)
    line_level_display_mode = db.Column(db.String, default="data_points_only")
    manual_filename_input = db.Column(db.Boolean, default=False)

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    project = db.relationship("Project", back_populates="settings")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "match_filenames": self.match_filenames,
            "color_by_directory": self.color_by_directory,
            "line_level_display_mode": self.line_level_display_mode,
            "manual_filename_input": self.manual_filename_input,
        }

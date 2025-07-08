from server.extensions import db


class Settings(db.Model):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    match_file_names = db.Column(db.Boolean, default=True)

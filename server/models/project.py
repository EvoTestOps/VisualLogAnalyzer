from sqlalchemy import event
from sqlalchemy.sql import func

from server.extensions import db

from server.models.settings import Settings


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    analyses = db.relationship(
        "Analysis", back_populates="project", cascade="all, delete-orphan"
    )

    settings = db.relationship(
        "Settings",
        uselist=False,
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def to_dict(self, include_analyses=False):
        data = {
            "id": self.id,
            "name": self.name,
            "time_created": (
                self.time_created.isoformat() if self.time_created else None
            ),
            "time_updated": (
                self.time_updated.isoformat() if self.time_updated else None
            ),
            "analyses_count": len(self.analyses),
        }

        if include_analyses:
            data["analyses"] = [analysis.to_dict() for analysis in self.analyses]

        return data


@event.listens_for(Project, "after_insert")
def create_settings(mapper, connection, target):
    connection.execute(
        Settings.__table__.insert(), {"project_id": target.id, "match_filenames": True}
    )

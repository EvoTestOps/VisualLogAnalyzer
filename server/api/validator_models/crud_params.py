from pathlib import Path
from typing import Literal, Optional
from flask import current_app

from pydantic import BaseModel, field_validator


class ProjectParams(BaseModel):
    name: str
    base_path: Optional[str] = None

    @field_validator("base_path", mode="after")
    @classmethod
    def validate_directory_path(cls, value: Optional[str]) -> Optional[str]:
        if not value:
            return None

        path = Path(value).resolve()

        log_data_root = Path(current_app.config["LOG_DATA_PATH"]).resolve()

        try:
            path.relative_to(log_data_root)
        except ValueError:
            raise ValueError(f"Path must be inside {log_data_root}, got {path}")

        if not path.is_dir():
            raise ValueError(f"Directory does not exist: {path}")

        return str(path)


class SettingsParams(BaseModel):
    match_filenames: bool
    color_by_directory: bool
    line_level_display_mode: Literal["data_points_only", "moving_avg_only", "all"] = (
        "data_points_only"
    )
    manual_filename_input: bool

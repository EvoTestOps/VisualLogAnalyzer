from pydantic import BaseModel
from typing import Literal


class ProjectParams(BaseModel):
    name: str


class SettingsParams(BaseModel):
    match_filenames: bool
    color_by_directory: bool
    line_level_display_mode: Literal["data_points_only", "moving_avg_only", "all"] = (
        "data_points_only"
    )

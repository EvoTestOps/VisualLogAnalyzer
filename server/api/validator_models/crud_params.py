from pydantic import BaseModel


class ProjectParams(BaseModel):
    name: str


class SettingsParams(BaseModel):
    match_filenames: bool
    color_by_directory: bool

from pydantic import BaseModel


class ProjectParams(BaseModel):
    name: str


class SettingsParams(BaseModel):
    match_filenames: bool

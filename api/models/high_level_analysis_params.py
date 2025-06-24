from pydantic import BaseModel, Field, field_validator, model_validator
import os


def _validate_directory_path(path: str):
    if not path:
        raise ValueError(f"Directory path is required.")
    if not os.path.exists(path):
        raise ValueError(f"Log data path does not exists: {path}")
    return path


class UniqueTermsParams(BaseModel):
    directory_path: str = Field(default=False, alias="dir_path")
    item_list_col: str = "e_words"
    file_level: bool = False

    @field_validator("directory_path", mode="after")
    @classmethod
    def validate_directory_path(cls, value: str) -> str:
        return _validate_directory_path(value)


# Same as uniquetermsparams but might change in the future
class UmapParams(BaseModel):
    directory_path: str = Field(default=False, alias="dir_path")
    item_list_col: str = "e_words"
    file_level: bool = False

    @field_validator("directory_path", mode="after")
    @classmethod
    def validate_directory_path(cls, value: str) -> str:
        return _validate_directory_path(value)


class FileCountsParams(BaseModel):
    directory_path: str = Field(default=False, alias="dir_path")

    @field_validator("directory_path", mode="after")
    @classmethod
    def validate_directory_path(cls, value: str) -> str:
        return _validate_directory_path(value)

from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator

from server.api.validator_models.validator_utils import validate_directory_path


class UniqueTermsParams(BaseModel):
    directory_path: str = Field(alias="dir_path")
    item_list_col: str = "e_words"
    file_level: bool = False

    @field_validator("directory_path", mode="after")
    @classmethod
    def validate_directory_path(cls, value: str) -> str:
        return validate_directory_path(value)


class UmapParams(BaseModel):
    directory_path: str = Field(alias="dir_path")
    item_list_col: str = "e_words"
    file_level: bool = False
    vectorizer: Literal["count", "tfidf"] = "count"
    mask_type: Optional[str] = None

    @field_validator("directory_path", mode="after")
    @classmethod
    def validate_directory_path(cls, value: str) -> str:
        return validate_directory_path(value)


class FileCountsParams(BaseModel):
    directory_path: str = Field(alias="dir_path")

    @field_validator("directory_path", mode="after")
    @classmethod
    def validate_directory_path(cls, value: str) -> str:
        return validate_directory_path(value)

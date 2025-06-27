from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from typing import Any
from pydantic import BaseModel, Field, field_validator
from api.models.validator_utils import validate_directory_path


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
    vectorizer: object = CountVectorizer

    @field_validator("vectorizer", mode="before")
    @classmethod
    def create_vectorizer(cls, value: Any) -> Any:
        if isinstance(value, str):
            if value == "count":
                return CountVectorizer
            elif value == "tfidf":
                return TfidfVectorizer
            else:
                raise ValueError(f"Unsupported vectorizer type: {value}")
        else:
            return CountVectorizer

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

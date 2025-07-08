from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from server.api.validator_models.validator_utils import validate_directory_path


class LogDistanceParams(BaseModel):
    directory_path: str = Field(alias="dir_path")
    target_run: str
    comparison_runs: Optional[List[str]] = None
    item_list_col: str = "e_words"
    file_level: bool = False
    mask_type: Optional[str] = None
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

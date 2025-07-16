from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from server.api.validator_models.validator_utils import validate_directory_path


class LogDistanceParams(BaseModel):
    directory_path: str = Field(alias="dir_path")
    target_run: str
    comparison_runs: Optional[List[str]] = None
    item_list_col: str = "e_words"
    file_level: bool = False
    mask_type: Optional[str] = None
    vectorizer: Literal["count", "tfidf"] = "count"

    @field_validator("directory_path", mode="after")
    @classmethod
    def validate_directory_path(cls, value: str) -> str:
        return validate_directory_path(value)

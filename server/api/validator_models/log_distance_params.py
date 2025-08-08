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
    name: Optional[str]

    @field_validator("directory_path", mode="after")
    @classmethod
    def validate_directory_path(cls, value: str) -> str:
        return validate_directory_path(value)

    @field_validator("comparison_runs", mode="before")
    @classmethod
    def validate_comparison_runs(cls, value):
        if value is None:
            return None

        if isinstance(value, list) and all(isinstance(v, str) for v in value):
            return value

        if isinstance(value, str):
            try:
                return [v.strip() for v in value.split(",") if v.strip()]
            except Exception as e:
                raise ValueError(
                    f"Failed to parse comparison runs from string: {value}. Error: {e}"
                )

        raise ValueError(
            "Comparison runs must be a comma-separated string or a list of strings"
        )

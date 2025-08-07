import os
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import Self


class AnomalyDetectionParams(BaseModel):
    train_data_path: str
    test_data_path: str
    name: Optional[str]
    models: List[str] = ["kmeans"]
    item_list_col: str = "e_words"
    log_format: Literal["raw", "lo2"] = "raw"
    sequence_enhancement: bool = Field(default=False, alias="seq")
    runs_to_include: Optional[List[str]] = None
    run_level: bool = False
    files_to_include: Optional[List[str]] = None
    file_level: bool = False
    mask_type: Optional[str] = None
    vectorizer: Literal["count", "tfidf"] = "count"

    @field_validator("train_data_path", mode="after")
    @classmethod
    def validate_train_data_path(cls, value: str) -> str:
        if not os.path.exists(value):
            raise ValueError(
                f"Training data path does not exists: {value if value else 'None'}"
            )
        return value

    @field_validator("test_data_path", mode="after")
    @classmethod
    def validate_test_data_path(cls, value: str) -> str:
        if not os.path.exists(value):
            raise ValueError(
                f"Test data path does not exists: {value if value else 'None'}"
            )
        return value

    @field_validator("models", mode="after")
    @classmethod
    def validate_models(cls, value: List[str]) -> List[str]:
        if not value or len(value) < 1:
            raise ValueError(
                "No detection models selected. Select atleast one to run analysis."
            )
        return value

    @field_validator("runs_to_include", mode="after")
    @classmethod
    def validate_runs_to_include(
        cls, value: Optional[List[str]]
    ) -> Optional[List[str]]:
        if value is not None and len(value) == 0:
            return None
        return value

    @field_validator("files_to_include", mode="after")
    @classmethod
    def validate_files_to_include(
        cls, value: Optional[List[str]]
    ) -> Optional[List[str]]:
        if value is not None and len(value) == 0:
            return None
        return value

    @model_validator(mode="after")
    def check_exclusive_levels(self) -> Self:
        if self.run_level and self.file_level:
            raise ValueError(
                "Only run level or file level analysis can be true at once."
            )
        return self

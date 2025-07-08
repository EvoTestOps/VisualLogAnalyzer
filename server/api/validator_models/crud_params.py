from pydantic import BaseModel


class ProjectParams(BaseModel):
    name: str

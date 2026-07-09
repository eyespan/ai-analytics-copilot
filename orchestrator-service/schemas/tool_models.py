# schemas/tool_models.py

from pydantic import BaseModel


class GetTimeInput(BaseModel):
    pass


class GetTimeOutput(BaseModel):
    current_time: str


class SearchDocsInput(BaseModel):
    query: str


class SearchDocsOutput(BaseModel):
    results: list[str]

from pydantic import BaseModel, Field

class IndexRequest(BaseModel):
    repo_path: str | None = None

class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)

class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=12)

class DebugRequest(BaseModel):
    stack_trace: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=12)

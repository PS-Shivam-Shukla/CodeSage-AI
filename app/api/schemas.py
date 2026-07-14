from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str

class IndexRequest(BaseModel):
    repository_path: str


class RepositoryIndexResponse(BaseModel):
    status: str
    message: str

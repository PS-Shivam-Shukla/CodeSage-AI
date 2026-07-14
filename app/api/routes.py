from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.api.schemas import (
    ChatRequest,
    ChatResponse,
    IndexRequest,
    RepositoryIndexResponse,
)
from app.indexing import IndexingService
from pathlib import Path
import sqlite3
from app.rag import RAGPipeline


router = APIRouter()

pipeline = RAGPipeline()
indexing_service = IndexingService()


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
):

    answer = pipeline.ask(
        request.question
    )

    return ChatResponse(
        answer=answer
    )


@router.post(
    "/index",
    response_model=RepositoryIndexResponse,
)
def index_repository(
    request: IndexRequest,
    background_tasks: BackgroundTasks,
):
    """Schedule repository indexing as a background task and return immediately.

    This prevents long-running indexing requests from timing out on the client
    and gives the frontend an immediate success response while the server
    processes the repository in the background.
    """

    try:
        # schedule the long-running indexing to run in the background
        background_tasks.add_task(
            indexing_service.index_repository,
            request.repository_path,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    return RepositoryIndexResponse(
        status="accepted",
        message="Indexing started in background.",
    )


@router.get(
    "/index/status",
)
def index_status():
    """Return a lightweight status of the on-disk Chroma DB.

    This helps the frontend show progress without relying on server stdout.
    """
    db_path = Path("chroma_db") / "chroma.sqlite3"

    if not db_path.exists():
        return {"status": "not_found", "message": "chroma DB not present"}

    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM segments")
        segments = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM embeddings")
        embeddings = cur.fetchone()[0]
        conn.close()

        return {
            "status": "ok",
            "segments": segments,
            "embeddings": embeddings,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
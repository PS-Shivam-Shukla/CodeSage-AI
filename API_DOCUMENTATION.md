# API Documentation

Base URL: `http://localhost:8000`

All request and response bodies use `application/json`.

---

## Endpoints

### POST /chat

Ask a natural language question about the indexed repository.

**Request Body**

```json
{
  "question": "What does the IndexingService do?"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `question` | string | Yes | The question to ask about the codebase |

**Response Body — 200 OK**

```json
{
  "answer": "The IndexingService orchestrates the full pipeline: it loads documents from the repository, splits them into chunks, and stores the chunks in ChromaDB."
}
```

| Field | Type | Description |
|---|---|---|
| `answer` | string | Generated answer grounded in repository context |

**Error — 500 Internal Server Error**

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Notes**
- The LLM will respond with `"I couldn't find that information in the repository."` if the answer cannot be found in the retrieved context.
- Retrieves top-5 most relevant chunks by default before generating the answer.
- Timeout on the frontend Axios client is set to 120 seconds.

---

### POST /index

Index a local repository into the vector database. Returns immediately — indexing runs as a background task.

**Request Body**

```json
{
  "repository_path": "/path/to/your/repository"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `repository_path` | string | Yes | Absolute or relative path to the repository on the server filesystem |

**Response Body — 200 OK**

```json
{
  "status": "accepted",
  "message": "Indexing started in background."
}
```

| Field | Type | Description |
|---|---|---|
| `status` | string | Always `"accepted"` when the task is successfully queued |
| `message` | string | Human-readable confirmation message |

**Error — 500 Internal Server Error**

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Notes**
- The endpoint returns before indexing completes. Poll `/index/status` to track progress.
- Supported file types: `.py` `.java` `.js` `.ts` `.jsx` `.tsx` `.json` `.xml` `.yml` `.yaml` `.properties` `.toml` `.ini` `.md` `.txt` `.sql` `.html` `.css` `.pdf`
- Files exceeding **5 MB** are skipped automatically.
- The following directories are ignored: `.git`, `node_modules`, `target`, `build`, `dist`, `coverage`, `.venv`, `venv`, `__pycache__`, `.idea`, `.vscode`, `.github`

---

### GET /index/status

Returns a lightweight status of the on-disk ChromaDB — useful for polling indexing progress from the frontend.

**Request** — No body required.

**Response — 200 OK (DB found)**

```json
{
  "status": "ok",
  "segments": 12,
  "embeddings": 248
}
```

| Field | Type | Description |
|---|---|---|
| `status` | string | `"ok"` when the DB is found and queryable |
| `segments` | integer | Number of ChromaDB segments |
| `embeddings` | integer | Number of stored embeddings (roughly equals total chunks) |

**Response — 200 OK (DB not yet created)**

```json
{
  "status": "not_found",
  "message": "chroma DB not present"
}
```

**Response — 200 OK (DB error)**

```json
{
  "status": "error",
  "message": "Error message from SQLite"
}
```

---

## Schemas

### ChatRequest

```python
class ChatRequest(BaseModel):
    question: str
```

### ChatResponse

```python
class ChatResponse(BaseModel):
    answer: str
```

### IndexRequest

```python
class IndexRequest(BaseModel):
    repository_path: str
```

### RepositoryIndexResponse

```python
class RepositoryIndexResponse(BaseModel):
    status: str
    message: str
```

---

## CORS

The following origins are allowed by default:

- `http://localhost:5173`
- `http://127.0.0.1:5173`
- `http://localhost:5174`
- `http://127.0.0.1:5174`

All HTTP methods and headers are permitted. Credentials are allowed.

To add additional origins, update the `allow_origins` list in `main.py`.

---

## Interactive Docs

FastAPI provides interactive documentation automatically:

| URL | Description |
|---|---|
| `http://localhost:8000/docs` | Swagger UI |
| `http://localhost:8000/redoc` | ReDoc |
| `http://localhost:8000/openapi.json` | Raw OpenAPI schema |

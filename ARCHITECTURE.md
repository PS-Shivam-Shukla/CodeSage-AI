# Architecture

This document describes the system design, component responsibilities, and data flow of CodeSage AI.

---

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                           │
│          React 19 + TypeScript + Vite + Tailwind CSS            │
│   /repository  /chat  /vector-store  /models  /settings  ...   │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP (Axios)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│                         main.py                                 │
│              CORS · Router · Pydantic Schemas                   │
│                                                                 │
│   POST /chat          POST /index        GET /index/status      │
└──────┬────────────────────┬──────────────────────┬─────────────┘
       │                    │                      │
       ▼                    ▼                      ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│ RAGPipeline  │  │ IndexingService  │  │  SQLite Status Query │
│              │  │  (Background)    │  │   (chroma.sqlite3)   │
│ 1. Retrieve  │  │ 1. Ingest        │  └──────────────────────┘
│ 2. Context   │  │ 2. Split         │
│ 3. Generate  │  │ 3. Embed + Store │
└──────┬───────┘  └────────┬─────────┘
       │                   │
       ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ChromaDB (local)                           │
│           persist_directory: ./chroma_db                        │
│           collection: repository_chunks                         │
│           embedding: BAAI/bge-m3 (HuggingFace, CPU)            │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼ (retrieved context)
┌─────────────────────────────────────────────────────────────────┐
│                    NVIDIA AI Endpoints                          │
│           model: meta/llama-3.1-70b-instruct                    │
│           temperature: 0.2 · top_p: 0.9 · max_tokens: 1024     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### Frontend (`frontend/`)

Built with React 19, TypeScript, Vite, and Tailwind CSS. Communicates with the backend exclusively via an Axios instance (`src/services/api.ts`) pointed at `http://localhost:8000` by default (overridable via `VITE_API_URL`).

| Component | Responsibility |
|---|---|
| `App.tsx` | Route definitions via React Router v7 |
| `Layout.tsx` | Shared shell — sidebar + topbar + content area |
| `Sidebar.tsx` | Navigation links to all pages |
| `ChatPage.tsx` | Message thread, input box, Markdown rendering |
| `RepositoryPage.tsx` | Path input + trigger for `/index` endpoint |
| `VectorStorePage.tsx` | Displays index status from `/index/status` |
| `chat.service.ts` | `POST /chat` call |
| `repository.service.ts` | `POST /index` call |
| `api.ts` | Axios base instance (timeout: 120s) |

---

### Backend API Layer (`app/api/`)

| File | Responsibility |
|---|---|
| `routes.py` | Three route handlers: `/chat`, `/index`, `/index/status` |
| `schemas.py` | Pydantic models: `ChatRequest`, `ChatResponse`, `IndexRequest`, `RepositoryIndexResponse` |

The `/index` endpoint uses FastAPI `BackgroundTasks` so the HTTP response returns immediately (`202 Accepted`) while indexing runs server-side.

---

### Indexing Pipeline (`app/indexing/` + `app/ingestion/` + `app/splitters/`)

```
Repository path
      │
      ▼
RepositoryIngestionService
  - rglob("*") recursive file walk
  - Filter: IGNORED_DIRECTORIES, SUPPORTED_EXTENSIONS, MAX_FILE_SIZE (5 MB)
  - Load PDF via PyPDF, text files via plain read
  - Returns: List[LangChain Document]
      │
      ▼
DocumentSplitter
  - RecursiveCharacterTextSplitter
  - chunk_size=1000, chunk_overlap=200
  - Code-aware separators (class, def, function, interface, enum …)
  - Enriches metadata: chunk_index, chunk_number, total_chunks, chunk_label
  - Returns: List[LangChain Document] (chunks)
      │
      ▼
ChromaService.add_documents()
  - Generates embeddings via EmbeddingService (BAAI/bge-m3)
  - Stores in ChromaDB collection "repository_chunks"
```

---

### Embedding Service (`app/embeddings/`)

- Model: `BAAI/bge-m3` — a multilingual, multi-granularity embedding model
- Loaded once via `@lru_cache(maxsize=1)` to avoid repeated model initialization
- Runs on CPU by default (configurable in `app/config/embedding_config.py`)
- Normalized embeddings enabled for cosine similarity compatibility
- Model weights cached locally in `./models/`

---

### Retrieval (`app/retriever/`)

`RetrievalService` wraps `ChromaService.similarity_search()`:
- Takes a user query string
- Returns top-k (default 5) most semantically similar document chunks
- Similarity is computed via cosine distance on normalized `bge-m3` embeddings

---

### RAG Pipeline (`app/rag/`)

```
User question
      │
      ▼
RetrievalService.retrieve(question, k=5)
      │
      ▼
RAGPipeline._build_context(documents)
  - Joins page_content of all chunks with "\n\n"
      │
      ▼
LLMService.generate_answer(question, context)
      │
      ▼
PromptService.build_prompt()
  - Loads system prompt from app/llm/prompts/repository_qa.txt
  - Injects {context} and {question}
      │
      ▼
NVIDIAProvider.generate(prompt)
  - ChatNVIDIA.invoke(prompt)
  - Returns: answer string
```

---

### LLM Layer (`app/llm/`)

| Component | Responsibility |
|---|---|
| `LLMService` | Coordinates prompt building and generation |
| `NVIDIAProvider` | Wraps `ChatNVIDIA` — single responsibility: communicate with NVIDIA API |
| `PromptService` | Loads and builds the LangChain prompt template from the `.txt` file |
| `llm_config.py` | Model name, temperature, top_p, max_tokens |

The system prompt instructs the LLM to answer **only** from the provided context and to respond with `"I couldn't find that information in the repository."` when the answer is not present.

---

### Vector Store (`app/vectorstore/`)

`ChromaService` wraps `langchain_chroma.Chroma`:
- Persist directory: `./chroma_db`
- Collection name: `repository_chunks`
- Embedding function: `EmbeddingService.get_model()`
- Exposes `add_documents()` and `similarity_search()`

---

### Configuration (`app/config/`)

All tunable parameters are centralised in dedicated config files — no magic numbers in business logic:

| File | Controls |
|---|---|
| `embedding_config.py` | Model name, device, normalization, cache folder |
| `vectorstore_config.py` | ChromaDB persist directory, collection name |
| `splitter_config.py` | Chunk size, overlap, separator priority list |
| `llm_config.py` | LLM model, temperature, top_p, max_tokens |

---

## Data Flow Summary

| Scenario | Flow |
|---|---|
| Index a repository | Frontend → `POST /index` → BackgroundTask → Ingest → Split → Embed → ChromaDB |
| Ask a question | Frontend → `POST /chat` → RAGPipeline → ChromaDB similarity search → NVIDIA LLM → answer |
| Check index status | Frontend → `GET /index/status` → SQLite query on `chroma.sqlite3` → counts |
| CLI usage | `CLI.py` → `IndexingService` → `RAGPipeline` directly (no HTTP layer) |

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Background indexing via FastAPI `BackgroundTasks` | Prevents HTTP timeout on large repositories |
| `lru_cache` on embedding model | Avoids reloading a large model on every request |
| Code-aware `RecursiveCharacterTextSplitter` separators | Keeps class/function boundaries intact in chunks |
| Metadata enrichment on chunks | Enables traceability — knowing which chunk came from which file and position |
| Config files separate from logic | Switching models or tuning parameters requires no logic changes |
| Strict LLM system prompt | Prevents hallucination — LLM must stay grounded in retrieved context |

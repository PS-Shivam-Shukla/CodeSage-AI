# Changelog

All notable changes to CodeSage AI are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Streaming LLM responses via Server-Sent Events
- Multi-repository support
- Conversation history persistence
- Docker Compose setup for one-command deployment
- Support for CUDA-accelerated embeddings

---

## [1.0.0] — 2025-07-14

### Added

#### Backend
- `FastAPI` application entry point (`main.py`) with CORS middleware configured for local Vite dev server ports `5173` and `5174`
- `POST /chat` endpoint — accepts a `question` string and returns a generated `answer`
- `POST /index` endpoint — schedules repository indexing as a `BackgroundTask` and returns `202 Accepted` immediately
- `GET /index/status` endpoint — queries the on-disk ChromaDB SQLite file and returns segment and embedding counts
- `IndexingService` — orchestrates the full ingestion → split → store pipeline
- `RepositoryIngestionService` — recursively walks a repository, filters by supported extension and 5 MB size limit, loads files as LangChain `Document` objects
- `DocumentSplitter` — wraps `RecursiveCharacterTextSplitter` (chunk size: 1000, overlap: 200) with code-aware separators and enriches each chunk with `chunk_index`, `chunk_number`, `total_chunks`, and `chunk_label` metadata
- `EmbeddingService` — loads `BAAI/bge-m3` via `HuggingFaceEmbeddings` with `lru_cache` to avoid repeated model loading
- `ChromaService` — persists vector data to `./chroma_db` under the `repository_chunks` collection
- `RetrievalService` — top-k similarity search (default k=5) over ChromaDB
- `RAGPipeline` — chains retrieval → context building → LLM generation
- `LLMService` — combines `PromptService` and `NVIDIAProvider`
- `NVIDIAProvider` — wraps `ChatNVIDIA` with `meta/llama-3.1-70b-instruct` (temp: 0.2, top_p: 0.9, max_tokens: 1024)
- `PromptService` — loads the system prompt from `app/llm/prompts/repository_qa.txt`
- System prompt that strictly restricts the LLM to answer only from provided context
- `CLI.py` — interactive terminal interface for indexing and Q&A without the frontend

#### Frontend
- React 19 + TypeScript + Vite + Tailwind CSS single-page application
- Page routes: `/repository`, `/chat`, `/history`, `/models`, `/vector-store`, `/logs`, `/api-keys`, `/settings`, `/account`
- Sidebar navigation with `lucide-react` icons
- `ChatPage` — message input with typing indicator and Markdown rendering via `react-markdown` and `react-syntax-highlighter`
- `RepositoryPage` — repository path input and indexing trigger
- `VectorStorePage` — displays ChromaDB index status via `/index/status`
- Axios API client (`frontend/src/services/api.ts`) with 120-second timeout
- Dark/light theme support via `useTheme` hook

#### Configuration
- `app/config/embedding_config.py` — centralised embedding model settings
- `app/config/vectorstore_config.py` — ChromaDB directory and collection name
- `app/config/splitter_config.py` — chunk size, overlap, and separators
- `app/llm/llm_config.py` — LLM model name, temperature, top_p, max_tokens
- `.gitignore` covering Python, Node, React, ChromaDB, virtual environments, and model cache

#### Documentation
- `README.md` — project overview, setup instructions, and feature list
- `ARCHITECTURE.md` — system design and component interactions
- `API_DOCUMENTATION.md` — full REST API reference
- `PROJECT_STRUCTURE.md` — annotated directory tree
- `CONTRIBUTING.md` — contribution guidelines
- `ROADMAP.md` — planned features and milestones
- `CHANGELOG.md` — this file
- `LICENSE` — MIT License
- `docs/PHASE_1.md` — Phase 1 environment setup notes

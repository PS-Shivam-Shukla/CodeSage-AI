# Project Structure

Annotated directory tree for CodeSage AI.

```
CodeSage-AI/
│
├── main.py                          # FastAPI app entry point — CORS + router registration
├── CLI.py                           # Terminal interface — index + interactive Q&A without frontend
├── requirements.txt                 # Python backend dependencies
├── package.json                     # Root npm scripts (delegates to frontend/)
├── .env                             # Environment variables (not committed — see .gitignore)
├── .gitignore                       # Ignores: .venv, chroma_db, models, node_modules, dist, etc.
│
├── README.md                        # Project overview, setup, quick start
├── ARCHITECTURE.md                  # System design, component diagram, data flow
├── API_DOCUMENTATION.md             # Full REST API reference
├── PROJECT_STRUCTURE.md             # This file
├── CONTRIBUTING.md                  # Contribution guidelines
├── CHANGELOG.md                     # Version history
├── ROADMAP.md                       # Planned features and milestones
├── LICENSE                          # MIT License
│
├── app/                             # Backend application package
│   │
│   ├── api/                         # HTTP layer
│   │   ├── __init__.py              # Exports router
│   │   ├── routes.py                # Route handlers: /chat, /index, /index/status
│   │   └── schemas.py               # Pydantic request/response models
│   │
│   ├── config/                      # Centralised configuration (no magic numbers in logic)
│   │   ├── __init__.py
│   │   ├── embedding_config.py      # Embedding model name, device, normalization, cache path
│   │   ├── vectorstore_config.py    # ChromaDB persist dir + collection name
│   │   └── splitter_config.py       # Chunk size, overlap, separator list
│   │
│   ├── constants/                   # Shared constant keys
│   │   ├── __init__.py
│   │   └── metadata_key.py          # Chunk metadata keys (CHUNK_INDEX, CHUNK_LABEL, etc.)
│   │
│   ├── embeddings/                  # Embedding service
│   │   ├── __init__.py
│   │   └── embedding_service.py     # Loads BAAI/bge-m3 via HuggingFace with lru_cache
│   │
│   ├── indexing/                    # Orchestration layer for the indexing pipeline
│   │   ├── __init__.py
│   │   └── indexing.py              # IndexingService: ingest → split → store
│   │
│   ├── ingestion/                   # Repository document loading
│   │   ├── constants.py             # SUPPORTED_EXTENSIONS, IGNORED_DIRECTORIES, MAX_FILE_SIZE
│   │   ├── loaders.py               # load_pdf() and load_text_file() helpers
│   │   ├── metadata.py              # Metadata helpers for loaded documents
│   │   └── repository_ingestion.py  # RepositoryIngestionService — recursive file walker
│   │
│   ├── llm/                         # LLM layer
│   │   ├── __init__.py              # Exports LLMService
│   │   ├── config.py                # Re-exports from llm_config for internal use
│   │   ├── llm_config.py            # MODEL_NAME, TEMPERATURE, TOP_P, MAX_TOKENS
│   │   ├── llm_service.py           # LLMService — coordinates prompt + provider
│   │   ├── prompts/
│   │   │   ├── __init__.py
│   │   │   ├── prompt_service.py    # PromptService — builds LangChain prompt template
│   │   │   └── repository_qa.txt    # System prompt template with {context} and {question}
│   │   └── providers/
│   │       ├── __init__.py
│   │       └── nvidia_provider.py   # NVIDIAProvider — wraps ChatNVIDIA
│   │
│   ├── rag/                         # RAG pipeline
│   │   ├── __init__.py              # Exports RAGPipeline
│   │   └── rag_pipeline.py          # Retrieve → build context → generate answer
│   │
│   ├── retriever/                   # Retrieval service
│   │   ├── __init__.py
│   │   └── retrieval_service.py     # RetrievalService — top-k similarity search
│   │
│   ├── splitters/                   # Document chunking
│   │   ├── __init__.py
│   │   └── document_splitter.py     # DocumentSplitter — RecursiveCharacterTextSplitter + metadata
│   │
│   ├── utils/                       # Shared utility helpers
│   │
│   └── vectorstore/                 # Vector database abstraction
│       ├── __init__.py
│       └── chroma_service.py        # ChromaService — add_documents + similarity_search
│
├── frontend/                        # React 19 + TypeScript + Vite frontend
│   ├── index.html                   # Vite HTML entry point
│   ├── package.json                 # Frontend dependencies and npm scripts
│   ├── package-lock.json
│   ├── vite.config.ts               # Vite configuration
│   ├── tailwind.config.ts           # Tailwind CSS configuration
│   ├── postcss.config.js
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   └── src/
│       ├── main.tsx                 # React app entry point (ReactDOM.createRoot)
│       ├── App.tsx                  # Router setup — all page routes defined here
│       ├── styles/
│       │   └── globals.css          # Global Tailwind base styles
│       ├── layout/
│       │   └── Layout.tsx           # Shell layout — sidebar + topbar + <Outlet>
│       ├── components/              # Reusable UI components
│       │   ├── Sidebar.tsx          # Navigation sidebar
│       │   ├── Topbar.tsx           # Top navigation bar
│       │   ├── ChatInput.tsx        # Message input with send button
│       │   ├── ChatMessage.tsx      # Single chat message with Markdown support
│       │   ├── Navbar.tsx
│       │   ├── RepositoryCard.tsx
│       │   ├── StatusFooter.tsx
│       │   └── ui/                  # Primitive UI components
│       │       ├── button.tsx
│       │       ├── card.tsx
│       │       ├── EmptyState.tsx
│       │       ├── Loader.tsx
│       │       ├── Toast.tsx
│       │       ├── theme.tsx
│       │       └── TypingIndicator.tsx
│       ├── pages/                   # Route-level page components
│       │   ├── ChatPage.tsx         # /chat — main conversation interface
│       │   ├── RepositoryPage.tsx   # /repository — index a repository
│       │   ├── VectorStorePage.tsx  # /vector-store — view ChromaDB status
│       │   ├── HistoryPage.tsx      # /history
│       │   ├── ModelsPage.tsx       # /models
│       │   ├── LogsPage.tsx         # /logs
│       │   ├── ApiKeysPage.tsx      # /api-keys
│       │   ├── SettingsPage.tsx     # /settings
│       │   └── AccountPage.tsx      # /account
│       ├── services/                # API communication layer
│       │   ├── api.ts               # Axios base instance (baseURL + 120s timeout)
│       │   ├── chat.service.ts      # POST /chat
│       │   └── repository.service.ts # POST /index
│       ├── hooks/
│       │   └── useTheme.ts          # Dark/light theme toggle hook
│       ├── types/
│       │   └── index.ts             # Shared TypeScript type definitions
│       └── utils/
│           └── cn.ts                # Tailwind class merging utility (clsx + tailwind-merge)
│
├── scripts/                         # Utility scripts
│   ├── check_chroma.py              # Verify ChromaDB contents
│   ├── check_servers.py             # Check backend connectivity
│   └── poll_index_status.py         # Poll /index/status endpoint
│
├── tests/                           # Backend test suite
│   ├── test_embedding.py
│   ├── test_indexing.py
│   ├── test_rag.py
│   ├── test_repository_ingestion.py
│   └── test_retriever.py
│
├── docs/                            # Additional documentation
│   └── PHASE_1.md                   # Phase 1 environment setup notes
│
├── chroma_db/                       # ChromaDB local persistence (not committed)
├── models/                          # HuggingFace model cache (not committed)
├── .venv/                           # Python virtual environment (not committed)
└── .venv_backend/                   # Alternate Python virtual environment (not committed)
```

---

## Key Conventions

- All backend config lives in `app/config/` — no hard-coded values in business logic
- Each `app/` sub-package has a single responsibility and its own `__init__.py` exporting its public interface
- Frontend services (`src/services/`) are the only layer that touches the Axios client
- Page components in `src/pages/` are thin — heavy logic belongs in services or hooks
- Nothing under `chroma_db/`, `models/`, `.venv*`, `node_modules/`, or `dist/` is ever committed

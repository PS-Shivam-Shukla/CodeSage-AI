# Roadmap

This document outlines the planned features and milestones for CodeSage AI.

Status indicators: ✅ Done · 🚧 In Progress · 📋 Planned · 💡 Under Consideration

---

## Phase 1 — Foundation ✅

> Environment, architecture, and core RAG pipeline

| Feature | Status |
|---|---|
| FastAPI backend with CORS | ✅ |
| `POST /chat` — question answering endpoint | ✅ |
| `POST /index` — background repository indexing | ✅ |
| `GET /index/status` — ChromaDB status polling | ✅ |
| `BAAI/bge-m3` embeddings via HuggingFace | ✅ |
| ChromaDB local vector store | ✅ |
| `meta/llama-3.1-70b-instruct` via NVIDIA AI Endpoints | ✅ |
| RecursiveCharacterTextSplitter with code-aware separators | ✅ |
| Chunk metadata enrichment (index, label, total) | ✅ |
| Multi-format file ingestion (20 file types) | ✅ |
| PDF loading via PyPDF | ✅ |
| CLI interface (`CLI.py`) | ✅ |
| React 19 + TypeScript + Tailwind frontend | ✅ |
| Chat page with Markdown + syntax highlighting | ✅ |
| Repository indexing page | ✅ |
| Vector store status page | ✅ |
| `.gitignore` — excludes chroma_db, models, venvs, node_modules | ✅ |

---

## Phase 2 — Reliability & UX 📋

> Making the experience smoother and more production-ready

| Feature | Status |
|---|---|
| Streaming LLM responses (SSE / WebSocket) | 📋 |
| Indexing progress percentage via polling | 📋 |
| Error handling and user-facing error messages on the frontend | 📋 |
| Toast notifications for indexing and errors | 📋 |
| Conversation history — persist chat sessions locally | 📋 |
| Backend request logging middleware | 📋 |
| Configurable `k` (number of retrieved chunks) from frontend | 📋 |
| Unit test coverage for all backend services | 📋 |
| CI pipeline (GitHub Actions) — lint + test on push | 📋 |

---

## Phase 3 — Power Features 📋

> Expanding capability and flexibility

| Feature | Status |
|---|---|
| Multi-repository support — index and query multiple repos | 📋 |
| Repository switching from the frontend UI | 📋 |
| Re-indexing support — update existing collection without full reset | 📋 |
| CUDA / GPU acceleration for embeddings | 📋 |
| Source citation — show which file/chunk the answer came from | 📋 |
| Hybrid search — combine dense (vector) + sparse (BM25) retrieval | 📋 |
| Configurable LLM provider (OpenAI, Groq, Ollama) | 📋 |
| Configurable embedding model from the settings page | 📋 |
| API key management UI (fully functional) | 📋 |

---

## Phase 4 — Production & Deployment 💡

> Deploying CodeSage AI beyond localhost

| Feature | Status |
|---|---|
| Docker + Docker Compose setup | 💡 |
| Environment variable validation on startup | 💡 |
| Remote ChromaDB / Qdrant support | 💡 |
| Authentication (API key or JWT) | 💡 |
| Rate limiting on API endpoints | 💡 |
| Frontend build pipeline and static asset serving from FastAPI | 💡 |
| Helm chart for Kubernetes deployment | 💡 |
| Observability — structured logging + metrics (Prometheus/Grafana) | 💡 |

---

## Long-Term Ideas 💡

- VS Code extension for in-editor code Q&A
- GitHub App integration — automatically index PRs and repos
- Code generation mode — suggest fixes and improvements based on context
- Team collaboration — shared collections and chat history
- Fine-tuned embedding model on code-specific datasets

---

## Contributing to the Roadmap

Have a feature idea? Open an issue on GitHub with the label `enhancement` and describe the problem you are trying to solve. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

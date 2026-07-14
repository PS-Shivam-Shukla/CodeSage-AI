# CodeSage AI

## Overview

`CodeSage AI` is a Retrieval-Augmented Generation (RAG) application built with a FastAPI backend and a Vite + React frontend. The project ingests repository documents, indexes them in ChromaDB, and provides a conversational AI interface for user questions.

## Key Components

- **Backend**: Python, FastAPI, LangChain, ChromaDB
- **Frontend**: React 19, Vite, TypeScript, Tailwind CSS
- **Workflow**:
  1. Ingest documents from a repository
  2. Split documents into chunks
  3. Index chunks in ChromaDB
  4. Retrieve relevant chunks for a user query
  5. Generate an answer using an LLM

## Repository Structure

- `main.py` - FastAPI application entrypoint
- `app/` - backend modules and business logic
  - `api/` - HTTP routes and request/response schemas
  - `rag/` - retrieval and generation pipeline
  - `indexing/` - document indexing pipeline
  - `ingestion/`, `splitters/`, `vectorstore/` - document processing
- `frontend/` - React frontend application
- `requirements.txt` - backend dependencies
- `docs/` - supporting documentation
- `tests/` - backend tests

## Backend Setup

### Requirements

- Python 3.11+ recommended
- `pip` package manager
- `.env` file with environment variables

### Install Dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run Locally

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Backend API

- `POST /chat`
  - Request: `{ "question": "..." }`
  - Response: `{ "answer": "..." }`

## Frontend Setup

### Requirements

- Node.js 20+ recommended
- npm

### Install Dependencies

```powershell
cd frontend
npm install
```

### Run in Development

```powershell
npm run dev
```

### Build for Production

```powershell
npm run build
```

### Preview Production Build

```powershell
npm run preview
```

## Production Deployment

### Backend

- Use `uvicorn` or a production server such as `gunicorn` with Uvicorn workers
- Set environment variables securely through your host
- Use HTTPS and a reverse proxy (Nginx, Traefik, Cloudflare)

Example production start:

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

- Build the frontend with `npm run build`
- Serve static assets from a CDN or a web server
- Use the built `dist/` folder in production hosting

### Docker (Recommended for Production)

- Build container images for backend and frontend
- Use a multi-container setup or static file hosting for the frontend
- Ensure environment variables are passed securely at runtime

## Environment Variables

Create a `.env` file in the project root for backend configuration. Typical keys may include:

```text
OPENAI_API_KEY=...
NVIDIA_API_KEY=...
CHROMA_SETTING=...
```

> Note: This repository currently uses LangChain and NVIDIA AI endpoint logic. Adjust `.env` contents to match your provider configuration.

## Important Notes

- The frontend uses Vite path aliasing with `@` mapped to `src/`.
- `frontend/package.json` includes `build` scripts that run TypeScript project references and Vite.
- Backend code uses a `RAGPipeline` abstraction to chain retrieval and generation.
- For production stability, enable `skipLibCheck` only in development if needed and keep dependencies updated.

## Developer Workflow

1. Start the backend
2. Start the frontend
3. Index documents if necessary
4. Use the frontend chat interface against the backend API

## Testing

- Backend tests should live in `tests/`
- Run Python tests via your preferred test runner

## Troubleshooting

- If TypeScript reports deprecated options in `frontend/tsconfig.app.json`, update the config to use modern settings and `ignoreDeprecations: "6.0"` as needed.
- If frontend alias imports fail, ensure `frontend/vite.config.ts` includes an alias for `@`.
- If packages are missing, rerun `npm install` in the `frontend` folder.

## Contact

For production support, review the `docs/` folder and update the root README with environment-specific deployment details.

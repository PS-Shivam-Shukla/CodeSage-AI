# CodeSage AI

> Advanced RAG (Retrieval-Augmented Generation) system for intelligent code repository analysis

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-blue.svg)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Features

- **Intelligent Code Analysis**: Query your codebase using natural language
- **Advanced RAG Pipeline**: Optimized retrieval with query expansion and multi-query search
- **Comprehensive Evaluation**: Built-in metrics for answer quality and relevance
- **Production-Ready**: Rate limiting, retry logic, and error handling
- **Modern Stack**: FastAPI backend + React frontend with TypeScript

## 📋 Prerequisites

- **Python 3.11+** (backend)
- **Node.js 20+** (frontend)
- **NVIDIA API Key** (for LLM access)

## 🔧 Installation

### Backend Setup

```bash
# Create and activate virtual environment
python -m venv .venv_backend
.\.venv_backend\Scripts\Activate.ps1  # Windows PowerShell
# source .venv_backend/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
# Required
NVIDIA_API_KEY=your_nvidia_api_key_here

# Optional - Model Configuration
EVAL_LLM_MODEL=meta/llama-3.1-70b-instruct
EVAL_LLM_TEMPERATURE=0.1
EVAL_LLM_MAX_TOKENS=512

# Optional - Chunking Configuration
DEFAULT_CHUNK_SIZE=600
DEFAULT_CHUNK_OVERLAP=150

# Optional - Retrieval Configuration
DEFAULT_K=10
```

## 🚀 Quick Start

### 1. Start Backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`

### 2. Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at `http://localhost:5173`

### 3. Index a Repository

```python
from app.indexing.indexing import IndexingService

service = IndexingService()
service.index_repository("path/to/your/repository")
```

Or use the API:

```bash
curl -X POST "http://localhost:8000/index" \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "path/to/your/repository"}'
```

### 4. Query Your Code

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main architecture of this project?"}'
```

## 📊 Evaluation

Run comprehensive evaluation metrics:

```bash
python run_evaluation.py
```

For quick testing:

```bash
python quick_test.py
```

Results are saved in `evaluation_reports/`

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                    (React + TypeScript)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────┐
│                     FastAPI Backend                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌─────────────┐    ┌──────────────┐  │
│  │ Indexing     │───▶│ ChromaDB    │◀───│ Retrieval    │  │
│  │ Service      │    │ (Vectors)   │    │ Service      │  │
│  └──────────────┘    └─────────────┘    └──────┬───────┘  │
│                                                  │          │
│  ┌──────────────┐    ┌─────────────┐    ┌──────▼───────┐  │
│  │ Query        │───▶│ RAG         │◀───│ Embedding    │  │
│  │ Expander     │    │ Pipeline    │    │ Service      │  │
│  └──────────────┘    └──────┬──────┘    └──────────────┘  │
│                             │                              │
│                      ┌──────▼───────┐                      │
│                      │ NVIDIA LLM   │                      │
│                      │ (Llama 3.1)  │                      │
│                      └──────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
CodeSage-AI/
├── app/
│   ├── api/              # API routes and schemas
│   ├── config/           # Configuration files
│   ├── embeddings/       # Embedding service
│   ├── evaluation/       # Evaluation metrics
│   ├── indexing/         # Document indexing
│   ├── ingestion/        # Document loading
│   ├── llm/              # LLM integration
│   ├── rag/              # RAG pipeline
│   ├── retriever/        # Retrieval + query expansion
│   ├── splitters/        # Document chunking
│   ├── utils/            # Utilities (caching, retry logic)
│   └── vectorstore/      # ChromaDB interface
├── frontend/             # React frontend
├── evaluation_reports/   # Evaluation results
├── chroma_db/           # Vector database
├── main.py              # FastAPI entry point
├── run_evaluation.py    # Evaluation runner
└── quick_test.py        # Quick validation script
```

## 🔑 Key Features

### Advanced Retrieval
- **Query Expansion**: Automatically enhances queries with relevant terms
- **Multi-Query Retrieval**: Generates multiple query variations for better recall
- **Intelligent Chunking**: Python-aware code splitting (600 chars with 150 overlap)
- **Retrieves 10 documents** by default for comprehensive context

### Production Reliability
- **Retry Logic**: Automatic retry with exponential backoff for API failures
- **Rate Limiting**: Built-in delays to prevent 429 errors
- **Embedding Cache**: In-memory LRU cache (1000 entries) for faster responses
- **Batch Processing**: Efficient memory management during indexing

### Comprehensive Evaluation
- **7 Quality Metrics**: Context precision, recall, faithfulness, relevancy, correctness, reasoning quality, hallucination rate
- **Detailed Reports**: JSON reports with scores, latency, and explanations
- **Ground Truth Support**: Compare answers against expected results

## 📈 Performance

### Typical Metrics

| Metric | Score | Grade |
|--------|-------|-------|
| Context Precision | 0.40-0.60 | Average-Good |
| Context Recall | 0.50-0.70 | Average-Good |
| Faithfulness | 0.45-0.65 | Average-Good |
| Answer Relevancy | 0.65-0.80 | Good |
| Answer Correctness | 0.60-0.75 | Good |
| Reasoning Quality | 0.70-0.95 | Good-Excellent |

### Response Times
- **Retrieval**: 100-500ms (with cache hits)
- **End-to-End**: 1.5-10s (depending on complexity)

## 🛠️ API Endpoints

### Chat
```http
POST /chat
Content-Type: application/json

{
  "question": "How is authentication implemented?"
}
```

### Index Repository
```http
POST /index
Content-Type: application/json

{
  "repository_path": "/path/to/repo"
}
```

### Check Index Status
```http
GET /index/status
```

## 🧪 Testing

### Unit Tests
```bash
pytest tests/
```

### Quick Validation
```bash
python quick_test.py
```

### Full Evaluation
```bash
python run_evaluation.py
```

## 📦 Production Deployment

### Backend

```bash
# Use gunicorn with uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend

```bash
cd frontend
npm run build
# Serve dist/ folder with nginx or CDN
```

### Environment Variables (Production)

- Set `NVIDIA_API_KEY` securely via environment
- Configure `EVAL_LLM_TIMEOUT` for network latency
- Adjust `DEFAULT_K` based on context requirements
- Enable HTTPS with reverse proxy (nginx, Traefik)

## 🔍 Troubleshooting

### Issue: Slow Indexing
- **Check exclusions** in `app/ingestion/constants.py`
- Ensure virtual environments are excluded
- Use smaller repositories for testing first

### Issue: Low Evaluation Scores
- **Re-index** with current chunking parameters
- Verify query expansion is enabled
- Check if k=10 documents are being retrieved
- Ensure NVIDIA API key is valid

### Issue: 429 Rate Limit Errors
- Retry logic should handle automatically
- Increase delay in `run_evaluation.py` if needed
- Check API quota and limits

### Issue: High Memory Usage
- Reduce batch size in `app/config/vectorstore_config.py`
- Clear embedding cache: restart application
- Use smaller chunk size if needed

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See `CONTRIBUTING.md` for detailed guidelines.

## 📞 Support

For issues and questions:
- **Issues**: Open an issue on GitHub
- **Documentation**: Check `docs/` folder
- **Evaluation**: Review reports in `evaluation_reports/`

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Powered by [NVIDIA AI Endpoints](https://build.nvidia.com/)
- Vector storage by [ChromaDB](https://www.trychroma.com/)
- Embeddings by [HuggingFace](https://huggingface.co/) (BAAI/bge-m3)

---

**Made with ❤️ for developers who want to understand their code better**

# Contributing to CodeSage AI

Thank you for your interest in contributing. This document covers everything you need to get started.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Branch Naming](#branch-naming)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

---

## Code of Conduct

Be respectful and constructive. Harassment of any kind will not be tolerated.

---

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/CodeSage-AI.git
   cd CodeSage-AI
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/PS-Shivam-Shukla/CodeSage-AI.git
   ```

---

## Development Setup

### Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the root with your `NVIDIA_API_KEY`.

Start the backend:

```powershell
uvicorn main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

---

## Branch Naming

Use the following prefixes:

| Prefix | Purpose |
|---|---|
| `feat/` | New features |
| `fix/` | Bug fixes |
| `docs/` | Documentation changes |
| `refactor/` | Code refactoring without behaviour change |
| `chore/` | Build system, dependency updates |
| `test/` | Adding or improving tests |

Example: `feat/streaming-responses`

---

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(optional scope): <short summary>
```

Examples:

```
feat(api): add streaming support to /chat endpoint
fix(indexing): handle empty repository path gracefully
docs: update API documentation for /index/status
chore(deps): upgrade langchain to latest
```

---

## Pull Request Process

1. Sync your fork with upstream before starting work:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```
2. Create a new branch from `main`
3. Make your changes — keep commits atomic and focused
4. Ensure the backend starts without errors: `uvicorn main:app --reload`
5. Ensure the frontend builds without errors: `npm run build` (inside `frontend/`)
6. Open a PR against `main` with a clear description of what changed and why
7. Link any related issues in the PR description

---

## Code Style

### Python

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints on all function signatures
- Write docstrings for all public classes and methods
- Keep modules focused — one responsibility per file
- Use `lru_cache` or similar patterns to avoid re-loading heavy resources (e.g. embedding models)

### TypeScript / React

- Prefer functional components and hooks
- Keep components small and single-purpose
- Use `const` over `let` where possible
- Name files with PascalCase for components, camelCase for utilities and services

---

## Reporting Bugs

Open an issue on GitHub with the following information:

- OS and Python/Node.js version
- Steps to reproduce
- Expected behaviour
- Actual behaviour
- Any relevant error logs or screenshots

---

## Suggesting Features

Open an issue with the label `enhancement`. Describe:

- The problem you are trying to solve
- Your proposed solution
- Any alternatives you considered

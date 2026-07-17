# Contributing to CodeSage AI

Thank you for your interest in contributing to CodeSage AI! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/CodeSage-AI.git
   cd CodeSage-AI
   ```
3. **Set up development environment**:
   ```bash
   python -m venv .venv_backend
   .\.venv_backend\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

## 📝 Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `perf/` - Performance improvements
- `refactor/` - Code refactoring

### 2. Make Your Changes

- Write clear, commented code
- Follow existing code style and patterns
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run tests
pytest tests/

# Quick validation
python quick_test.py

# Full evaluation
python run_evaluation.py
```

### 4. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git commit -m "Add query expansion for API-related terms"
git commit -m "Fix: Handle empty context in retrieval service"
git commit -m "Docs: Update README with new configuration options"
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear description of changes
- Any related issue numbers
- Screenshots (if UI changes)
- Test results

## 🧪 Testing Guidelines

### Unit Tests

```python
# tests/test_retrieval.py
def test_query_expansion():
    expander = QueryExpander()
    queries = expander.expand_query("What is API?")
    assert len(queries) > 1
    assert any("endpoint" in q.lower() for q in queries)
```

### Integration Tests

```python
# tests/test_pipeline.py
def test_rag_pipeline_with_expansion():
    pipeline = RAGPipeline()
    result = pipeline.ask_with_context("How does auth work?", k=10)
    assert len(result.contexts) == 10
    assert result.answer is not None
```

## 📐 Code Style

### Python

- Follow [PEP 8](https://pep8.org/)
- Use type hints where possible
- Maximum line length: 100 characters
- Use docstrings for all public functions/classes

Example:

```python
def expand_query(query: str, use_acronyms: bool = True) -> List[str]:
    """
    Expand user query into multiple variations.
    
    Args:
        query: Original user question
        use_acronyms: Whether to expand acronyms
        
    Returns:
        List of query variations
    """
    pass
```

### TypeScript (Frontend)

- Use TypeScript strict mode
- Follow React best practices
- Use functional components with hooks
- Maximum line length: 100 characters

## 🏗️ Architecture Guidelines

### Adding New Features

1. **Retrieval Enhancement**:
   - Add to `app/retriever/`
   - Update `RetrievalService` class
   - Add tests in `tests/test_retrieval.py`

2. **Evaluation Metrics**:
   - Add to `app/evaluation/`
   - Integrate with `EvaluationService`
   - Document in evaluation config

3. **API Endpoints**:
   - Add to `app/api/routes.py`
   - Define schemas in `app/api/schemas.py`
   - Update API documentation

### Performance Considerations

- Use caching where appropriate
- Implement batch processing for bulk operations
- Add retry logic for external API calls
- Consider memory usage for large repositories

## 📊 Evaluation Standards

All changes should maintain or improve:
- Context Precision (target: >0.40)
- Context Recall (target: >0.50)
- Overall Average Score (target: >0.50)
- Response Time (target: <10s)

Run evaluation before submitting PR:

```bash
python run_evaluation.py
```

## 🐛 Bug Reports

When reporting bugs, include:
- **Description**: Clear description of the issue
- **Steps to Reproduce**: Exact steps to reproduce the bug
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, dependencies
- **Logs**: Relevant error messages or logs

## 💡 Feature Requests

When proposing features:
- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: What other approaches were considered?
- **Impact**: How does this affect existing functionality?

## 📚 Documentation

Update documentation when:
- Adding new features
- Changing API endpoints
- Modifying configuration options
- Improving performance

Documentation locations:
- `README.md` - Main documentation
- `CHANGELOG.md` - Version history
- Code docstrings - Inline documentation
- `docs/` - Detailed guides (if applicable)

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🤝 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the issue, not the person
- Help others learn and grow

## 📞 Questions?

If you have questions:
- Open an issue on GitHub
- Check existing issues and discussions
- Review the README and documentation

## 🙏 Thank You!

Your contributions make CodeSage AI better for everyone. We appreciate your time and effort!

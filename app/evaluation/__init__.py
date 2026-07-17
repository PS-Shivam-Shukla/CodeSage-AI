"""
app/evaluation/__init__.py
==========================

Public API for the CodeSage AI Evaluation Framework.

This module is fully independent of the RAG pipeline.
It consumes the structured output of the pipeline (RAGResult)
and produces scored, graded EvaluationResult objects.

Quick start
-----------
    from app.evaluation import EvaluationService
    from app.rag import RAGPipeline

    # 1. Run the RAG pipeline with structured output
    pipeline = RAGPipeline()
    rag_result = pipeline.ask_with_context(
        question="How is JWT authentication implemented?",
        ground_truth="JWT tokens are verified via middleware.",  # optional
        repository_name="MyApp",
    )

    # 2. Evaluate
    service = EvaluationService()
    eval_result = service.evaluate(rag_result)

    # 3. Report
    from app.evaluation import ReportGenerator
    ReportGenerator.print_console(eval_result)
    ReportGenerator.save_json(eval_result)
    ReportGenerator.save_markdown(eval_result)
"""

from app.evaluation.models import (
    EvaluationInput,
    MetricScore,
    EvaluationResult,
)
from app.evaluation.evaluation_service import EvaluationService
from app.evaluation.report_generator import ReportGenerator

__all__ = [
    # Data models
    "EvaluationInput",
    "MetricScore",
    "EvaluationResult",
    # Core service
    "EvaluationService",
    # Reporting
    "ReportGenerator",
]

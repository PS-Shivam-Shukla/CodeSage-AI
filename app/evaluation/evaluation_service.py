"""
app/evaluation/evaluation_service.py
======================================

The single public entry point for the CodeSage AI Evaluation Framework.

Architecture
------------

    RAGPipeline.ask_with_context()
            │
            ▼
        RAGResult
            │
            ▼
    EvaluationService.evaluate(rag_result)
            │
            ├── EvaluationAdapter.run()     ← 5 quality metrics
            │       └── manual evaluation   ← NVIDIA LLM + bge-m3 as judges
            │
            ├── ReasoningEvaluator.evaluate()  ← LLM-as-a-Judge rubric
            │
            ├── _compute_hallucination_rate()  ← derived from faithfulness
            │
            ├── _compute_weighted_average()    ← config.METRIC_WEIGHTS
            │
            └── EvaluationResult               ← returned to caller

Design decisions
----------------
1. Lazy initialisation: EvaluationAdapter and ReasoningEvaluator are only
   instantiated when evaluate() is first called, not at import time.
   This means importing the module never triggers LLM or model loading.

2. Independent metric failures: If evaluation adapter fails, ReasoningEvaluator still
   runs. If ReasoningEvaluator fails, evaluation scores are still returned.
   Each component fails in isolation; the EvaluationResult is always
   returned with whatever scores could be computed.

3. Weighted average excludes None scores and hallucination_rate.
   hallucination_rate is a derived metric (1 - faithfulness), not an
   independent measurement, so including it would double-count faithfulness.

4. Stateless design: No instance variables mutated after __init__.
   Safe to share a single EvaluationService across FastAPI requests.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.evaluation.config import (
    METRIC_WEIGHTS,
    SCORE_DECIMAL_PLACES,
    grade_from_average,
    label_from_score,
)
from app.evaluation.models import (
    EvaluationInput,
    EvaluationResult,
    MetricScore,
)
from app.evaluation.evaluation_adapter import EvaluationAdapter
from app.evaluation.reasoning_evaluator import ReasoningEvaluator

logger = logging.getLogger(__name__)


class EvaluationService:
    """
    Orchestrates all evaluation components and returns a complete
    EvaluationResult for a single RAG response.

    This is the ONLY class external code needs to import for evaluation.

    Usage — from a RAGResult (recommended)
    ---------------------------------------
        from app.evaluation import EvaluationService
        from app.rag import RAGPipeline

        pipeline = RAGPipeline()
        rag_result = pipeline.ask_with_context(
            question     = "How is JWT auth implemented?",
            ground_truth = "JWT tokens are verified via middleware.",
        )

        service    = EvaluationService()
        result     = service.evaluate(rag_result)

        print(result.overall_grade)        # "A+"
        print(result.faithfulness.score)   # 0.94
        print(result.average_score)        # 0.91

    Usage — from raw strings (convenience)
    ----------------------------------------
        result = service.evaluate_from_raw(
            question     = "How is JWT auth implemented?",
            answer       = "The app uses JWT tokens...",
            contexts     = ["JWT tokens are issued on login...", "..."],
            ground_truth = "JWT-based auth via middleware.",
        )

    Accessing reports
    -----------------
        from app.evaluation import ReportGenerator
        ReportGenerator.print_console(result)
        ReportGenerator.save_json(result)
        ReportGenerator.save_markdown(result)
    """

    def __init__(self) -> None:
        """
        Initialise the EvaluationService.

        Component instances (EvaluationAdapter, ReasoningEvaluator) are
        created lazily on the first evaluate() call to avoid loading
        models at import time.
        """
        self._evaluation_adapter: Optional[EvaluationAdapter] = None
        self._reasoner:  Optional[ReasoningEvaluator] = None

    # -----------------------------------------------------------------------
    # Primary public method — accepts RAGResult
    # -----------------------------------------------------------------------

    def evaluate(self, rag_result: object) -> EvaluationResult:
        """
        Evaluate a RAG pipeline response represented as a RAGResult.

        Accepts the ``RAGResult`` dataclass produced by
        ``RAGPipeline.ask_with_context()``.

        Args:
            rag_result: A ``RAGResult`` instance from the RAG pipeline.

        Returns:
            A fully populated ``EvaluationResult``.
        """
        # Import here to avoid circular imports at module level
        from app.rag.rag_pipeline import RAGResult

        if not isinstance(rag_result, RAGResult):
            raise TypeError(
                f"Expected RAGResult, got {type(rag_result).__name__}.\n"
                f"Use RAGPipeline.ask_with_context() to get a RAGResult."
            )

        return self._run_evaluation(
            question             = rag_result.question,
            answer               = rag_result.answer,
            contexts             = rag_result.contexts,
            ground_truth         = rag_result.ground_truth,
            repository_name      = rag_result.repository_name,
            retrieval_latency_ms = rag_result.retrieval_latency_ms,
            response_time_ms     = rag_result.response_time_ms,
        )

    # -----------------------------------------------------------------------
    # Convenience method — accepts raw strings
    # -----------------------------------------------------------------------

    def evaluate_from_raw(
        self,
        question:             str,
        answer:               str,
        contexts:             list[str],
        ground_truth:         Optional[str]   = None,
        repository_name:      Optional[str]   = None,
        retrieval_latency_ms: Optional[float] = None,
        response_time_ms:     Optional[float] = None,
    ) -> EvaluationResult:
        """
        Evaluate a RAG response from raw string arguments.

        Convenience wrapper for scripts, notebooks, and tests where
        constructing a RAGResult object is unnecessary.

        Args:
            question:             The user question.
            answer:               The LLM-generated answer.
            contexts:             List of retrieved chunk strings.
            ground_truth:         Expected answer (optional).
            repository_name:      Label shown in reports (optional).
            retrieval_latency_ms: Vector search time in ms (optional).
            response_time_ms:     End-to-end time in ms (optional).

        Returns:
            A fully populated ``EvaluationResult``.
        """
        return self._run_evaluation(
            question             = question,
            answer               = answer,
            contexts             = contexts,
            ground_truth         = ground_truth,
            repository_name      = repository_name,
            retrieval_latency_ms = retrieval_latency_ms,
            response_time_ms     = response_time_ms,
        )

    # -----------------------------------------------------------------------
    # Core evaluation logic
    # -----------------------------------------------------------------------

    def _run_evaluation(
        self,
        question:             str,
        answer:               str,
        contexts:             list[str],
        ground_truth:         Optional[str],
        repository_name:      Optional[str],
        retrieval_latency_ms: Optional[float],
        response_time_ms:     Optional[float],
    ) -> EvaluationResult:
        """
        Execute all evaluation components and assemble EvaluationResult.

        Steps
        -----
        1. Lazily initialise EvaluationAdapter and ReasoningEvaluator.
        2. Run evaluation adapter (5 metrics) — catches and logs any failure.
        3. Run ReasoningEvaluator — catches and logs any failure.
        4. Derive hallucination_rate from faithfulness score.
        5. Wrap each raw score in a MetricScore (score + label).
        6. Compute weighted average (excluding None + hallucination_rate).
        7. Derive overall grade from average.
        8. Return EvaluationResult.
        """
        logger.info(
            "Evaluation started  |  question=%.80s  ground_truth=%s",
            question,
            "yes" if ground_truth else "no",
        )

        # ── Step 1: lazy init ────────────────────────────────────────────────
        self._ensure_components_initialised()

        # ── Step 2: evaluation metrics ──────────────────────────────────────────
        evaluation_scores = self._run_evaluation_adapter_safely(
            question=question,
            answer=answer,
            contexts=contexts,
            ground_truth=ground_truth,
        )

        # ── Step 3: reasoning quality (LLM-as-a-Judge) ──────────────────────
        reasoning_metric = self._run_reasoning_safely(
            question=question,
            answer=answer,
            contexts=contexts,
        )

        # ── Step 4: derive hallucination rate ────────────────────────────────
        faithfulness_score = evaluation_scores.get("faithfulness")
        hallucination_score = (
            round(1.0 - faithfulness_score, SCORE_DECIMAL_PLACES)
            if faithfulness_score is not None
            else None
        )

        # ── Step 5: build MetricScore objects ────────────────────────────────
        context_precision = MetricScore(
            name  = "Context Precision",
            score = evaluation_scores.get("context_precision"),
            label = label_from_score(evaluation_scores.get("context_precision")),
        )
        context_recall = MetricScore(
            name  = "Context Recall",
            score = evaluation_scores.get("context_recall"),
            label = label_from_score(evaluation_scores.get("context_recall")),
        )
        faithfulness = MetricScore(
            name  = "Faithfulness",
            score = faithfulness_score,
            label = label_from_score(faithfulness_score),
        )
        answer_relevancy = MetricScore(
            name  = "Answer Relevancy",
            score = evaluation_scores.get("answer_relevancy"),
            label = label_from_score(evaluation_scores.get("answer_relevancy")),
        )
        answer_correctness = MetricScore(
            name  = "Answer Correctness",
            score = evaluation_scores.get("answer_correctness"),
            label = label_from_score(evaluation_scores.get("answer_correctness")),
        )
        hallucination_rate = MetricScore(
            name  = "Hallucination Rate",
            score = hallucination_score,
            # Lower is better for hallucination rate, but we store it raw.
            # The report generator renders it as "X% hallucination detected".
            label = self._hallucination_label(hallucination_score),
        )

        # ── Step 6: weighted average ─────────────────────────────────────────
        average_score = self._compute_weighted_average(
            precision   = evaluation_scores.get("context_precision"),
            recall      = evaluation_scores.get("context_recall"),
            faithfulness_val = faithfulness_score,
            relevancy   = evaluation_scores.get("answer_relevancy"),
            correctness = evaluation_scores.get("answer_correctness"),
            reasoning   = reasoning_metric.score,
        )

        # ── Step 7: overall grade ────────────────────────────────────────────
        overall_grade = grade_from_average(average_score)

        # ── Step 8: assemble and return ──────────────────────────────────────
        result = EvaluationResult(
            question             = question,
            repository_name      = repository_name,
            context_precision    = context_precision,
            context_recall       = context_recall,
            faithfulness         = faithfulness,
            answer_relevancy     = answer_relevancy,
            answer_correctness   = answer_correctness,
            hallucination_rate   = hallucination_rate,
            reasoning_quality    = reasoning_metric,
            retrieval_latency_ms = retrieval_latency_ms,
            response_time_ms     = response_time_ms,
            average_score        = average_score,
            overall_grade        = overall_grade,
        )

        logger.info(
            "Evaluation complete  |  grade=%s  average=%.2f",
            result.overall_grade,
            result.average_score or 0.0,
        )
        return result

    # -----------------------------------------------------------------------
    # Component runners with individual error isolation
    # -----------------------------------------------------------------------

    def _run_evaluation_adapter_safely(
        self,
        question:     str,
        answer:       str,
        contexts:     list[str],
        ground_truth: Optional[str],
    ) -> dict[str, Optional[float]]:
        """
        Run EvaluationAdapter.run() and return scores dict.

        Returns all-None dict on any failure so the rest of the
        evaluation can continue.
        """
        empty: dict[str, Optional[float]] = {
            "context_precision":  None,
            "context_recall":     None,
            "faithfulness":       None,
            "answer_relevancy":   None,
            "answer_correctness": None,
        }
        try:
            return self._evaluation_adapter.run(  # type: ignore[union-attr]
                question     = question,
                answer       = answer,
                contexts     = contexts,
                ground_truth = ground_truth,
            )
        except Exception as exc:
            logger.error("Evaluation adapter failed: %s", exc)
            return empty

    def _run_reasoning_safely(
        self,
        question: str,
        answer:   str,
        contexts: list[str],
    ) -> MetricScore:
        """
        Run ReasoningEvaluator.evaluate() and return MetricScore.

        Returns N/A MetricScore on any failure.
        """
        try:
            return self._reasoner.evaluate(  # type: ignore[union-attr]
                question = question,
                answer   = answer,
                contexts = contexts,
            )
        except Exception as exc:
            logger.error("ReasoningEvaluator failed: %s", exc)
            return MetricScore(
                name        = "Reasoning Quality",
                score       = None,
                label       = "N/A",
                explanation = f"Evaluation failed: {exc}",
            )

    # -----------------------------------------------------------------------
    # Lazy initialisation
    # -----------------------------------------------------------------------

    def _ensure_components_initialised(self) -> None:
        """
        Initialise EvaluationAdapter and ReasoningEvaluator on first call.

        Lazy init means importing EvaluationService never loads the LLM
        or embedding model — only the first evaluate() call triggers that.
        This keeps startup time fast and avoids loading models in tests
        that mock these components.
        """
        if self._evaluation_adapter is None:
            logger.info("Initialising EvaluationAdapter...")
            self._evaluation_adapter = EvaluationAdapter()

        if self._reasoner is None:
            logger.info("Initialising ReasoningEvaluator...")
            self._reasoner = ReasoningEvaluator()

    # -----------------------------------------------------------------------
    # Private computation helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _compute_weighted_average(
        precision:        Optional[float],
        recall:           Optional[float],
        faithfulness_val: Optional[float],
        relevancy:        Optional[float],
        correctness:      Optional[float],
        reasoning:        Optional[float],
    ) -> Optional[float]:
        """
        Compute the weighted average of all quality metric scores.

        Rules:
        - Metrics with score=None are excluded from both numerator
          and denominator — they are NOT treated as zero.
        - hallucination_rate is excluded (derived, not independent).
        - Returns None if every metric score is None.

        Args:
            precision:        Context Precision score or None.
            recall:           Context Recall score or None.
            faithfulness_val: Faithfulness score or None.
            relevancy:        Answer Relevancy score or None.
            correctness:      Answer Correctness score or None.
            reasoning:        Reasoning Quality score or None.

        Returns:
            Weighted average in [0.0, 1.0] or None.
        """
        candidates = [
            ("context_precision",  precision),
            ("context_recall",     recall),
            ("faithfulness",       faithfulness_val),
            ("answer_relevancy",   relevancy),
            ("answer_correctness", correctness),
            ("reasoning_quality",  reasoning),
        ]

        weighted_sum  = 0.0
        total_weight  = 0.0

        for key, score in candidates:
            if score is None:
                continue
            weight        = METRIC_WEIGHTS.get(key, 1.0)
            weighted_sum += score * weight
            total_weight += weight

        if total_weight == 0.0:
            return None

        return round(weighted_sum / total_weight, SCORE_DECIMAL_PLACES)

    @staticmethod
    def _hallucination_label(rate: Optional[float]) -> str:
        """
        Convert a hallucination rate (0.0 = none, 1.0 = full) to a label.

        Inverted thresholds: a LOW hallucination rate is GOOD.

            rate <= 0.05  →  "Excellent"  (< 5% hallucination)
            rate <= 0.15  →  "Good"       (< 15%)
            rate <= 0.30  →  "Average"    (< 30%)
            rate >  0.30  →  "Poor"

        Args:
            rate: Hallucination rate in [0.0, 1.0], or None.

        Returns:
            Quality label string.
        """
        if rate is None:
            return "N/A"
        if rate <= 0.05:
            return "Excellent"
        if rate <= 0.15:
            return "Good"
        if rate <= 0.30:
            return "Average"
        return "Poor"

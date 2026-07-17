"""
app/evaluation/models.py
========================

All Pydantic data models for the CodeSage AI Evaluation Framework.

Why Pydantic?
-------------
- Automatic type validation at runtime (catches bad data early)
- Free .model_dump() / .model_dump_json() for JSON serialisation
- Self-documenting via field descriptions
- Works seamlessly with FastAPI if evaluation is later exposed via API

Three models, three responsibilities
-------------------------------------
    EvaluationInput   →  what goes IN   (built from RAGResult)
    MetricScore       →  one scored metric (value + label + explanation)
    EvaluationResult  →  what comes OUT  (all scores + grade + metadata)
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# EvaluationInput
# ---------------------------------------------------------------------------

class EvaluationInput(BaseModel):
    """
    Everything the Evaluation Framework needs to evaluate one RAG response.

    This is built by EvaluationService from a RAGResult.
    Ground truth is optional — metrics requiring it are skipped gracefully.

    Fields
    ------
    question          : The original user question.
    answer            : The LLM-generated answer.
    contexts          : List of individual chunk strings retrieved from ChromaDB.
                        RAGAS expects list[str], not a single joined string.
    ground_truth      : Expected correct answer (optional).
                        Required by ContextRecall and AnswerCorrectness.
                        If None those metrics are skipped without error.
    repository_name   : Human-readable label shown in reports (optional).
    retrieval_latency_ms : Time taken for vector search in milliseconds.
    response_time_ms     : Total end-to-end time in milliseconds.
    """

    question:             str              = Field(..., min_length=1)
    answer:               str              = Field(..., min_length=1)
    contexts:             list[str]        = Field(..., min_length=1)
    ground_truth:         Optional[str]    = Field(default=None)
    repository_name:      Optional[str]    = Field(default=None)
    retrieval_latency_ms: Optional[float]  = Field(default=None, ge=0.0)
    response_time_ms:     Optional[float]  = Field(default=None, ge=0.0)


# ---------------------------------------------------------------------------
# MetricScore
# ---------------------------------------------------------------------------

class MetricScore(BaseModel):
    """
    The result of evaluating one individual metric.

    Keeps the raw numeric score, the human-readable label, and an
    optional explanation together so the report generator never needs
    to re-derive any of these from the number alone.

    Fields
    ------
    name        : Metric name, e.g. "Faithfulness".
    score       : Normalised score in [0.0, 1.0].
                  None when the metric was intentionally skipped
                  (e.g. Answer Correctness without ground truth).
    label       : "Excellent" / "Good" / "Average" / "Poor" / "N/A".
    explanation : Optional free-text explanation from LLM-as-a-Judge.
                  Present for Reasoning Quality; None for RAGAS metrics.
    """

    name:        str            = Field(..., description="Metric name.")
    score:       Optional[float] = Field(
        default=None,
        description="Score in [0.0, 1.0]. None = metric skipped.",
        ge=0.0,
        le=1.0,
    )
    label:       str            = Field(default="N/A")
    explanation: Optional[str]  = Field(default=None)

    @field_validator("score", mode="before")
    @classmethod
    def clamp_score(cls, v: Optional[float]) -> Optional[float]:
        """
        Clamp score to [0.0, 1.0].

        RAGAS occasionally returns values just outside this range due to
        floating-point arithmetic. Clamping prevents downstream assertion
        failures without hiding real errors.
        """
        if v is None:
            return None
        return max(0.0, min(1.0, float(v)))


# ---------------------------------------------------------------------------
# EvaluationResult
# ---------------------------------------------------------------------------

class EvaluationResult(BaseModel):
    """
    The complete output of evaluating one RAG response.

    Returned by EvaluationService.evaluate().
    Contains every MetricScore plus aggregate fields and metadata.

    Quality metrics (RAGAS)
    -----------------------
    context_precision   : Signal-to-noise of retrieved chunks.
    context_recall      : Coverage — did we retrieve everything needed?
    faithfulness        : Is every claim grounded in context? (anti-hallucination)
    answer_relevancy    : Does the answer address the question?
    answer_correctness  : How close to ground truth? (skipped if no ground truth)

    Derived metrics
    ---------------
    hallucination_rate  : 1.0 - faithfulness.score  (0.0 = no hallucination)
    reasoning_quality   : LLM-as-a-Judge score with explanation text.

    Latency
    -------
    retrieval_latency_ms : Vector search time.
    response_time_ms     : End-to-end time.

    Aggregates
    ----------
    average_score  : Weighted mean of all non-None quality scores.
    overall_grade  : A+ / A / B / C / F derived from average_score.

    Metadata
    --------
    question        : The evaluated question (for report traceability).
    repository_name : Optional label shown in reports.
    evaluated_at    : UTC timestamp of this evaluation run.
    """

    # ── Identity ─────────────────────────────────────────────────────────────
    question:        str            = Field(..., description="The evaluated question.")
    repository_name: Optional[str]  = Field(default=None)

    # ── RAGAS quality metrics ─────────────────────────────────────────────────
    context_precision:  MetricScore = Field(...)
    context_recall:     MetricScore = Field(...)
    faithfulness:       MetricScore = Field(...)
    answer_relevancy:   MetricScore = Field(...)
    answer_correctness: MetricScore = Field(...)

    # ── Derived metrics ───────────────────────────────────────────────────────
    hallucination_rate: MetricScore = Field(...)
    reasoning_quality:  MetricScore = Field(...)

    # ── Latency ───────────────────────────────────────────────────────────────
    retrieval_latency_ms: Optional[float] = Field(default=None)
    response_time_ms:     Optional[float] = Field(default=None)

    # ── Aggregates ────────────────────────────────────────────────────────────
    average_score: Optional[float] = Field(default=None)
    overall_grade: str             = Field(default="N/A")

    # ── Metadata ──────────────────────────────────────────────────────────────
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def quality_scores(self) -> list[float]:
        """
        Return all non-None quality metric scores as a flat list.

        Excludes hallucination_rate (derived, not independent) and
        latency values (different units entirely).
        Used by EvaluationService to compute average_score.
        """
        metrics = [
            self.context_precision,
            self.context_recall,
            self.faithfulness,
            self.answer_relevancy,
            self.answer_correctness,
            self.reasoning_quality,
        ]
        return [m.score for m in metrics if m.score is not None]

    def to_dict(self) -> dict:
        """Serialise to a plain JSON-safe Python dict."""
        return self.model_dump(mode="json")

    def to_json(self) -> str:
        """Serialise to a JSON string."""
        return self.model_dump_json(indent=2)

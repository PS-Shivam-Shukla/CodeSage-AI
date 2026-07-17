"""
app/evaluation/config.py
========================

Single source of truth for every tunable parameter in the
CodeSage AI Evaluation Framework.

Design principle
----------------
No magic numbers anywhere else in the module.
Every threshold, weight, label, grade boundary, model name,
and formatting constant is defined here so:

    1. Changing evaluation behaviour requires editing ONE file.
    2. All values can be overridden via environment variables
       for CI/CD or production deployments (12-factor app style).
    3. A new team member can understand evaluation criteria
       by reading this file alone.

Sections
--------
    A. LLM & Embedding model names (reuse pipeline models)
    B. Quality label thresholds   (Excellent / Good / Average / Poor)
    C. Overall grade boundaries   (A+ / A / B / C / F)
    D. Metric weights             (weighted average_score)
    E. Latency warning thresholds (ms)
    F. Report formatting settings
    G. Helper functions           (label_from_score, grade_from_average)
"""

from __future__ import annotations

import os


# ============================================================================
# A.  LLM & EMBEDDING MODEL (reuse the pipeline's own models)
# ============================================================================
# RAGAS needs an LLM and an embedding model to act as judges.
# We reuse the exact same models already used by the RAG pipeline so:
#   - No extra API keys required
#   - No additional model weights downloaded
#   - Evaluation scores are comparable to pipeline behaviour

# The NVIDIA NIM LLM — same as app/llm/llm_config.py
EVAL_LLM_MODEL: str = os.getenv(
    "EVAL_LLM_MODEL", "meta/llama-3.1-70b-instruct"
)
EVAL_LLM_TEMPERATURE: float = float(os.getenv("EVAL_LLM_TEMPERATURE", "0.1"))
EVAL_LLM_MAX_TOKENS:  int   = int(os.getenv("EVAL_LLM_MAX_TOKENS", "1024"))

# NVIDIA API key — read from environment, NEVER hardcoded
# The .env file sets NVIDIA_API_KEY which ChatNVIDIA picks up automatically.
# We document it here for clarity but do NOT read it in this module —
# langchain_nvidia_ai_endpoints reads it from os.environ directly.
NVIDIA_API_KEY_ENV_VAR: str = "NVIDIA_API_KEY"

# The HuggingFace embedding model — same as app/config/embedding_config.py
EVAL_EMBEDDING_MODEL: str = os.getenv(
    "EVAL_EMBEDDING_MODEL", "BAAI/bge-m3"
)


# ============================================================================
# B.  QUALITY LABEL THRESHOLDS
# ============================================================================
# Every MetricScore is converted to a label using these lower bounds:
#   score >= THRESHOLD_EXCELLENT  →  "Excellent"
#   score >= THRESHOLD_GOOD       →  "Good"
#   score >= THRESHOLD_AVERAGE    →  "Average"
#   score <  THRESHOLD_AVERAGE    →  "Poor"

THRESHOLD_EXCELLENT: float = float(os.getenv("EVAL_THRESHOLD_EXCELLENT", "0.85"))
THRESHOLD_GOOD:      float = float(os.getenv("EVAL_THRESHOLD_GOOD",      "0.70"))
THRESHOLD_AVERAGE:   float = float(os.getenv("EVAL_THRESHOLD_AVERAGE",   "0.50"))


# ============================================================================
# C.  OVERALL GRADE BOUNDARIES
# ============================================================================
# The overall grade is derived from the weighted average of all quality scores.
# Boundaries are also lower bounds (score >= boundary → that grade).

GRADE_BOUNDARIES: dict[str, float] = {
    "A+": float(os.getenv("EVAL_GRADE_APLUS", "0.90")),
    "A":  float(os.getenv("EVAL_GRADE_A",     "0.80")),
    "B":  float(os.getenv("EVAL_GRADE_B",     "0.70")),
    "C":  float(os.getenv("EVAL_GRADE_C",     "0.50")),
    "F":  0.0,
}

# Must be iterated in descending score order
GRADE_ORDER: list[str] = ["A+", "A", "B", "C", "F"]


# ============================================================================
# D.  METRIC WEIGHTS
# ============================================================================
# Used for computing the weighted average_score.
# Faithfulness is weighted higher because hallucination is the most
# dangerous failure mode in a production RAG system.
# Weights are normalised internally — they do not need to sum to 1.0.

METRIC_WEIGHTS: dict[str, float] = {
    "context_precision":   float(os.getenv("EVAL_WEIGHT_PRECISION",   "1.0")),
    "context_recall":      float(os.getenv("EVAL_WEIGHT_RECALL",      "1.0")),
    "faithfulness":        float(os.getenv("EVAL_WEIGHT_FAITHFULNESS", "1.5")),
    "answer_relevancy":    float(os.getenv("EVAL_WEIGHT_RELEVANCY",    "1.0")),
    "answer_correctness":  float(os.getenv("EVAL_WEIGHT_CORRECTNESS",  "1.0")),
    "hallucination_rate":  0.0,   # derived metric — excluded from average
    "reasoning_quality":   float(os.getenv("EVAL_WEIGHT_REASONING",   "1.0")),
}


# ============================================================================
# E.  LATENCY WARNING THRESHOLDS (milliseconds)
# ============================================================================
# These appear as warning flags in reports but do NOT affect metric scores.

LATENCY_RETRIEVAL_WARN_MS: float = float(
    os.getenv("EVAL_LATENCY_RETRIEVAL_WARN", "500")
)
LATENCY_RESPONSE_WARN_MS: float = float(
    os.getenv("EVAL_LATENCY_RESPONSE_WARN", "3000")
)


# ============================================================================
# F.  REPORT FORMATTING
# ============================================================================

REPORT_SEPARATOR_WIDTH: int = 60
REPORT_OUTPUT_DIR:      str = os.getenv("EVAL_REPORT_OUTPUT_DIR", "./evaluation_reports")
SCORE_DECIMAL_PLACES:   int = int(os.getenv("EVAL_SCORE_DECIMALS", "2"))


# ============================================================================
# G.  HELPER FUNCTIONS
# ============================================================================
# Placed in config so both evaluation_service.py and report_generator.py
# share the exact same label/grade logic — no duplication.

def label_from_score(score: float | None) -> str:
    """
    Convert a 0.0–1.0 score to a human-readable quality label.

    Args:
        score: Float in [0.0, 1.0], or None if metric was skipped.

    Returns:
        "Excellent" | "Good" | "Average" | "Poor" | "N/A"

    Examples:
        >>> label_from_score(0.92)
        'Excellent'
        >>> label_from_score(0.72)
        'Good'
        >>> label_from_score(None)
        'N/A'
    """
    if score is None:
        return "N/A"
    if score >= THRESHOLD_EXCELLENT:
        return "Excellent"
    if score >= THRESHOLD_GOOD:
        return "Good"
    if score >= THRESHOLD_AVERAGE:
        return "Average"
    return "Poor"


def grade_from_average(average: float | None) -> str:
    """
    Convert a weighted average score to an overall letter grade.

    Args:
        average: Mean of all quality metric scores, or None.

    Returns:
        "A+" | "A" | "B" | "C" | "F" | "N/A"

    Examples:
        >>> grade_from_average(0.95)
        'A+'
        >>> grade_from_average(0.45)
        'F'
        >>> grade_from_average(None)
        'N/A'
    """
    if average is None:
        return "N/A"
    for grade in GRADE_ORDER:
        if average >= GRADE_BOUNDARIES[grade]:
            return grade
    return "F"

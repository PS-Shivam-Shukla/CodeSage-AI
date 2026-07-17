"""
app/evaluation/reasoning_evaluator.py
======================================

LLM-as-a-Judge evaluator for Reasoning Quality.

What is Reasoning Quality?
--------------------------
RAGAS measures *retrieval* and *faithfulness* well, but it does not
assess whether the answer is well-reasoned, clearly structured, and
useful to a developer reading it.

Reasoning Quality asks:
    "Does the answer actually help a developer understand the codebase?"

It checks:
    - Logical coherence  : Does the answer follow a clear line of reasoning?
    - Completeness       : Does it cover the key aspects of the question?
    - Clarity            : Is it well-structured and easy to follow?
    - Code-awareness     : Does it reference specific code elements when relevant?
    - Conciseness        : Is it appropriately detailed, not bloated or too brief?

Why LLM-as-a-Judge?
--------------------
Traditional NLP metrics (BLEU, ROUGE) measure surface-level text overlap.
They cannot evaluate whether an answer is logically sound or developer-friendly.

An LLM judge can assess reasoning quality semantically — the same way a
senior engineer would review a colleague's explanation.

Design
------
- Uses the same NVIDIA NIM LLM already used by the RAG pipeline.
- The prompt is a structured rubric (1–5 scale per dimension).
- The LLM response is parsed with a regex fallback — no JSON mode required,
  works with any LLM that follows basic instructions.
- Returns a MetricScore with score in [0.0, 1.0] and a text explanation.
- If the LLM call fails or the response cannot be parsed, returns a safe
  MetricScore(score=None, label="N/A") so the rest of evaluation continues.

Scoring rubric (1–5 per dimension, normalised to 0.0–1.0)
----------------------------------------------------------
    Dimension           Weight
    ──────────────────  ──────
    Logical Coherence     25%
    Completeness          25%
    Clarity               20%
    Code Awareness        15%
    Conciseness           15%
"""

from __future__ import annotations

import logging
import os
import re
from typing import Optional

from langchain_nvidia_ai_endpoints import ChatNVIDIA

from app.evaluation.config import (
    EVAL_LLM_MAX_TOKENS,
    EVAL_LLM_MODEL,
    EVAL_LLM_TEMPERATURE,
    EVAL_LLM_TIMEOUT,
    NVIDIA_API_KEY_ENV_VAR,
    label_from_score,
)
from app.evaluation.models import MetricScore
from app.utils.retry_handler import retry_on_rate_limit

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Scoring rubric weights — must sum to 1.0
# ---------------------------------------------------------------------------
_DIMENSION_WEIGHTS: dict[str, float] = {
    "logical_coherence": 0.25,
    "completeness":      0.25,
    "clarity":           0.20,
    "code_awareness":    0.15,
    "conciseness":       0.15,
}

# ---------------------------------------------------------------------------
# Judge prompt template
# ---------------------------------------------------------------------------
_JUDGE_PROMPT = """\
You are an expert AI evaluator assessing the quality of an AI assistant's \
answer about a software repository.

You will score the answer on five dimensions using a scale of 1 to 5.

SCORING SCALE:
  5 = Excellent   (near perfect)
  4 = Good        (minor issues)
  3 = Average     (some problems but usable)
  2 = Poor        (significant issues)
  1 = Very Poor   (unacceptable)

DIMENSIONS TO SCORE:
  1. Logical Coherence  : Does the answer follow clear, logical reasoning?
  2. Completeness       : Does it address all key aspects of the question?
  3. Clarity            : Is it well-structured and easy to understand?
  4. Code Awareness     : Does it reference specific code elements correctly?
  5. Conciseness        : Is the length appropriate? Not bloated, not too brief?

---
QUESTION:
{question}

RETRIEVED CONTEXT (what the AI was given):
{context_summary}

AI ANSWER:
{answer}
---

Respond ONLY in this exact format (no extra text):
LOGICAL_COHERENCE: <1-5>
COMPLETENESS: <1-5>
CLARITY: <1-5>
CODE_AWARENESS: <1-5>
CONCISENESS: <1-5>
EXPLANATION: <one sentence explaining the overall quality>
"""


class ReasoningEvaluator:
    """
    Evaluates the reasoning quality of a RAG-generated answer using
    an LLM-as-a-Judge approach with a structured rubric.

    This class is intentionally separate from RagasAdapter because:
      - It uses a custom prompt, not RAGAS metrics.
      - It produces a score + natural-language explanation.
      - It can be extended or replaced independently of RAGAS.

    Usage
    -----
        evaluator = ReasoningEvaluator()
        metric    = evaluator.evaluate(
            question = "How is JWT authentication implemented?",
            answer   = "The app uses JWT tokens verified in middleware.",
            contexts = ["JWT tokens are issued on login...", "Middleware checks..."],
        )
        print(metric.score)       # 0.84
        print(metric.label)       # "Good"
        print(metric.explanation) # "The answer is clear but misses token expiry."
    """

    def __init__(self) -> None:
        """
        Initialise the LLM judge using the same NVIDIA model as the pipeline.

        Raises:
            EnvironmentError: If NVIDIA_API_KEY is not in the environment.
        """
        api_key = os.getenv(NVIDIA_API_KEY_ENV_VAR)
        if not api_key:
            raise EnvironmentError(
                f"'{NVIDIA_API_KEY_ENV_VAR}' is not set. "
                f"Add it to your .env file."
            )

        # Slightly higher temperature than generation to encourage
        # varied but thoughtful judgement responses
        self._llm = ChatNVIDIA(
            model=EVAL_LLM_MODEL,
            temperature=max(EVAL_LLM_TEMPERATURE, 0.2),
            max_tokens=EVAL_LLM_MAX_TOKENS,
            timeout=EVAL_LLM_TIMEOUT,
        )
        logger.info("ReasoningEvaluator initialised with model: %s", EVAL_LLM_MODEL)

    # -----------------------------------------------------------------------
    # LLM call with retry logic
    # -----------------------------------------------------------------------

    @retry_on_rate_limit(max_retries=5, initial_delay=2.0)
    def _call_llm_with_retry(self, prompt: str):
        """
        Call the LLM with automatic retry on rate limits.
        
        Retries up to 5 times with exponential backoff on 429 errors.
        """
        return self._llm.invoke(prompt)

    # -----------------------------------------------------------------------
    # Public interface
    # -----------------------------------------------------------------------

    def evaluate(
        self,
        question: str,
        answer:   str,
        contexts: list[str],
    ) -> MetricScore:
        """
        Score the reasoning quality of an answer using LLM-as-a-Judge.

        Args:
            question: The original user question.
            answer:   The LLM-generated answer to evaluate.
            contexts: List of retrieved context strings (for the judge's reference).

        Returns:
            MetricScore with:
                name        = "Reasoning Quality"
                score       = weighted average of rubric scores (0.0–1.0)
                label       = "Excellent" / "Good" / "Average" / "Poor"
                explanation = one-sentence summary from the LLM judge

            If the LLM call or parsing fails:
                score = None, label = "N/A", explanation = error description
        """
        # Summarise context to keep the prompt within token limits
        context_summary = self._summarise_context(contexts)

        prompt = _JUDGE_PROMPT.format(
            question        = question,
            context_summary = context_summary,
            answer          = answer,
        )

        try:
            response = self._call_llm_with_retry(prompt)
            raw_text = response.content if hasattr(response, "content") else str(response)
            return self._parse_response(raw_text)

        except Exception as exc:
            logger.error("ReasoningEvaluator LLM call failed: %s", exc)
            return MetricScore(
                name        = "Reasoning Quality",
                score       = None,
                label       = "N/A",
                explanation = f"Evaluation failed: {exc}",
            )

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def _parse_response(self, raw: str) -> MetricScore:
        """
        Parse the structured LLM judge response into a MetricScore.

        Expected format (one field per line):
            LOGICAL_COHERENCE: 4
            COMPLETENESS: 5
            CLARITY: 4
            CODE_AWARENESS: 3
            CONCISENESS: 4
            EXPLANATION: The answer clearly explains the JWT flow.

        Fallback:
            If any dimension score is missing the dimension is skipped
            (its weight is redistributed proportionally).
            If ALL dimensions are missing, score=None is returned.

        Args:
            raw: Raw text returned by the LLM judge.

        Returns:
            MetricScore with normalised score and explanation.
        """
        dimension_map: dict[str, str] = {
            "logical_coherence": r"LOGICAL_COHERENCE\s*:\s*([1-5])",
            "completeness":      r"COMPLETENESS\s*:\s*([1-5])",
            "clarity":           r"CLARITY\s*:\s*([1-5])",
            "code_awareness":    r"CODE_AWARENESS\s*:\s*([1-5])",
            "conciseness":       r"CONCISENESS\s*:\s*([1-5])",
        }

        # Extract dimension scores
        raw_scores: dict[str, int] = {}
        for dim, pattern in dimension_map.items():
            match = re.search(pattern, raw, re.IGNORECASE)
            if match:
                raw_scores[dim] = int(match.group(1))

        # Extract explanation
        explanation_match = re.search(
            r"EXPLANATION\s*:\s*(.+)", raw, re.IGNORECASE
        )
        explanation = (
            explanation_match.group(1).strip()
            if explanation_match
            else "No explanation provided."
        )

        # Guard: no dimensions parsed at all
        if not raw_scores:
            logger.warning(
                "ReasoningEvaluator could not parse any scores from: %s", raw[:200]
            )
            return MetricScore(
                name        = "Reasoning Quality",
                score       = None,
                label       = "N/A",
                explanation = "Could not parse judge response.",
            )

        # Compute weighted average
        # Only include dimensions that were successfully parsed;
        # redistribute their weight proportionally
        total_weight = sum(
            _DIMENSION_WEIGHTS[d]
            for d in raw_scores
            if d in _DIMENSION_WEIGHTS
        )
        if total_weight == 0.0:
            return MetricScore(
                name        = "Reasoning Quality",
                score       = None,
                label       = "N/A",
                explanation = explanation,
            )

        weighted_sum = sum(
            (raw_scores[d] / 5.0) * _DIMENSION_WEIGHTS[d]
            for d in raw_scores
            if d in _DIMENSION_WEIGHTS
        )

        # Normalise by actual total weight (handles missing dimensions)
        normalised_score = round(weighted_sum / total_weight, 4)

        return MetricScore(
            name        = "Reasoning Quality",
            score       = normalised_score,
            label       = label_from_score(normalised_score),
            explanation = explanation,
        )

    @staticmethod
    def _summarise_context(contexts: list[str], max_chars: int = 800) -> str:
        """
        Produce a short summary of the retrieved contexts for the judge prompt.

        We truncate to avoid exceeding the LLM's context window.
        The judge only needs to know what information was available,
        not the full verbatim text.

        Args:
            contexts:  List of retrieved chunk strings.
            max_chars: Maximum total characters in the summary.

        Returns:
            A single string with numbered context snippets.
        """
        if not contexts:
            return "(no context was retrieved)"

        lines: list[str] = []
        used  = 0

        for i, chunk in enumerate(contexts, start=1):
            # Take only the first 150 chars of each chunk
            snippet = chunk.strip()[:150].replace("\n", " ")
            line    = f"[{i}] {snippet}..."
            used   += len(line)
            if used > max_chars:
                lines.append(f"[...{len(contexts) - i + 1} more chunks truncated]")
                break
            lines.append(line)

        return "\n".join(lines)

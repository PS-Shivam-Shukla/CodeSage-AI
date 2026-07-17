"""
app/evaluation/ragas_adapter.py
================================

Encapsulates ALL RAGAS-specific code behind a clean adapter.

Why an adapter?
---------------
If we scattered ``from ragas import ...`` imports across multiple files:
  - Replacing RAGAS with another framework means hunting through the
    entire evaluation module.
  - Testing becomes harder because RAGAS is tightly coupled everywhere.
  - Version-specific quirks (like the Vertex AI import fix) are spread around.

With this adapter:
  - RAGAS lives in exactly ONE file.
  - EvaluationService never imports ragas directly — it calls this adapter.
  - Swapping RAGAS means rewriting only this file, nothing else changes.
  - The adapter can be mocked in tests without touching real RAGAS code.

What this adapter does
----------------------
1. Initialises the NVIDIA LLM and bge-m3 embedding model as RAGAS judges
   (reusing the same models already used by the RAG pipeline).
2. Runs RAGAS evaluate() on the five standard metrics.
3. Extracts the scores from the RAGAS result Dataset.
4. Returns a plain Python dict — no RAGAS types leak out.

RAGAS 0.3.3 API contract
------------------------
    from ragas import evaluate
    from ragas.metrics import (
        context_precision, context_recall, faithfulness,
        answer_relevancy, answer_correctness,
    )
    from ragas.llms.base   import LangchainLLMWrapper
    from ragas.embeddings.base import LangchainEmbeddingsWrapper
    from datasets import Dataset

    # Wire models
    context_precision.llm = LangchainLLMWrapper(llm)
    context_precision.embeddings = LangchainEmbeddingsWrapper(emb)
    # ... repeat for each metric

    # Build HuggingFace Dataset
    ds = Dataset.from_dict({
        "question":     [question],
        "answer":       [answer],
        "contexts":     [contexts],          # list[list[str]]
        "ground_truth": [ground_truth],      # optional
    })

    result = evaluate(ds, metrics=[...])
    score  = result["context_precision"]     # float
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from datasets import Dataset
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from ragas import evaluate
from ragas.embeddings.base import LangchainEmbeddingsWrapper
from ragas.llms.base import LangchainLLMWrapper
from ragas.metrics import (
    AnswerCorrectness,
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
    Faithfulness,
    answer_correctness,
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)

from app.embeddings.embedding_service import EmbeddingService
from app.evaluation.config import (
    EVAL_LLM_MAX_TOKENS,
    EVAL_LLM_MODEL,
    EVAL_LLM_TEMPERATURE,
    NVIDIA_API_KEY_ENV_VAR,
)

logger = logging.getLogger(__name__)

# ── Type alias: the raw scores dict returned by this adapter ──────────────────
# Keys match the metric names used in EvaluationService.
RagasScores = dict[str, Optional[float]]


class RagasAdapter:
    """
    Thin adapter that wraps RAGAS and exposes a single ``run()`` method.

    This class is the ONLY place in the codebase that imports or
    instantiates anything from the ``ragas`` library.

    Initialisation
    --------------
    On construction the adapter:
      1. Reads NVIDIA_API_KEY from the environment (never hardcoded).
      2. Creates a ChatNVIDIA LLM instance wrapped for RAGAS.
      3. Re-uses the already-cached bge-m3 embedding model wrapped for RAGAS.
      4. Assigns both to all five RAGAS metric instances.

    The same LLM and embedding model objects that power the RAG pipeline
    are reused here — no extra models, no extra API keys, no extra memory.

    Usage
    -----
        adapter = RagasAdapter()
        scores  = adapter.run(
            question     = "How is authentication handled?",
            answer       = "JWT tokens are verified in middleware.",
            contexts     = ["JWT tokens...", "The middleware checks..."],
            ground_truth = "Authentication uses JWT middleware.",  # optional
        )
        # scores is a plain dict, no ragas types
        print(scores["faithfulness"])        # e.g. 0.92
        print(scores["context_precision"])   # e.g. 0.88
    """

    def __init__(self) -> None:
        """
        Initialise RAGAS metric instances with the project's LLM and embeddings.

        Raises:
            EnvironmentError: If NVIDIA_API_KEY is not set in the environment.
        """
        api_key = os.getenv(NVIDIA_API_KEY_ENV_VAR)
        if not api_key:
            raise EnvironmentError(
                f"Environment variable '{NVIDIA_API_KEY_ENV_VAR}' is not set.\n"
                f"Add it to your .env file: {NVIDIA_API_KEY_ENV_VAR}=your_key_here"
            )

        # ── Build the LLM judge ────────────────────────────────────────────────
        # ChatNVIDIA reads NVIDIA_API_KEY from os.environ automatically.
        # We wrap it in LangchainLLMWrapper so RAGAS can call it.
        nvidia_llm = ChatNVIDIA(
            model=EVAL_LLM_MODEL,
            temperature=EVAL_LLM_TEMPERATURE,
            max_tokens=EVAL_LLM_MAX_TOKENS,
        )
        ragas_llm = LangchainLLMWrapper(nvidia_llm)

        # ── Build the embedding judge ──────────────────────────────────────────
        # EmbeddingService.get_model() returns the lru_cache'd bge-m3 model
        # that the RAG pipeline already loaded. Zero extra memory cost.
        hf_embeddings: HuggingFaceEmbeddings = EmbeddingService.get_model()
        ragas_embeddings = LangchainEmbeddingsWrapper(hf_embeddings)

        # ── Wire both judges into all five RAGAS metric instances ──────────────
        # RAGAS 0.3.x metric instances are module-level singletons.
        # We assign llm/embeddings directly on the instance.
        self._wire_metrics(ragas_llm, ragas_embeddings)

        logger.info(
            "RagasAdapter initialised  |  llm=%s  embeddings=%s",
            EVAL_LLM_MODEL,
            hf_embeddings.model_name,
        )

    # -----------------------------------------------------------------------
    # Public interface
    # -----------------------------------------------------------------------

    def run(
        self,
        question:     str,
        answer:       str,
        contexts:     list[str],
        ground_truth: Optional[str] = None,
    ) -> RagasScores:
        """
        Run RAGAS evaluation on a single question-answer-context triplet.

        This method:
          1. Builds a HuggingFace Dataset in the format RAGAS expects.
          2. Chooses which metrics to run based on ground_truth availability.
          3. Calls ragas.evaluate().
          4. Extracts scores into a plain Python dict (no RAGAS types).

        Ground truth handling
        ---------------------
        - ContextRecall and AnswerCorrectness REQUIRE ground truth.
        - If ground_truth is None those two metrics are excluded from the
          ragas.evaluate() call so no KeyError or NaN occurs.
        - Their scores will be None in the returned dict.

        Args:
            question:     The original user question.
            answer:       The LLM-generated answer.
            contexts:     List of retrieved chunk strings (one string per chunk).
            ground_truth: Expected correct answer. Pass None to skip
                          metrics that require it.

        Returns:
            RagasScores dict with keys:
                "context_precision"   → float | None
                "context_recall"      → float | None
                "faithfulness"        → float | None
                "answer_relevancy"    → float | None
                "answer_correctness"  → float | None

        Raises:
            Exception: Any RAGAS-internal error is logged and re-raised so
                       EvaluationService can decide how to handle it.
        """
        # ── Step 1: build the dataset ────────────────────────────────────────
        data: dict[str, list] = {
            "question": [question],
            "answer":   [answer],
            "contexts": [contexts],   # RAGAS expects list[list[str]]
        }

        # Include ground_truth only when available
        # RAGAS raises if the column is present but empty/None
        has_ground_truth = ground_truth is not None and ground_truth.strip() != ""
        if has_ground_truth:
            data["ground_truth"] = [ground_truth]

        dataset = Dataset.from_dict(data)

        # ── Step 2: choose metrics ────────────────────────────────────────────
        # Metrics that do NOT need ground truth
        metrics_no_gt = [
            context_precision,
            faithfulness,
            answer_relevancy,
        ]
        # Metrics that DO need ground truth
        metrics_need_gt = [
            context_recall,
            answer_correctness,
        ]

        active_metrics = metrics_no_gt.copy()
        if has_ground_truth:
            active_metrics.extend(metrics_need_gt)

        # ── Step 3: run RAGAS evaluate ────────────────────────────────────────
        logger.info(
            "Running RAGAS evaluate  |  metrics=%s  ground_truth=%s",
            [m.name for m in active_metrics],
            "yes" if has_ground_truth else "no",
        )

        try:
            result = evaluate(dataset=dataset, metrics=active_metrics)
        except Exception as exc:
            logger.error("RAGAS evaluate() failed: %s", exc)
            raise

        # ── Step 4: extract scores into plain dict ────────────────────────────
        scores: RagasScores = {
            "context_precision":  self._safe_get(result, "context_precision"),
            "context_recall":     self._safe_get(result, "context_recall"),
            "faithfulness":       self._safe_get(result, "faithfulness"),
            "answer_relevancy":   self._safe_get(result, "answer_relevancy"),
            "answer_correctness": self._safe_get(result, "answer_correctness"),
        }

        logger.info("RAGAS scores: %s", scores)
        return scores

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _wire_metrics(
        ragas_llm:        LangchainLLMWrapper,
        ragas_embeddings: LangchainEmbeddingsWrapper,
    ) -> None:
        """
        Assign the LLM and embedding model to every RAGAS metric instance.

        RAGAS 0.3.x uses module-level singleton metric instances
        (e.g. ``ragas.metrics.faithfulness``).  We must set their
        ``.llm`` and ``.embeddings`` attributes before calling evaluate().

        Not all metrics use embeddings — ContextPrecision and ContextRecall
        are LLM-only.  We assign embeddings anyway; RAGAS ignores the
        attribute if the metric does not use it.

        Args:
            ragas_llm:        Wrapped NVIDIA LLM ready for RAGAS.
            ragas_embeddings: Wrapped bge-m3 model ready for RAGAS.
        """
        for metric in [
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
            answer_correctness,
        ]:
            metric.llm = ragas_llm
            # Assign embeddings — ignored by metrics that don't use them
            if hasattr(metric, "embeddings"):
                metric.embeddings = ragas_embeddings

    @staticmethod
    def _safe_get(
        result: object,
        key:    str,
    ) -> Optional[float]:
        """
        Safely extract a score from the RAGAS result object.

        RAGAS result is dict-like.  If a metric was not run (because
        ground_truth was absent) its key will not be present — we
        return None rather than raising KeyError.

        NaN values (which RAGAS occasionally produces for edge cases)
        are also converted to None so Pydantic validation never sees NaN.

        Args:
            result: The object returned by ragas.evaluate().
            key:    The metric name to extract.

        Returns:
            Float score or None.
        """
        import math
        try:
            value = result[key]  # type: ignore[index]
            if value is None:
                return None
            fval = float(value)
            return None if math.isnan(fval) else fval
        except (KeyError, TypeError, ValueError):
            return None

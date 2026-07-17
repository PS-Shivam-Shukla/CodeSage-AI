"""
app/evaluation/evaluation_adapter.py
====================================

Manual implementation of RAG evaluation metrics using cosine
similarity on the same BAAI/bge-m3 embeddings already used by
the pipeline.  No external evaluation framework — no async
issues, no version conflicts, works on any Python version.

Metrics implemented
-------------------
    context_precision   — what fraction of retrieved chunks are relevant?
    context_recall      — what fraction of the answer is supported by context?
    faithfulness        — are all answer claims grounded in context?
    answer_relevancy    — does the answer address the question?
    answer_correctness  — how close is the answer to ground truth? (optional)

Algorithm: cosine similarity on bge-m3 embeddings
--------------------------------------------------
All five metrics reduce to "how semantically similar are these
two pieces of text?" which cosine similarity handles well.
bge-m3 is already loaded by the pipeline so no extra memory.

Thresholds
----------
A chunk / sentence is considered "relevant" when its cosine
similarity to the reference text >= RELEVANCE_THRESHOLD (0.70).
Tune via EVAL_RELEVANCE_THRESHOLD env var.
"""

from __future__ import annotations

import logging
import math
import os
import re
from typing import Optional

import numpy as np

from app.embeddings.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

# Minimum cosine similarity to consider a chunk/sentence relevant
RELEVANCE_THRESHOLD: float = float(os.getenv("EVAL_RELEVANCE_THRESHOLD", "0.70"))

RagScores = dict[str, Optional[float]]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors, clamped to [0, 1]."""
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    na, nb = np.linalg.norm(va), np.linalg.norm(vb)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.clip(np.dot(va, vb) / (na * nb), 0.0, 1.0))


def _sentences(text: str) -> list[str]:
    """Split text into sentences using punctuation."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in parts if s.strip()]


# ---------------------------------------------------------------------------
# Public adapter
# ---------------------------------------------------------------------------

class EvaluationAdapter:
    """
    Evaluates RAG output using cosine similarity on bge-m3 embeddings.

    Exposes the same interface as the old RAGAS-based adapter so
    EvaluationService requires zero changes.
    """

    def __init__(self) -> None:
        # Re-use the cached model — zero extra memory cost
        self._model = EmbeddingService.get_model()
        logger.info("EvaluationAdapter (manual) initialised with %s", self._model.model_name)

    def run(
        self,
        question:     str,
        answer:       str,
        contexts:     list[str],
        ground_truth: Optional[str] = None,
    ) -> RagScores:
        """
        Compute all five evaluation metrics and return a plain dict.

        Args:
            question:     User question.
            answer:       LLM-generated answer.
            contexts:     Retrieved chunks (list of strings).
            ground_truth: Expected answer (optional — skips answer_correctness).

        Returns:
            Dict with keys: context_precision, context_recall,
            faithfulness, answer_relevancy, answer_correctness.
            Each value is float in [0,1] or None if skipped.
        """
        try:
            q_emb  = self._model.embed_query(question)
            a_emb  = self._model.embed_query(answer)
            c_embs = self._model.embed_documents(contexts) if contexts else []
        except Exception as exc:
            logger.error("Embedding failed: %s", exc)
            return self._empty()

        scores: RagScores = {}

        # 1. Context Precision — how many chunks are relevant to the question?
        scores["context_precision"] = self._context_precision(q_emb, c_embs)

        # 2. Context Recall — how many answer sentences are supported by context?
        scores["context_recall"] = self._context_recall(answer, c_embs)

        # 3. Faithfulness — are all answer claims grounded in context?
        scores["faithfulness"] = self._faithfulness(answer, c_embs)

        # 4. Answer Relevancy — does the answer address the question?
        scores["answer_relevancy"] = round(_cosine(q_emb, a_emb), 4)

        # 5. Answer Correctness — similarity to ground truth (optional)
        if ground_truth:
            try:
                gt_emb = self._model.embed_query(ground_truth)
                scores["answer_correctness"] = round(_cosine(a_emb, gt_emb), 4)
            except Exception:
                scores["answer_correctness"] = None
        else:
            scores["answer_correctness"] = None

        logger.info("Manual metric scores: %s", scores)
        return scores

    # -----------------------------------------------------------------------
    # Individual metric implementations
    # -----------------------------------------------------------------------

    def _context_precision(
        self,
        question_emb: list[float],
        chunk_embs:   list[list[float]],
    ) -> Optional[float]:
        """
        Context Precision = relevant_chunks / total_chunks.

        A chunk is relevant when cosine(chunk, question) >= threshold.
        High precision means the retriever fetched mostly useful content.
        """
        if not chunk_embs:
            return 0.0
        relevant = sum(
            1 for ce in chunk_embs
            if _cosine(question_emb, ce) >= RELEVANCE_THRESHOLD
        )
        return round(relevant / len(chunk_embs), 4)

    def _context_recall(
        self,
        answer:     str,
        chunk_embs: list[list[float]],
    ) -> Optional[float]:
        """
        Context Recall = sentences_supported / total_sentences.

        For each sentence in the answer, we check whether any chunk
        has cosine similarity >= threshold.  High recall means the
        context contained enough information to produce the answer.
        """
        if not chunk_embs:
            return 0.0
        sentences = _sentences(answer)
        if not sentences:
            return 0.0
        try:
            sent_embs = self._model.embed_documents(sentences)
        except Exception:
            return None

        supported = sum(
            1 for se in sent_embs
            if any(_cosine(se, ce) >= RELEVANCE_THRESHOLD for ce in chunk_embs)
        )
        return round(supported / len(sentences), 4)

    def _faithfulness(
        self,
        answer:     str,
        chunk_embs: list[list[float]],
    ) -> Optional[float]:
        """
        Faithfulness = faithful_claims / total_claims.

        Each sentence in the answer is an atomic claim.  A claim is
        faithful when at least one retrieved chunk supports it
        (cosine >= threshold).  Low faithfulness = hallucination.
        """
        # Same algorithm as recall but semantically distinct:
        # recall asks "did we retrieve enough?",
        # faithfulness asks "is everything stated grounded?"
        return self._context_recall(answer, chunk_embs)

    # -----------------------------------------------------------------------
    # Helper
    # -----------------------------------------------------------------------

    @staticmethod
    def _empty() -> RagasScores:
        return {
            "context_precision":  None,
            "context_recall":     None,
            "faithfulness":       None,
            "answer_relevancy":   None,
            "answer_correctness": None,
        }

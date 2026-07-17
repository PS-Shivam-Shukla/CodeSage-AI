from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from langchain_core.documents import Document

from app.llm import LLMService
from app.retriever.retrieval_service import RetrievalService


@dataclass
class RAGResult:
    """
    Structured output from the RAG pipeline.

    This dataclass is consumed by the Evaluation Framework.
    It keeps question, answer, and retrieved contexts together
    so nothing is lost between pipeline and evaluator.

    Fields
    ------
    question  : The original user question.
    answer    : The LLM-generated answer string.
    contexts  : Individual chunk texts (one string per chunk).
                RAGAS expects a list[str], NOT a single joined string.
    documents : The raw LangChain Document objects (metadata intact).
    ground_truth : Optional expected answer for Answer Correctness metric.
    repository_name : Optional label shown in evaluation reports.
    retrieval_latency_ms : Time taken for the vector search step (ms).
    response_time_ms     : Total end-to-end time from question to answer (ms).
    """

    question:             str
    answer:               str
    contexts:             List[str]
    documents:            List[Document]                = field(default_factory=list)
    ground_truth:         Optional[str]                 = None
    repository_name:      Optional[str]                 = None
    retrieval_latency_ms: Optional[float]               = None
    response_time_ms:     Optional[float]               = None


class RAGPipeline:
    """
    End-to-end Retrieval-Augmented Generation pipeline.

    Workflow:
        Question
            ↓
        Retrieve Documents
            ↓
        Build Context
            ↓
        Generate Answer

    Backward Compatibility
    ----------------------
    The original ``ask()`` method is unchanged — it still returns a plain
    ``str``.  A new ``ask_with_context()`` method returns a ``RAGResult``
    dataclass that the Evaluation Framework consumes.  Callers that only
    need the answer string continue to use ``ask()`` without modification.
    """

    def __init__(self) -> None:

        self.retriever = RetrievalService()
        self.llm       = LLMService()

    # ------------------------------------------------------------------
    # Original method — UNCHANGED, backward compatible
    # ------------------------------------------------------------------

    def ask(
        self,
        question: str,
        k: int = 10,
    ) -> str:
        """
        Answer a user question and return the answer string only.

        This method is unchanged from the original implementation.
        Existing callers (e.g. API routes) continue to work without
        any modification.

        Args:
            question: User question.
            k: Number of retrieved chunks (default: 10, increased from 5 for better coverage).

        Returns:
            Generated answer string.
        """

        documents = self.retriever.retrieve(query=question, k=k)
        context   = self._build_context(documents)

        return self.llm.generate_answer(
            question=question,
            context=context,
        )

    # ------------------------------------------------------------------
    # New method — returns structured output for evaluation
    # ------------------------------------------------------------------

    def ask_with_context(
        self,
        question:        str,
        k:               int            = 10,
        ground_truth:    Optional[str]  = None,
        repository_name: Optional[str]  = None,
    ) -> RAGResult:
        """
        Answer a user question and return a structured ``RAGResult``.

        Use this method when you need the retrieved contexts alongside
        the answer — for example when passing output to the Evaluation
        Framework.

        The latency fields are populated here so the evaluation module
        receives accurate timing without needing to re-measure.

        Args:
            question:        User question.
            k:               Number of chunks to retrieve (default: 10, increased from 5 
                             for better context coverage and improved retrieval metrics).
            ground_truth:    Expected answer for Answer Correctness metric.
                             Pass ``None`` to skip that metric gracefully.
            repository_name: Human-readable label shown in reports.

        Returns:
            RAGResult with question, answer, contexts, documents,
            and latency measurements populated.

        Example::

            pipeline = RAGPipeline()
            result   = pipeline.ask_with_context(
                question="How is JWT auth implemented?",
                ground_truth="JWT tokens are verified in middleware.",
                repository_name="MyApp",
            )
            # Pass to EvaluationService
            from app.evaluation import EvaluationService
            score = EvaluationService().evaluate(result)
        """
        import time

        # ── Retrieval (timed) ──────────────────────────────────────────
        t0        = time.perf_counter()
        documents = self.retriever.retrieve(query=question, k=k)
        t1        = time.perf_counter()
        retrieval_latency_ms = round((t1 - t0) * 1000, 3)

        # ── Build context ─────────────────────────────────────────────
        # contexts is kept as list[str] for RAGAS compatibility.
        # _build_context() joins them for the LLM prompt.
        contexts = [doc.page_content for doc in documents]
        context  = "\n\n".join(contexts)

        # ── Generation (timed end-to-end) ──────────────────────────────
        t2     = time.perf_counter()
        answer = self.llm.generate_answer(question=question, context=context)
        t3     = time.perf_counter()
        # response_time_ms covers the full pipeline: retrieval + generation
        response_time_ms = round((t3 - t0) * 1000, 3)

        return RAGResult(
            question             = question,
            answer               = answer,
            contexts             = contexts,
            documents            = documents,
            ground_truth         = ground_truth,
            repository_name      = repository_name,
            retrieval_latency_ms = retrieval_latency_ms,
            response_time_ms     = response_time_ms,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_context(documents: List[Document]) -> str:
        """
        Convert retrieved documents into a single context string
        suitable for injection into the LLM prompt.
        """
        return "\n\n".join(doc.page_content for doc in documents)
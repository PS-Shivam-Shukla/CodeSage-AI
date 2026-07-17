"""
app/evaluation/latency.py
=========================

Latency measurement utilities for the Evaluation Framework.

Why a dedicated module?
-----------------------
Spreading time.perf_counter() calls across the codebase leads to:
  - Inconsistent units (some callers forget to multiply by 1000)
  - Different clock sources (time.time vs perf_counter)
  - No reusable formatting for reports

This module gives:
  ✓ One consistent clock  (perf_counter — monotonic, high resolution)
  ✓ Two usage patterns:
        measure_callable()   — wraps any single function call
        measure_block()      — context manager for multi-line blocks
  ✓ One formatter          (format_latency) used by report_generator.py

Where latency fits in evaluation
---------------------------------
    retrieval_latency_ms  →  timed inside RAGPipeline.ask_with_context()
    response_time_ms      →  timed inside RAGPipeline.ask_with_context()

Both values travel through RAGResult → EvaluationInput → EvaluationResult
and appear in every report format.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any, Callable, Generator, TypeVar

# Generic return type — measure_callable preserves the wrapped function's type
T = TypeVar("T")


# ---------------------------------------------------------------------------
# Core primitive
# ---------------------------------------------------------------------------

def elapsed_ms(start: float, end: float) -> float:
    """
    Convert a perf_counter interval to milliseconds.

    Args:
        start: Value from time.perf_counter() at start.
        end:   Value from time.perf_counter() at end.

    Returns:
        Elapsed time in milliseconds, rounded to 3 decimal places.
    """
    return round((end - start) * 1000, 3)


# ---------------------------------------------------------------------------
# Pattern 1 — wrap a synchronous callable
# ---------------------------------------------------------------------------

def measure_callable(
    fn: Callable[..., T],
    *args: Any,
    **kwargs: Any,
) -> tuple[T, float]:
    """
    Execute a synchronous callable, time it, and return
    both the result and elapsed milliseconds.

    Args:
        fn:      Any synchronous callable.
        *args:   Positional arguments forwarded to fn.
        **kwargs: Keyword arguments forwarded to fn.

    Returns:
        (result, elapsed_ms) tuple.

    Example — measuring retrieval::

        from app.evaluation.latency import measure_callable

        docs, latency_ms = measure_callable(
            retriever.retrieve, query="How is auth handled?", k=5
        )
        print(f"Retrieved {len(docs)} docs in {latency_ms} ms")
    """
    start  = time.perf_counter()
    result = fn(*args, **kwargs)
    end    = time.perf_counter()
    return result, elapsed_ms(start, end)


# ---------------------------------------------------------------------------
# Pattern 2 — context manager for arbitrary code blocks
# ---------------------------------------------------------------------------

@contextmanager
def measure_block() -> Generator[LatencyCapture, None, None]:
    """
    Context manager that measures the elapsed time of a code block.

    Yields a LatencyCapture object. Read .elapsed_ms AFTER the block exits.

    Example::

        from app.evaluation.latency import measure_block

        with measure_block() as timer:
            docs    = retriever.retrieve(query, k=5)
            context = build_context(docs)
            answer  = llm.generate(context)

        print(f"Total: {timer.elapsed_ms} ms")
    """
    capture         = LatencyCapture()
    capture._start  = time.perf_counter()
    try:
        yield capture
    finally:
        capture._end       = time.perf_counter()
        capture.elapsed_ms = elapsed_ms(capture._start, capture._end)


class LatencyCapture:
    """
    Value object that holds the elapsed time captured by measure_block().

    Attributes
    ----------
    elapsed_ms : float
        Elapsed time in milliseconds.
        Available only AFTER the ``with measure_block()`` block exits.
        Reads 0.0 while still inside the block.
    """

    def __init__(self) -> None:
        self._start:    float = 0.0
        self._end:      float = 0.0
        self.elapsed_ms: float = 0.0

    def __repr__(self) -> str:
        return f"LatencyCapture(elapsed_ms={self.elapsed_ms})"


# ---------------------------------------------------------------------------
# Formatter used by report_generator.py
# ---------------------------------------------------------------------------

def format_latency(ms: float | None) -> str:
    """
    Format a latency value for display in evaluation reports.

    Rules:
        None      → "N/A"
        < 1000 ms → "XXX ms"    (e.g. "352 ms")
        >= 1000   → "X.XX sec"  (e.g. "1.47 sec")

    Args:
        ms: Latency in milliseconds, or None if not measured.

    Returns:
        Human-readable string.

    Examples:
        >>> format_latency(352.4)
        '352 ms'
        >>> format_latency(1470.8)
        '1.47 sec'
        >>> format_latency(None)
        'N/A'
    """
    if ms is None:
        return "N/A"
    if ms < 1000:
        return f"{ms:.0f} ms"
    return f"{ms / 1000:.2f} sec"

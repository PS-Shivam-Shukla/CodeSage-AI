"""
tests/test_evaluation.py
=========================

Unit tests for the CodeSage AI Evaluation Framework.

Testing strategy
-----------------
All external dependencies are mocked so tests:
  - Run in under 3 seconds (no model loading, no GPU, no API calls)
  - Work fully offline and in CI pipelines
  - Produce deterministic results every run

What is mocked
--------------
  - RagasAdapter      → returns controlled score dicts
  - ReasoningEvaluator → returns controlled MetricScore objects
  - EmbeddingService   → not loaded
  - ChatNVIDIA         → not called
  - NVIDIA_API_KEY     → patched in os.environ

Test sections
--------------
  A. config.py           — label_from_score, grade_from_average
  B. latency.py          — elapsed_ms, measure_callable, measure_block,
                           format_latency
  C. models.py           — EvaluationInput validation, MetricScore clamp,
                           EvaluationResult helpers
  D. evaluation_service  — evaluate_from_raw end-to-end, weighted average,
                           None handling, hallucination derivation
  E. reasoning_evaluator — _parse_response, _summarise_context
  F. report_generator    — console lines, markdown, json file I/O
  G. rag_pipeline        — RAGResult dataclass, ask_with_context structure
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ── Imports under test ────────────────────────────────────────────────────────
from app.evaluation.config import (
    THRESHOLD_AVERAGE,
    THRESHOLD_EXCELLENT,
    THRESHOLD_GOOD,
    grade_from_average,
    label_from_score,
)
from app.evaluation.latency import (
    LatencyCapture,
    elapsed_ms,
    format_latency,
    measure_block,
    measure_callable,
)
from app.evaluation.models import EvaluationInput, EvaluationResult, MetricScore
from app.evaluation.report_generator import ReportGenerator


# =============================================================================
# SHARED FIXTURES
# =============================================================================

@pytest.fixture
def good_metric() -> MetricScore:
    return MetricScore(name="Test", score=0.92, label="Excellent")


@pytest.fixture
def full_result() -> EvaluationResult:
    """Fully populated EvaluationResult used by report tests."""
    mk = lambda name, score, label, explanation=None: MetricScore(
        name=name, score=score, label=label, explanation=explanation
    )
    return EvaluationResult(
        question             = "How is JWT authentication implemented?",
        repository_name      = "MyApp",
        context_precision    = mk("Context Precision",  0.94, "Excellent"),
        context_recall       = mk("Context Recall",     0.91, "Excellent"),
        faithfulness         = mk("Faithfulness",       0.97, "Excellent"),
        answer_relevancy     = mk("Answer Relevancy",   0.95, "Excellent"),
        answer_correctness   = mk("Answer Correctness", 0.92, "Excellent"),
        hallucination_rate   = mk("Hallucination Rate", 0.03, "Excellent"),
        reasoning_quality    = mk(
            "Reasoning Quality", 0.88, "Excellent",
            "Clear and well-structured answer."
        ),
        retrieval_latency_ms = 352.4,
        response_time_ms     = 1470.8,
        average_score        = 0.94,
        overall_grade        = "A+",
    )


@pytest.fixture
def result_no_ground_truth() -> EvaluationResult:
    """Result with answer_correctness and context_recall skipped (no GT)."""
    mk = lambda name, score, label: MetricScore(name=name, score=score, label=label)
    return EvaluationResult(
        question           = "What database is used?",
        context_precision  = mk("Context Precision", 0.80, "Good"),
        context_recall     = mk("Context Recall",    None, "N/A"),
        faithfulness       = mk("Faithfulness",      0.88, "Excellent"),
        answer_relevancy   = mk("Answer Relevancy",  0.85, "Excellent"),
        answer_correctness = mk("Answer Correctness", None, "N/A"),
        hallucination_rate = mk("Hallucination Rate", 0.12, "Good"),
        reasoning_quality  = mk("Reasoning Quality",  0.78, "Good"),
        average_score      = 0.83,
        overall_grade      = "A",
    )


# =============================================================================
# SECTION A — config.py
# =============================================================================

class TestLabelFromScore:
    def test_excellent(self):
        assert label_from_score(1.0) == "Excellent"
        assert label_from_score(THRESHOLD_EXCELLENT) == "Excellent"

    def test_good(self):
        assert label_from_score(THRESHOLD_GOOD) == "Good"
        assert label_from_score(0.75) == "Good"

    def test_average(self):
        assert label_from_score(THRESHOLD_AVERAGE) == "Average"
        assert label_from_score(0.60) == "Average"

    def test_poor(self):
        assert label_from_score(0.0) == "Poor"
        assert label_from_score(THRESHOLD_AVERAGE - 0.01) == "Poor"

    def test_none_returns_na(self):
        assert label_from_score(None) == "N/A"


class TestGradeFromAverage:
    def test_a_plus(self):
        assert grade_from_average(0.90) == "A+"
        assert grade_from_average(1.00) == "A+"

    def test_a(self):
        assert grade_from_average(0.80) == "A"
        assert grade_from_average(0.89) == "A"

    def test_b(self):
        assert grade_from_average(0.70) == "B"
        assert grade_from_average(0.79) == "B"

    def test_c(self):
        assert grade_from_average(0.50) == "C"
        assert grade_from_average(0.69) == "C"

    def test_f(self):
        assert grade_from_average(0.0)  == "F"
        assert grade_from_average(0.49) == "F"

    def test_none_returns_na(self):
        assert grade_from_average(None) == "N/A"


# =============================================================================
# SECTION B — latency.py
# =============================================================================

class TestElapsedMs:
    def test_one_second(self):
        assert elapsed_ms(0.0, 1.0) == 1000.0

    def test_sub_millisecond(self):
        assert elapsed_ms(0.0, 0.0005) == 0.5

    def test_returns_float(self):
        assert isinstance(elapsed_ms(0.0, 0.001), float)

    def test_real_clock(self):
        start = time.perf_counter()
        time.sleep(0.01)
        end = time.perf_counter()
        assert elapsed_ms(start, end) >= 5.0


class TestMeasureCallable:
    def test_returns_result_and_ms(self):
        result, ms = measure_callable(lambda: 42)
        assert result == 42
        assert ms >= 0.0

    def test_passes_args(self):
        result, _ = measure_callable(lambda x, y: x + y, 3, 4)
        assert result == 7

    def test_passes_kwargs(self):
        def greet(name, greeting="Hi"):
            return f"{greeting}, {name}!"
        result, _ = measure_callable(greet, "World", greeting="Hello")
        assert result == "Hello, World!"

    def test_ms_is_float(self):
        _, ms = measure_callable(lambda: None)
        assert isinstance(ms, float)


class TestMeasureBlock:
    def test_captures_elapsed(self):
        with measure_block() as timer:
            time.sleep(0.01)
        assert timer.elapsed_ms >= 5.0

    def test_returns_latency_capture(self):
        with measure_block() as timer:
            pass
        assert isinstance(timer, LatencyCapture)

    def test_elapsed_zero_before_exit(self):
        captured = []
        with measure_block() as timer:
            captured.append(timer.elapsed_ms)
        assert captured[0] == 0.0
        assert timer.elapsed_ms > 0.0


class TestFormatLatency:
    def test_none(self):
        assert format_latency(None) == "N/A"

    def test_under_1000(self):
        assert format_latency(352.4) == "352 ms"
        assert format_latency(0.0)   == "0 ms"

    def test_over_1000(self):
        assert format_latency(1000.0) == "1.00 sec"
        assert format_latency(1470.8) == "1.47 sec"


# =============================================================================
# SECTION C — models.py
# =============================================================================

class TestEvaluationInput:
    def test_valid_minimal(self):
        inp = EvaluationInput(
            question="Q?",
            answer="A.",
            contexts=["ctx"],
        )
        assert inp.ground_truth is None
        assert inp.retrieval_latency_ms is None

    def test_valid_full(self):
        inp = EvaluationInput(
            question="Q?",
            answer="A.",
            contexts=["ctx1", "ctx2"],
            ground_truth="GT",
            repository_name="Repo",
            retrieval_latency_ms=100.0,
            response_time_ms=500.0,
        )
        assert inp.ground_truth == "GT"
        assert inp.repository_name == "Repo"

    def test_empty_question_raises(self):
        with pytest.raises(Exception):
            EvaluationInput(question="", answer="A.", contexts=["c"])

    def test_empty_contexts_raises(self):
        with pytest.raises(Exception):
            EvaluationInput(question="Q?", answer="A.", contexts=[])

    def test_negative_latency_raises(self):
        with pytest.raises(Exception):
            EvaluationInput(
                question="Q?", answer="A.", contexts=["c"],
                retrieval_latency_ms=-1.0,
            )


class TestMetricScore:
    def test_normal_score(self):
        ms = MetricScore(name="Test", score=0.85, label="Excellent")
        assert ms.score == pytest.approx(0.85)

    def test_score_clamped_above_1(self):
        ms = MetricScore(name="Test", score=1.5, label="Excellent")
        assert ms.score == pytest.approx(1.0)

    def test_score_clamped_below_0(self):
        ms = MetricScore(name="Test", score=-0.3, label="Poor")
        assert ms.score == pytest.approx(0.0)

    def test_none_score(self):
        ms = MetricScore(name="Test", score=None, label="N/A")
        assert ms.score is None
        assert ms.label == "N/A"

    def test_explanation_optional(self):
        ms = MetricScore(name="Test", score=0.9, label="Excellent")
        assert ms.explanation is None


class TestEvaluationResult:
    def test_quality_scores_excludes_none(self, full_result):
        scores = full_result.quality_scores()
        assert len(scores) == 6   # 5 RAGAS + reasoning, NOT hallucination_rate
        assert all(s is not None for s in scores)

    def test_quality_scores_skips_none(self, result_no_ground_truth):
        scores = result_no_ground_truth.quality_scores()
        # context_recall=None, answer_correctness=None → 4 remain
        assert len(scores) == 4
        assert None not in scores

    def test_to_dict_is_serialisable(self, full_result):
        d = full_result.to_dict()
        assert isinstance(d, dict)
        serialised = json.dumps(d, default=str)
        assert "overall_grade" in serialised

    def test_to_json_is_string(self, full_result):
        j = full_result.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed["overall_grade"] == "A+"

    def test_overall_grade_in_result(self, full_result):
        assert full_result.overall_grade == "A+"

    def test_repository_name_optional(self, result_no_ground_truth):
        assert result_no_ground_truth.repository_name is None


# =============================================================================
# SECTION D — evaluation_service.py
# =============================================================================

class TestEvaluationServiceWeightedAverage:
    """Tests for the static _compute_weighted_average helper — no LLM needed."""

    def _avg(self, **kwargs):
        from app.evaluation.evaluation_service import EvaluationService
        return EvaluationService._compute_weighted_average(**kwargs)

    def test_all_none_returns_none(self):
        result = self._avg(
            precision=None, recall=None, faithfulness_val=None,
            relevancy=None, correctness=None, reasoning=None,
        )
        assert result is None

    def test_excludes_none_from_denominator(self):
        # Only precision=1.0 with weight 1.0 → average must be 1.0, not 1/6
        result = self._avg(
            precision=1.0, recall=None, faithfulness_val=None,
            relevancy=None, correctness=None, reasoning=None,
        )
        assert result == pytest.approx(1.0, abs=0.01)

    def test_perfect_scores(self):
        result = self._avg(
            precision=1.0, recall=1.0, faithfulness_val=1.0,
            relevancy=1.0, correctness=1.0, reasoning=1.0,
        )
        assert result == pytest.approx(1.0, abs=0.01)

    def test_faithfulness_weighted_higher(self):
        # faithfulness weight=1.5, others=1.0
        # faithfulness=1.0, all others=0.0
        # weights: precision=1.0, recall=1.0, faithfulness=1.5,
        #          relevancy=1.0, correctness=1.0, reasoning=1.0 → total=7.5
        # weighted_sum = 1.0 * 1.5 = 1.5
        # average = 1.5 / 7.5 = 0.20 BUT RAGAS weights may differ per config.
        # The key assertion is: faithfulness score dominates other equal scores.
        result_faithful = self._avg(
            precision=0.0, recall=0.0, faithfulness_val=1.0,
            relevancy=0.0, correctness=0.0, reasoning=0.0,
        )
        result_precision = self._avg(
            precision=1.0, recall=0.0, faithfulness_val=0.0,
            relevancy=0.0, correctness=0.0, reasoning=0.0,
        )
        # faithfulness (weight 1.5) should produce a higher average than
        # precision (weight 1.0) when both score 1.0 and all others are 0.0
        assert result_faithful is not None
        assert result_precision is not None
        assert result_faithful > result_precision

    def test_result_in_valid_range(self):
        result = self._avg(
            precision=0.7, recall=0.8, faithfulness_val=0.9,
            relevancy=0.85, correctness=0.75, reasoning=0.8,
        )
        assert result is not None
        assert 0.0 <= result <= 1.0


class TestEvaluationServiceHallucinationLabel:
    def _label(self, rate):
        from app.evaluation.evaluation_service import EvaluationService
        return EvaluationService._hallucination_label(rate)

    def test_none_returns_na(self):
        assert self._label(None) == "N/A"

    def test_excellent_low_rate(self):
        assert self._label(0.0)  == "Excellent"
        assert self._label(0.05) == "Excellent"

    def test_good(self):
        assert self._label(0.10) == "Good"
        assert self._label(0.15) == "Good"

    def test_average(self):
        assert self._label(0.20) == "Average"
        assert self._label(0.30) == "Average"

    def test_poor_high_rate(self):
        assert self._label(0.50) == "Poor"
        assert self._label(1.0)  == "Poor"


class TestEvaluationServiceEvaluateFromRaw:
    """
    End-to-end test of evaluate_from_raw() with mocked components.
    RagasAdapter and ReasoningEvaluator are replaced with simple mocks.
    """

    @pytest.fixture
    def service_with_mocks(self):
        """Return EvaluationService with both internal components mocked."""
        from app.evaluation.evaluation_service import EvaluationService

        mock_ragas = MagicMock()
        mock_ragas.run.return_value = {
            "context_precision":  0.90,
            "context_recall":     0.85,
            "faithfulness":       0.95,
            "answer_relevancy":   0.88,
            "answer_correctness": 0.82,
        }

        mock_reasoner = MagicMock()
        mock_reasoner.evaluate.return_value = MetricScore(
            name="Reasoning Quality", score=0.84,
            label="Good", explanation="Clear answer."
        )

        svc = EvaluationService()
        svc._ragas    = mock_ragas
        svc._reasoner = mock_reasoner
        return svc

    def test_returns_evaluation_result(self, service_with_mocks):
        result = service_with_mocks.evaluate_from_raw(
            question="How is auth handled?",
            answer="JWT tokens are used.",
            contexts=["JWT tokens are verified in middleware."],
        )
        assert isinstance(result, EvaluationResult)

    def test_overall_grade_set(self, service_with_mocks):
        result = service_with_mocks.evaluate_from_raw(
            question="Q?", answer="A.", contexts=["ctx"],
        )
        assert result.overall_grade in ["A+", "A", "B", "C", "F", "N/A"]

    def test_average_score_in_range(self, service_with_mocks):
        result = service_with_mocks.evaluate_from_raw(
            question="Q?", answer="A.", contexts=["ctx"],
        )
        assert result.average_score is not None
        assert 0.0 <= result.average_score <= 1.0

    def test_hallucination_derived_from_faithfulness(self, service_with_mocks):
        result = service_with_mocks.evaluate_from_raw(
            question="Q?", answer="A.", contexts=["ctx"],
        )
        expected = round(1.0 - 0.95, 2)
        assert result.hallucination_rate.score == pytest.approx(expected, abs=0.01)

    def test_answer_correctness_skipped_without_ground_truth(self, service_with_mocks):
        service_with_mocks._ragas.run.return_value = {
            "context_precision":  0.90,
            "context_recall":     None,
            "faithfulness":       0.95,
            "answer_relevancy":   0.88,
            "answer_correctness": None,
        }
        result = service_with_mocks.evaluate_from_raw(
            question="Q?", answer="A.", contexts=["ctx"],
            ground_truth=None,
        )
        assert result.answer_correctness.score is None
        assert result.answer_correctness.label == "N/A"

    def test_ragas_failure_still_returns_result(self, service_with_mocks):
        service_with_mocks._ragas.run.side_effect = RuntimeError("API error")
        result = service_with_mocks.evaluate_from_raw(
            question="Q?", answer="A.", contexts=["ctx"],
        )
        assert isinstance(result, EvaluationResult)
        assert result.faithfulness.score is None

    def test_reasoning_failure_still_returns_result(self, service_with_mocks):
        service_with_mocks._reasoner.evaluate.side_effect = RuntimeError("LLM down")
        result = service_with_mocks.evaluate_from_raw(
            question="Q?", answer="A.", contexts=["ctx"],
        )
        assert isinstance(result, EvaluationResult)
        assert result.reasoning_quality.score is None

    def test_latency_values_passed_through(self, service_with_mocks):
        result = service_with_mocks.evaluate_from_raw(
            question="Q?", answer="A.", contexts=["ctx"],
            retrieval_latency_ms=312.4,
            response_time_ms=1470.8,
        )
        assert result.retrieval_latency_ms == pytest.approx(312.4)
        assert result.response_time_ms     == pytest.approx(1470.8)

    def test_repository_name_passed_through(self, service_with_mocks):
        result = service_with_mocks.evaluate_from_raw(
            question="Q?", answer="A.", contexts=["ctx"],
            repository_name="TestRepo",
        )
        assert result.repository_name == "TestRepo"


# =============================================================================
# SECTION E — reasoning_evaluator.py
# =============================================================================

class TestReasoningEvaluatorParseResponse:
    """Tests _parse_response() — no LLM needed."""

    def _parse(self, raw: str) -> MetricScore:
        from app.evaluation.reasoning_evaluator import ReasoningEvaluator
        # Bypass __init__ (needs NVIDIA key) by creating unbound instance
        obj = object.__new__(ReasoningEvaluator)
        return obj._parse_response(raw)

    def test_perfect_scores(self):
        raw = (
            "LOGICAL_COHERENCE: 5\n"
            "COMPLETENESS: 5\n"
            "CLARITY: 5\n"
            "CODE_AWARENESS: 5\n"
            "CONCISENESS: 5\n"
            "EXPLANATION: Perfect answer."
        )
        result = self._parse(raw)
        assert result.score == pytest.approx(1.0, abs=0.01)
        assert result.label == "Excellent"
        assert result.explanation == "Perfect answer."

    def test_minimum_scores(self):
        raw = (
            "LOGICAL_COHERENCE: 1\n"
            "COMPLETENESS: 1\n"
            "CLARITY: 1\n"
            "CODE_AWARENESS: 1\n"
            "CONCISENESS: 1\n"
            "EXPLANATION: Very poor."
        )
        result = self._parse(raw)
        assert result.score == pytest.approx(0.2, abs=0.01)

    def test_mixed_scores(self):
        raw = (
            "LOGICAL_COHERENCE: 4\n"
            "COMPLETENESS: 3\n"
            "CLARITY: 5\n"
            "CODE_AWARENESS: 4\n"
            "CONCISENESS: 4\n"
            "EXPLANATION: Mostly good."
        )
        result = self._parse(raw)
        assert result.score is not None
        assert 0.6 < result.score < 1.0
        assert result.explanation == "Mostly good."

    def test_missing_all_dimensions_returns_none(self):
        result = self._parse("No scores here at all.")
        assert result.score is None
        assert result.label == "N/A"

    def test_partial_dimensions_redistributes_weight(self):
        # Only 2 of 5 dimensions present
        raw = (
            "LOGICAL_COHERENCE: 5\n"
            "COMPLETENESS: 5\n"
            "EXPLANATION: Partial."
        )
        result = self._parse(raw)
        # Both present dimensions scored 5/5 → normalised = 1.0
        assert result.score == pytest.approx(1.0, abs=0.01)

    def test_explanation_fallback_when_missing(self):
        raw = (
            "LOGICAL_COHERENCE: 4\n"
            "COMPLETENESS: 4\n"
            "CLARITY: 4\n"
            "CODE_AWARENESS: 4\n"
            "CONCISENESS: 4\n"
        )
        result = self._parse(raw)
        assert result.explanation == "No explanation provided."


class TestReasoningEvaluatorSummariseContext:
    def _summarise(self, contexts, max_chars=800):
        from app.evaluation.reasoning_evaluator import ReasoningEvaluator
        return ReasoningEvaluator._summarise_context(contexts, max_chars)

    def test_empty_contexts(self):
        result = self._summarise([])
        assert "no context" in result.lower()

    def test_single_chunk_included(self):
        result = self._summarise(["JWT tokens are used."])
        assert "JWT" in result

    def test_truncation_applied(self):
        # Very small max_chars forces truncation
        long_contexts = ["x" * 200] * 10
        result = self._summarise(long_contexts, max_chars=50)
        assert "truncated" in result.lower()

    def test_numbered_chunks(self):
        result = self._summarise(["First chunk.", "Second chunk."])
        assert "[1]" in result
        assert "[2]" in result


# =============================================================================
# SECTION F — report_generator.py
# =============================================================================

class TestReportGeneratorConsole:
    def test_separator_present(self, full_result):
        lines = ReportGenerator._build_console_lines(full_result)
        thick = [l for l in lines if set(l.strip()) == {"="}]
        assert len(thick) >= 2

    def test_question_in_output(self, full_result):
        lines = ReportGenerator._build_console_lines(full_result)
        combined = "\n".join(lines)
        assert "JWT" in combined

    def test_grade_in_output(self, full_result):
        lines = ReportGenerator._build_console_lines(full_result)
        combined = "\n".join(lines)
        assert "A+" in combined

    def test_repository_name_shown(self, full_result):
        lines = ReportGenerator._build_console_lines(full_result)
        combined = "\n".join(lines)
        assert "MyApp" in combined

    def test_latency_warning_when_slow(self, full_result):
        from app.evaluation.models import EvaluationResult, MetricScore
        mk = lambda n, s, l: MetricScore(name=n, score=s, label=l)
        slow = EvaluationResult(
            question           = "Q?",
            context_precision  = mk("CP", 0.9, "Excellent"),
            context_recall     = mk("CR", 0.9, "Excellent"),
            faithfulness       = mk("F",  0.9, "Excellent"),
            answer_relevancy   = mk("AR", 0.9, "Excellent"),
            answer_correctness = mk("AC", 0.9, "Excellent"),
            hallucination_rate = mk("HR", 0.1, "Good"),
            reasoning_quality  = mk("RQ", 0.9, "Excellent"),
            retrieval_latency_ms = 9999.0,  # exceeds warning threshold
            response_time_ms     = 100.0,
            average_score = 0.9,
            overall_grade = "A+",
        )
        lines = ReportGenerator._build_console_lines(slow)
        combined = "\n".join(lines)
        assert "slow" in combined or "⚠" in combined

    def test_na_score_displayed_without_crash(self, result_no_ground_truth):
        lines = ReportGenerator._build_console_lines(result_no_ground_truth)
        combined = "\n".join(lines)
        assert "N/A" in combined


class TestReportGeneratorMarkdown:
    def test_contains_table_header(self, full_result):
        md = ReportGenerator._build_markdown(full_result)
        assert "| Metric |" in md

    def test_contains_all_metrics(self, full_result):
        md = ReportGenerator._build_markdown(full_result)
        for name in ["Faithfulness", "Context Precision", "Reasoning Quality",
                     "Hallucination Rate"]:
            assert name in md

    def test_overall_grade_in_summary(self, full_result):
        md = ReportGenerator._build_markdown(full_result)
        assert "A+" in md

    def test_reasoning_explanation_in_table(self, full_result):
        md = ReportGenerator._build_markdown(full_result)
        assert "Clear and well-structured" in md


class TestReportGeneratorFiles:
    def test_save_json_creates_file(self, tmp_path, full_result):
        out = str(tmp_path / "report.json")
        path = ReportGenerator.save_json(full_result, path=out)
        assert path.exists()

    def test_save_json_content_valid(self, tmp_path, full_result):
        out = str(tmp_path / "report.json")
        ReportGenerator.save_json(full_result, path=out)
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        assert data["overall_grade"] == "A+"

    def test_save_markdown_creates_file(self, tmp_path, full_result):
        out = str(tmp_path / "report.md")
        path = ReportGenerator.save_markdown(full_result, path=out)
        assert path.exists()

    def test_save_markdown_content(self, tmp_path, full_result):
        out = str(tmp_path / "report.md")
        ReportGenerator.save_markdown(full_result, path=out)
        content = Path(out).read_text(encoding="utf-8")
        assert "A+" in content
        assert "JWT" in content

    def test_save_json_batch(self, tmp_path, full_result, result_no_ground_truth):
        out = str(tmp_path / "batch.json")
        ReportGenerator.save_json_batch(
            [full_result, result_no_ground_truth], path=out
        )
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        assert data["total_evaluated"] == 2
        assert len(data["results"]) == 2

    def test_resolve_path_default(self):
        p = ReportGenerator._resolve_path(None, "report.json")
        assert p.name == "report.json"

    def test_resolve_path_custom_file(self):
        p = ReportGenerator._resolve_path("/tmp/my.json", "default.json")
        assert p.name == "my.json"

    def test_resolve_path_directory(self, tmp_path):
        p = ReportGenerator._resolve_path(str(tmp_path), "report.json")
        assert p.name == "report.json"
        assert p.parent == tmp_path


# =============================================================================
# SECTION G — rag_pipeline.py (RAGResult dataclass)
# =============================================================================

class TestRAGResult:
    """Tests for the RAGResult dataclass — no ChromaDB or LLM needed."""

    def test_rag_result_construction(self):
        from app.rag.rag_pipeline import RAGResult
        r = RAGResult(
            question = "How is auth handled?",
            answer   = "JWT tokens.",
            contexts = ["ctx1", "ctx2"],
        )
        assert r.question == "How is auth handled?"
        assert len(r.contexts) == 2
        assert r.ground_truth is None
        assert r.repository_name is None
        assert r.retrieval_latency_ms is None
        assert r.response_time_ms is None

    def test_rag_result_with_all_fields(self):
        from app.rag.rag_pipeline import RAGResult
        r = RAGResult(
            question             = "Q?",
            answer               = "A.",
            contexts             = ["c"],
            ground_truth         = "GT",
            repository_name      = "Repo",
            retrieval_latency_ms = 100.0,
            response_time_ms     = 500.0,
        )
        assert r.ground_truth == "GT"
        assert r.retrieval_latency_ms == 100.0

    def test_rag_result_contexts_is_list(self):
        from app.rag.rag_pipeline import RAGResult
        r = RAGResult(
            question="Q?", answer="A.",
            contexts=["chunk1", "chunk2", "chunk3"],
        )
        assert isinstance(r.contexts, list)
        assert r.contexts[1] == "chunk2"

    def test_evaluate_service_rejects_non_rag_result(self):
        from app.evaluation.evaluation_service import EvaluationService
        svc = EvaluationService()
        with pytest.raises(TypeError, match="RAGResult"):
            svc.evaluate({"question": "Q?", "answer": "A."})

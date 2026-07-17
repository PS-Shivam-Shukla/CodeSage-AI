"""
app/evaluation/report_generator.py
====================================

Renders an EvaluationResult in three output formats:

    1. Console  — aligned table printed to stdout
    2. JSON     — machine-readable file for CI pipelines / dashboards
    3. Markdown — documentation-friendly for GitHub / Notion / Confluence

Design decisions
-----------------
- Fully STATELESS: every method is a classmethod or staticmethod.
  No instance variables. Thread-safe by construction.

- Formatting is SEPARATE from computation. This class never calculates
  scores — it only renders pre-computed EvaluationResult objects.

- Output directories are created automatically (no manual mkdir needed).

- Both single-result and batch variants are provided for every format.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.evaluation.config import (
    LATENCY_RESPONSE_WARN_MS,
    LATENCY_RETRIEVAL_WARN_MS,
    REPORT_OUTPUT_DIR,
    REPORT_SEPARATOR_WIDTH,
    SCORE_DECIMAL_PLACES,
)
from app.evaluation.latency import format_latency
from app.evaluation.models import EvaluationResult, MetricScore

logger = logging.getLogger(__name__)

# ── Visual constants ──────────────────────────────────────────────────────────
SEP_THICK = "=" * REPORT_SEPARATOR_WIDTH
SEP_THIN  = "-" * REPORT_SEPARATOR_WIDTH

GRADE_EMOJI: dict[str, str] = {
    "A+": "🏆", "A": "✅", "B": "👍",
    "C":  "⚠️",  "F": "❌", "N/A": "—",
}
LABEL_EMOJI: dict[str, str] = {
    "Excellent": "🟢", "Good": "🔵",
    "Average":   "🟡", "Poor": "🔴", "N/A": "⚪",
}


class ReportGenerator:
    """
    Renders EvaluationResult objects into human- and machine-readable formats.

    All methods are classmethods or staticmethods — no instantiation needed.

    Single-result usage
    --------------------
        from app.evaluation import ReportGenerator
        ReportGenerator.print_console(result)
        ReportGenerator.save_json(result)
        ReportGenerator.save_markdown(result)

    Batch usage
    -----------
        ReportGenerator.print_console_batch(results)
        ReportGenerator.save_json_batch(results)
        ReportGenerator.save_markdown_batch(results)
    """

    # ==========================================================================
    # FORMAT 1 — CONSOLE
    # ==========================================================================

    @classmethod
    def print_console(cls, result: EvaluationResult) -> str:
        """
        Print a formatted evaluation report to stdout.

        Output matches the spec::

            ============================================================
              Evaluation Report
            ============================================================
              Question
              How is JWT authentication implemented?
            ------------------------------------------------------------
              Context Precision       0.94    🟢 Excellent
              Context Recall          0.91    🟢 Excellent
              Faithfulness            0.97    🟢 Excellent
              Answer Relevancy        0.95    🟢 Excellent
              Answer Correctness      0.92    🟢 Excellent
              Hallucination Rate      0.03    🟢 Excellent
              Reasoning Quality       0.88    🟢 Excellent
            ------------------------------------------------------------
              Retrieval Latency       352 ms
              Response Time           1.47 sec
            ------------------------------------------------------------
              Average Score           0.94
              Overall Grade           A+  🏆
            ============================================================

        Args:
            result: A completed EvaluationResult.

        Returns:
            The formatted report string (also printed to stdout).
        """
        lines = cls._build_console_lines(result)
        output = "\n".join(lines)
        print(output)
        return output

    @classmethod
    def print_console_batch(cls, results: list[EvaluationResult]) -> None:
        """Print multiple results to console followed by a batch summary."""
        for i, result in enumerate(results, start=1):
            print(f"\n[{i} / {len(results)}]")
            cls.print_console(result)
        cls._print_batch_summary(results)

    # ==========================================================================
    # FORMAT 2 — JSON
    # ==========================================================================

    @classmethod
    def save_json(
        cls,
        result: EvaluationResult,
        path:   Optional[str] = None,
    ) -> Path:
        """
        Save a single EvaluationResult to a JSON file.

        Args:
            result: A completed EvaluationResult.
            path:   Output file path. Defaults to
                    ``REPORT_OUTPUT_DIR/evaluation_report.json``.

        Returns:
            The Path where the file was saved.
        """
        output_path = cls._resolve_path(path, "evaluation_report.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False, default=str)

        logger.info("JSON report saved → %s", output_path)
        print(f"  JSON report saved → {output_path}")
        return output_path

    @classmethod
    def save_json_batch(
        cls,
        results: list[EvaluationResult],
        path:    Optional[str] = None,
    ) -> Path:
        """
        Save a batch of EvaluationResults to a single JSON file.

        The output structure::

            {
                "generated_at":    "2026-07-14T10:30:00",
                "total_evaluated": 5,
                "batch_average":   0.91,
                "results":         [ ... ]
            }

        Args:
            results: List of EvaluationResult objects.
            path:    Output file path.

        Returns:
            The Path where the file was saved.
        """
        output_path = cls._resolve_path(path, "batch_evaluation_report.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        scores = [r.average_score for r in results if r.average_score is not None]
        batch_avg = (
            round(sum(scores) / len(scores), SCORE_DECIMAL_PLACES)
            if scores else None
        )

        payload = {
            "generated_at":    datetime.utcnow().isoformat(),
            "total_evaluated": len(results),
            "batch_average":   batch_avg,
            "results":         [r.to_dict() for r in results],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False, default=str)

        logger.info("Batch JSON report saved → %s", output_path)
        print(f"  Batch JSON report saved → {output_path}")
        return output_path

    # ==========================================================================
    # FORMAT 3 — MARKDOWN
    # ==========================================================================

    @classmethod
    def save_markdown(
        cls,
        result: EvaluationResult,
        path:   Optional[str] = None,
    ) -> Path:
        """
        Save a single EvaluationResult as a Markdown file.

        Renders cleanly on GitHub, Notion, and Confluence.

        Args:
            result: A completed EvaluationResult.
            path:   Output file path. Defaults to
                    ``REPORT_OUTPUT_DIR/evaluation_report.md``.

        Returns:
            The Path where the file was saved.
        """
        output_path = cls._resolve_path(path, "evaluation_report.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        content = cls._build_markdown(result)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info("Markdown report saved → %s", output_path)
        print(f"  Markdown report saved → {output_path}")
        return output_path

    @classmethod
    def save_markdown_batch(
        cls,
        results: list[EvaluationResult],
        path:    Optional[str] = None,
    ) -> Path:
        """
        Save a batch of EvaluationResults as a single Markdown file.

        Args:
            results: List of EvaluationResult objects.
            path:    Output file path.

        Returns:
            The Path where the file was saved.
        """
        output_path = cls._resolve_path(path, "batch_evaluation_report.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        scores = [r.average_score for r in results if r.average_score is not None]
        batch_avg = (
            round(sum(scores) / len(scores), SCORE_DECIMAL_PLACES)
            if scores else None
        )

        sections: list[str] = [
            "# Batch Evaluation Report",
            "",
            f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  ",
            f"**Total Evaluated:** {len(results)}  ",
            f"**Batch Average Score:** "
            f"{batch_avg if batch_avg is not None else 'N/A'}",
            "",
            "---",
            "",
        ]

        for i, result in enumerate(results, start=1):
            sections.append(f"## Result {i} of {len(results)}")
            sections.append("")
            sections.append(cls._build_markdown(result))
            sections.append("---")
            sections.append("")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(sections))

        logger.info("Batch Markdown report saved → %s", output_path)
        print(f"  Batch Markdown report saved → {output_path}")
        return output_path

    # ==========================================================================
    # PRIVATE BUILDERS
    # ==========================================================================

    @staticmethod
    def _build_console_lines(result: EvaluationResult) -> list[str]:
        """Build the console report as a list of strings."""
        lines: list[str] = []

        lines.append(SEP_THICK)
        lines.append("  Evaluation Report")
        lines.append(SEP_THICK)

        # ── Repository + timestamp ────────────────────────────────────────────
        if result.repository_name:
            lines.append(f"  Repository : {result.repository_name}")
        lines.append(
            f"  Evaluated  : "
            f"{result.evaluated_at.strftime('%Y-%m-%d %H:%M UTC')}"
        )
        lines.append(SEP_THIN)

        # ── Question ──────────────────────────────────────────────────────────
        lines.append("  Question")
        # Wrap long questions at 56 chars
        q = result.question
        while len(q) > 56:
            lines.append(f"  {q[:56]}")
            q = q[56:]
        lines.append(f"  {q}")
        lines.append(SEP_THIN)

        # ── Quality metrics ───────────────────────────────────────────────────
        metric_rows: list[tuple[str, MetricScore]] = [
            ("Context Precision",  result.context_precision),
            ("Context Recall",     result.context_recall),
            ("Faithfulness",       result.faithfulness),
            ("Answer Relevancy",   result.answer_relevancy),
            ("Answer Correctness", result.answer_correctness),
            ("Hallucination Rate", result.hallucination_rate),
            ("Reasoning Quality",  result.reasoning_quality),
        ]

        for name, metric in metric_rows:
            score_str = (
                f"{metric.score:.{SCORE_DECIMAL_PLACES}f}"
                if metric.score is not None
                else "N/A    "
            )
            emoji = LABEL_EMOJI.get(metric.label, "")
            lines.append(
                f"  {name:<22}  {score_str:<8}  {emoji} {metric.label}"
            )
            # Show explanation for Reasoning Quality
            if metric.explanation and name == "Reasoning Quality":
                exp = metric.explanation[:54]
                lines.append(f"  {'':22}  └─ {exp}")

        lines.append(SEP_THIN)

        # ── Latency ───────────────────────────────────────────────────────────
        ret_str   = format_latency(result.retrieval_latency_ms)
        resp_str  = format_latency(result.response_time_ms)
        ret_warn  = (
            " ⚠️  slow"
            if result.retrieval_latency_ms
            and result.retrieval_latency_ms > LATENCY_RETRIEVAL_WARN_MS
            else ""
        )
        resp_warn = (
            " ⚠️  slow"
            if result.response_time_ms
            and result.response_time_ms > LATENCY_RESPONSE_WARN_MS
            else ""
        )
        lines.append(f"  {'Retrieval Latency':<22}  {ret_str}{ret_warn}")
        lines.append(f"  {'Response Time':<22}  {resp_str}{resp_warn}")
        lines.append(SEP_THIN)

        # ── Aggregates ────────────────────────────────────────────────────────
        avg_str = (
            f"{result.average_score:.{SCORE_DECIMAL_PLACES}f}"
            if result.average_score is not None
            else "N/A"
        )
        grade_emoji = GRADE_EMOJI.get(result.overall_grade, "")
        lines.append(f"  {'Average Score':<22}  {avg_str}")
        lines.append(
            f"  {'Overall Grade':<22}  {result.overall_grade}  {grade_emoji}"
        )
        lines.append(SEP_THICK)

        return lines

    @staticmethod
    def _build_markdown(result: EvaluationResult) -> str:
        """Build a Markdown report string for a single EvaluationResult."""
        grade_emoji = GRADE_EMOJI.get(result.overall_grade, "")
        lines: list[str] = []

        # Header
        lines.append("## Evaluation Report")
        lines.append("")
        if result.repository_name:
            lines.append(f"**Repository:** {result.repository_name}  ")
        lines.append(
            f"**Evaluated:** "
            f"{result.evaluated_at.strftime('%Y-%m-%d %H:%M UTC')}  "
        )
        lines.append(f"**Question:** {result.question}")
        lines.append("")

        # Quality metrics table
        lines.append("### Quality Metrics")
        lines.append("")
        lines.append("| Metric | Score | Label | Notes |")
        lines.append("|--------|------:|-------|-------|")

        metric_rows: list[tuple[str, MetricScore]] = [
            ("Context Precision",  result.context_precision),
            ("Context Recall",     result.context_recall),
            ("Faithfulness",       result.faithfulness),
            ("Answer Relevancy",   result.answer_relevancy),
            ("Answer Correctness", result.answer_correctness),
            ("Hallucination Rate", result.hallucination_rate),
            ("Reasoning Quality",  result.reasoning_quality),
        ]

        for name, metric in metric_rows:
            score_str = (
                f"{metric.score:.{SCORE_DECIMAL_PLACES}f}"
                if metric.score is not None
                else "N/A"
            )
            emoji = LABEL_EMOJI.get(metric.label, "")
            notes = metric.explanation or ""
            lines.append(
                f"| {name} | {score_str} | {emoji} {metric.label} | {notes} |"
            )

        lines.append("")

        # Latency table
        lines.append("### Latency")
        lines.append("")
        lines.append("| Measurement | Value |")
        lines.append("|-------------|-------|")

        ret_warn  = (
            " ⚠️"
            if result.retrieval_latency_ms
            and result.retrieval_latency_ms > LATENCY_RETRIEVAL_WARN_MS
            else ""
        )
        resp_warn = (
            " ⚠️"
            if result.response_time_ms
            and result.response_time_ms > LATENCY_RESPONSE_WARN_MS
            else ""
        )
        lines.append(
            f"| Retrieval Latency | "
            f"{format_latency(result.retrieval_latency_ms)}{ret_warn} |"
        )
        lines.append(
            f"| Response Time | "
            f"{format_latency(result.response_time_ms)}{resp_warn} |"
        )
        lines.append("")

        # Summary
        avg_str = (
            f"{result.average_score:.{SCORE_DECIMAL_PLACES}f}"
            if result.average_score is not None
            else "N/A"
        )
        lines.append("### Summary")
        lines.append("")
        lines.append("| | |")
        lines.append("|---|---|")
        lines.append(f"| **Average Score** | {avg_str} |")
        lines.append(
            f"| **Overall Grade** | {result.overall_grade} {grade_emoji} |"
        )
        lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _print_batch_summary(results: list[EvaluationResult]) -> None:
        """Print a compact batch summary after a multi-result console report."""
        scores = [r.average_score for r in results if r.average_score is not None]
        batch_avg = (
            round(sum(scores) / len(scores), SCORE_DECIMAL_PLACES)
            if scores else None
        )

        grade_counts: dict[str, int] = {}
        for r in results:
            grade_counts[r.overall_grade] = (
                grade_counts.get(r.overall_grade, 0) + 1
            )

        print(f"\n{SEP_THICK}")
        print("  Batch Summary")
        print(SEP_THICK)
        print(f"  {'Total evaluated':<25} {len(results)}")
        print(
            f"  {'Batch average score':<25} "
            f"{batch_avg if batch_avg is not None else 'N/A'}"
        )
        dist = "  ".join(
            f"{g}:{grade_counts.get(g, 0)}"
            for g in ["A+", "A", "B", "C", "F"]
        )
        print(f"  {'Grade distribution':<25} {dist}")
        print(SEP_THICK)

    @staticmethod
    def _resolve_path(path: Optional[str], default_filename: str) -> Path:
        """
        Resolve the output file path.

        Rules:
          - None        → REPORT_OUTPUT_DIR / default_filename
          - Directory   → path / default_filename
          - File path   → use as-is

        Args:
            path:             User-provided path or None.
            default_filename: Fallback filename.

        Returns:
            Resolved Path object.
        """
        if path is None:
            return Path(REPORT_OUTPUT_DIR) / default_filename
        p = Path(path)
        if p.suffix == "":
            return p / default_filename
        return p

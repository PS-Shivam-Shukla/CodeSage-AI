r"""
run_evaluation.py
=================

One-stop evaluation runner for CodeSage AI.

Run this single file to evaluate your RAG pipeline against a set of
test questions. It prints a formatted table in the terminal and saves
a JSON report to ./evaluation_reports/

Usage
-----
    # Activate your virtual environment first
    .venv_backend\Scripts\Activate.ps1  (PowerShell)
    source .venv_backend/bin/activate   (bash/zsh)

    # Run with default test questions
    python run_evaluation.py

    # Run with a custom repository path (indexes before evaluating)
    python run_evaluation.py --repo "C:/path/to/your/repo"

    # Run silently (no table, only JSON saved)
    python run_evaluation.py --quiet

What this script does
---------------------
    1. Loads environment variables from .env
    2. Initialises the RAG pipeline
    3. Runs ask_with_context() for each test question
    4. Evaluates each result using EvaluationService (RAGAS + LLM judge)
    5. Prints a rich table to the terminal
    6. Saves a JSON report to ./evaluation_reports/evaluation_report.json

Output files
------------
    ./evaluation_reports/evaluation_report.json      ← full results
    ./evaluation_reports/evaluation_report_batch.json ← batch summary
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

def _utcnow() -> datetime:
    """Return current UTC time — Python 3.11+ compatible."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
from pathlib import Path

# ── Load .env before any app imports ─────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

# ── Add project root to sys.path so `app.*` imports work ─────────────────────
sys.path.insert(0, str(Path(__file__).parent))

# ── App imports ───────────────────────────────────────────────────────────────
from app.evaluation.evaluation_service import EvaluationService
from app.evaluation.models import EvaluationResult
from app.evaluation.latency import format_latency
from app.evaluation.config import (
    REPORT_OUTPUT_DIR,
    SCORE_DECIMAL_PLACES,
    GRADE_BOUNDARIES,
)
from app.rag.rag_pipeline import RAGPipeline


# =============================================================================
# TEST QUESTIONS
# Edit this list to add/remove evaluation questions.
# ground_truth is optional — omit it or set to None to skip Answer Correctness.
# =============================================================================

TEST_CASES: list[dict] = [
    {
        "question":     "What is CodeSage-AI and what are its main components including the RAG pipeline, evaluation system, and API architecture?",
        "ground_truth": "CodeSage-AI is a RAG (Retrieval-Augmented Generation) system with FastAPI backend that includes: RAGPipeline for question-answering, EvaluationService with custom metrics adapter, IndexingService for repository processing, embedding service using BAAI/bge-m3, and NVIDIA LLM integration with meta/llama-3.1-70b-instruct model.",
    },
    {
        "question":     "List all the REST API endpoints available in this repository with their HTTP methods and purposes",
        "ground_truth": "The API endpoints are: POST /chat for question-answering, POST /index for repository indexing, and GET /index/status for checking indexing status and database state.",
    },
    {
        "question":     "Explain the evaluation metrics system: what metrics are computed and how does the custom evaluation adapter work?",
        "ground_truth": "The evaluation system computes 5 core metrics using cosine similarity on bge-m3 embeddings: context_precision, context_recall, faithfulness, answer_relevancy, answer_correctness, plus reasoning_quality via LLM-as-judge and derived hallucination_rate. The custom adapter replaced RAGAS dependency for better compatibility.",
    },
    {
        "question":     "What configuration files and environment variables are required to run this project?",
        "ground_truth": "Required environment variables include NVIDIA_API_KEY for LLM access. Configuration files include app/llm/llm_config.py for model settings, app/evaluation/config.py for evaluation parameters, and .env file for environment variables. The system uses meta/llama-3.1-70b-instruct model with BAAI/bge-m3 embeddings.",
    },
    {
        "question":     "How does the RAG pipeline work from indexing to retrieval to response generation?",
        "ground_truth": "The RAG pipeline: 1) IndexingService processes repository files and creates embeddings using BAAI/bge-m3, 2) stores them in Chroma vector database, 3) RAGPipeline retrieves relevant chunks via vector similarity search, 4) passes context to NVIDIA LLM (meta/llama-3.1-70b-instruct) for response generation, 5) EvaluationService measures quality using multiple metrics.",
    },
    {
        "question":     "What are the main Python classes and services implemented in the app directory structure?",
        "ground_truth": "Main classes include: RAGPipeline (question-answering), EvaluationService (metric computation), IndexingService (repository processing), EmbeddingService (vector generation), EvaluationAdapter (evaluation metrics), ReasoningEvaluator (LLM judge), plus FastAPI route handlers and configuration classes.",
    },
    {
        "question":     "Explain the directory structure and organization of the codebase",
        "ground_truth": "Directory structure: app/ contains core services (api/, evaluation/, llm/, rag/, embeddings/, indexing/), evaluation_reports/ stores results, .venv_backend/ is Python virtual environment, run_evaluation.py is main evaluation script, and configuration files at root level.",
    },
    {
        "question":     "How does the evaluation system handle errors and what retry mechanisms are in place?",
        "ground_truth": "The evaluation system includes timeout handling (120s for LLM calls) and graceful error handling where individual metric failures don't stop the entire evaluation. However, it currently lacks retry logic for API rate limiting (429 errors).",
    },
]


# =============================================================================
# VISUAL CONSTANTS
# =============================================================================

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
BLUE   = "\033[94m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
DIM    = "\033[2m"

GRADE_COLOR = {
    "A+": GREEN,  "A": GREEN,
    "B":  BLUE,   "C": YELLOW,
    "F":  RED,    "N/A": DIM,
}
LABEL_COLOR = {
    "Excellent": GREEN,  "Good":    BLUE,
    "Average":   YELLOW, "Poor":    RED,
    "N/A":       DIM,
}
LABEL_ICON = {
    "Excellent": "●", "Good": "●",
    "Average":   "◐", "Poor": "○", "N/A": "—",
}


def colorise(text: str, color: str) -> str:
    """Wrap text with ANSI colour codes."""
    return f"{color}{text}{RESET}"


def score_bar(score: float | None, width: int = 10) -> str:
    """Render a mini progress bar for a score value."""
    if score is None:
        return DIM + "─" * width + RESET
    filled = round(score * width)
    empty  = width - filled
    color  = GREEN if score >= 0.85 else BLUE if score >= 0.70 else YELLOW if score >= 0.50 else RED
    return color + "█" * filled + DIM + "░" * empty + RESET


# =============================================================================
# TABLE PRINTER
# =============================================================================

def print_result_table(result: EvaluationResult, index: int, total: int) -> None:
    """Print a single EvaluationResult as a formatted terminal table."""

    W = 72  # total table width

    def sep(char: str = "─") -> str:
        return DIM + char * W + RESET

    def header_sep() -> str:
        return DIM + "═" * W + RESET

    print()
    print(header_sep())
    print(f"  {BOLD}{CYAN}Evaluation Result  [{index}/{total}]{RESET}")
    print(header_sep())

    # ── Meta ─────────────────────────────────────────────────────────────────
    if result.repository_name:
        print(f"  {DIM}Repository :{RESET} {result.repository_name}")
    ts = result.evaluated_at.strftime("%Y-%m-%d %H:%M UTC")
    print(f"  {DIM}Evaluated  :{RESET} {ts}")
    print(sep())

    # ── Question ─────────────────────────────────────────────────────────────
    print(f"  {BOLD}Question{RESET}")
    q = result.question
    for i in range(0, len(q), 68):
        print(f"  {q[i:i+68]}")
    print(sep())

    # ── Metrics table header ──────────────────────────────────────────────────
    col_metric = 22
    col_score  = 8
    col_bar    = 14
    col_label  = 12

    hdr = (
        f"  {BOLD}{'Metric':<{col_metric}}"
        f"{'Score':>{col_score}}  "
        f"{'':>{col_bar}}  "
        f"{'Label':<{col_label}}{RESET}"
    )
    print(hdr)
    print(sep())

    # ── Metric rows ───────────────────────────────────────────────────────────
    rows = [
        ("Context Precision",  result.context_precision),
        ("Context Recall",     result.context_recall),
        ("Faithfulness",       result.faithfulness),
        ("Answer Relevancy",   result.answer_relevancy),
        ("Answer Correctness", result.answer_correctness),
        ("Hallucination Rate", result.hallucination_rate),
        ("Reasoning Quality",  result.reasoning_quality),
    ]

    for name, metric in rows:
        score_str = (
            f"{metric.score:.{SCORE_DECIMAL_PLACES}f}"
            if metric.score is not None
            else " N/A"
        )
        lc    = LABEL_COLOR.get(metric.label, DIM)
        icon  = LABEL_ICON.get(metric.label, "—")
        bar   = score_bar(metric.score, width=10)
        label = colorise(f"{icon} {metric.label}", lc)

        print(
            f"  {name:<{col_metric}}"
            f"{colorise(score_str, lc):>{col_score}}  "
            f"{bar}  "
            f"{label}"
        )

        # Reasoning explanation on next line
        if metric.explanation and name == "Reasoning Quality":
            exp = metric.explanation[:60]
            print(f"  {'':>{col_metric}}    {DIM}└─ {exp}{RESET}")

    print(sep())

    # ── Latency ───────────────────────────────────────────────────────────────
    from app.evaluation.config import LATENCY_RETRIEVAL_WARN_MS, LATENCY_RESPONSE_WARN_MS
    ret_val  = format_latency(result.retrieval_latency_ms)
    resp_val = format_latency(result.response_time_ms)
    ret_warn  = f" {YELLOW}⚠ slow{RESET}" if result.retrieval_latency_ms and result.retrieval_latency_ms > LATENCY_RETRIEVAL_WARN_MS else ""
    resp_warn = f" {YELLOW}⚠ slow{RESET}" if result.response_time_ms and result.response_time_ms > LATENCY_RESPONSE_WARN_MS else ""

    print(f"  {'Retrieval Latency':<{col_metric}}{CYAN}{ret_val:>{col_score}}{RESET}{ret_warn}")
    print(f"  {'Response Time':<{col_metric}}{CYAN}{resp_val:>{col_score}}{RESET}{resp_warn}")
    print(sep())

    # ── Summary ───────────────────────────────────────────────────────────────
    avg_str = (
        f"{result.average_score:.{SCORE_DECIMAL_PLACES}f}"
        if result.average_score is not None
        else "N/A"
    )
    gc = GRADE_COLOR.get(result.overall_grade, DIM)
    avg_bar = score_bar(result.average_score, width=10)

    print(f"  {'Average Score':<{col_metric}}{colorise(avg_str, gc):>{col_score}}  {avg_bar}")
    print(f"  {'Overall Grade':<{col_metric}}{colorise(BOLD + result.overall_grade + RESET, gc):>{col_score}}")
    print(header_sep())


def print_batch_summary(results: list[EvaluationResult]) -> None:
    """Print the batch summary table after all individual results."""
    W = 72

    scores = [r.average_score for r in results if r.average_score is not None]
    batch_avg = round(sum(scores) / len(scores), SCORE_DECIMAL_PLACES) if scores else None

    grade_counts: dict[str, int] = {}
    for r in results:
        grade_counts[r.overall_grade] = grade_counts.get(r.overall_grade, 0) + 1

    print()
    print(BOLD + CYAN + "═" * W + RESET)
    print(f"  {BOLD}{CYAN}Batch Summary{RESET}")
    print(BOLD + CYAN + "═" * W + RESET)
    print(f"  {'Questions evaluated':<30} {BOLD}{len(results)}{RESET}")

    if batch_avg is not None:
        gc  = GRADE_COLOR.get(next((g for g in ["A+","A","B","C","F"] if batch_avg >= GRADE_BOUNDARIES.get(g, 0)), "F"), DIM)
        bar = score_bar(batch_avg, width=20)
        print(f"  {'Batch average score':<30} {colorise(str(batch_avg), gc)}  {bar}")
    else:
        print(f"  {'Batch average score':<30} {DIM}N/A{RESET}")

    print(f"  {'Grade distribution':<30}", end="  ")
    for grade in ["A+", "A", "B", "C", "F"]:
        count = grade_counts.get(grade, 0)
        gc    = GRADE_COLOR.get(grade, DIM)
        print(colorise(f"{grade}:{count}", gc), end="  ")
    print()
    print(BOLD + CYAN + "═" * W + RESET)


# =============================================================================
# JSON WRITER
# =============================================================================

def save_json_report(
    results:   list[EvaluationResult],
    questions: list[dict],
    output_dir: str = REPORT_OUTPUT_DIR,
) -> Path:
    """
    Save full evaluation results to a JSON file.

    Output structure:
    {
        "generated_at":    "2026-07-14T10:30:00",
        "total_evaluated": 5,
        "batch_average":   0.91,
        "overall_grade":   "A+",
        "results": [
            {
                "question":            "...",
                "overall_grade":       "A+",
                "average_score":       0.94,
                "context_precision":   { "score": 0.94, "label": "Excellent" },
                "context_recall":      { "score": 0.91, "label": "Excellent" },
                "faithfulness":        { "score": 0.97, "label": "Excellent" },
                "answer_relevancy":    { "score": 0.95, "label": "Excellent" },
                "answer_correctness":  { "score": null,  "label": "N/A" },
                "hallucination_rate":  { "score": 0.03, "label": "Excellent" },
                "reasoning_quality":   { "score": 0.88, "label": "Excellent",
                                         "explanation": "..." },
                "retrieval_latency_ms": 312.4,
                "response_time_ms":     1470.8,
                "evaluated_at":         "2026-07-14T10:30:00"
            },
            ...
        ]
    }
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    scores    = [r.average_score for r in results if r.average_score is not None]
    batch_avg = round(sum(scores) / len(scores), SCORE_DECIMAL_PLACES) if scores else None

    # Determine batch grade
    batch_grade = "N/A"
    if batch_avg is not None:
        for grade in ["A+", "A", "B", "C", "F"]:
            if batch_avg >= GRADE_BOUNDARIES.get(grade, 0.0):
                batch_grade = grade
                break

    def metric_to_dict(m) -> dict:
        d: dict = {"score": m.score, "label": m.label}
        if m.explanation:
            d["explanation"] = m.explanation
        return d

    results_list = []
    for r in results:
        results_list.append({
            "question":            r.question,
            "repository_name":     r.repository_name,
            "overall_grade":       r.overall_grade,
            "average_score":       r.average_score,
            "context_precision":   metric_to_dict(r.context_precision),
            "context_recall":      metric_to_dict(r.context_recall),
            "faithfulness":        metric_to_dict(r.faithfulness),
            "answer_relevancy":    metric_to_dict(r.answer_relevancy),
            "answer_correctness":  metric_to_dict(r.answer_correctness),
            "hallucination_rate":  metric_to_dict(r.hallucination_rate),
            "reasoning_quality":   metric_to_dict(r.reasoning_quality),
            "retrieval_latency_ms": r.retrieval_latency_ms,
            "response_time_ms":    r.response_time_ms,
            "evaluated_at":        r.evaluated_at.isoformat(),
        })

    payload = {
        "generated_at":    _utcnow().isoformat(),
        "total_evaluated": len(results),
        "batch_average":   batch_avg,
        "overall_grade":   batch_grade,
        "results":         results_list,
    }

    ts   = _utcnow().strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"evaluation_report_{ts}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, default=str)

    return path


# =============================================================================
# MAIN RUNNER
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="CodeSage AI — Evaluation Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_evaluation.py
  python run_evaluation.py --repo C:/Projects/MyApp
  python run_evaluation.py --quiet
        """,
    )
    parser.add_argument(
        "--repo",
        default=None,
        help="Path to a local repository to index before evaluating. "
             "If omitted, uses whatever is already indexed in ChromaDB.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Skip the terminal table. Only save the JSON report.",
    )
    parser.add_argument(
        "--output-dir",
        default=REPORT_OUTPUT_DIR,
        help=f"Directory for JSON output (default: {REPORT_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    # ── Banner ────────────────────────────────────────────────────────────────
    if not args.quiet:
        print()
        print(BOLD + CYAN + "╔" + "═" * 70 + "╗" + RESET)
        print(BOLD + CYAN + "║" + " " * 22 + "CodeSage AI  Evaluation" + " " * 25 + "║" + RESET)
        print(BOLD + CYAN + "╚" + "═" * 70 + "╝" + RESET)
        print(f"  {DIM}Evaluating {len(TEST_CASES)} question(s) against the indexed repository{RESET}")
        print()

    # ── Check NVIDIA_API_KEY ──────────────────────────────────────────────────
    if not os.getenv("NVIDIA_API_KEY"):
        print(f"{RED}ERROR: NVIDIA_API_KEY is not set.{RESET}")
        print(f"  Add it to your .env file:  NVIDIA_API_KEY=your_key_here")
        sys.exit(1)

    # ── Initialise pipeline ───────────────────────────────────────────────────
    print(f"  {DIM}Loading RAG pipeline...{RESET}", flush=True)
    try:
        pipeline = RAGPipeline()
    except Exception as exc:
        print(f"{RED}ERROR: Could not initialise RAGPipeline: {exc}{RESET}")
        sys.exit(1)
    # ── Optional: index a repo first ──────────────────────────────────────────
    if args.repo:
        from app.indexing import IndexingService
        print(f"  {DIM}Indexing repository: {args.repo}{RESET}", flush=True)
        t0 = time.perf_counter()
        try:
            IndexingService().index_repository(args.repo)
            elapsed = round((time.perf_counter() - t0) * 1000)
            print(f"  {GREEN}✓ Indexing complete in {elapsed} ms{RESET}")
        except Exception as exc:
            print(f"{RED}ERROR during indexing: {exc}{RESET}")
            sys.exit(1)

    # ── Initialise evaluation service ─────────────────────────────────────────
    print(f"  {DIM}Initialising evaluation service (loading models)...{RESET}", flush=True)
    try:
        service = EvaluationService()
    except Exception as exc:
        print(f"{RED}ERROR: Could not initialise EvaluationService: {exc}{RESET}")
        sys.exit(1)

    # ── Run evaluations ───────────────────────────────────────────────────────
    results:  list[EvaluationResult] = []
    total     = len(TEST_CASES)

    for i, case in enumerate(TEST_CASES, start=1):
        question     = case["question"]
        ground_truth = case.get("ground_truth")

        if not args.quiet:
            print(f"\n  {DIM}[{i}/{total}] Running: {question[:60]}...{RESET}", flush=True)

        try:
            # ── Step 1: RAG pipeline (retry once on timeout) ─────────────────
            for attempt in range(1, 3):
                try:
                    rag_result = pipeline.ask_with_context(
                        question     = question,
                        ground_truth = ground_truth,
                    )
                    break
                except Exception as e:
                    if attempt == 2:
                        raise
                    if not args.quiet:
                        print(f"  {YELLOW}  ↺ Retrying RAG (attempt {attempt} failed: {str(e)[:60]}){RESET}", flush=True)
                    time.sleep(3)

            # ── Step 2: Evaluate ─────────────────────────────────────────────
            eval_result = service.evaluate(rag_result)
            results.append(eval_result)

            # ── Step 3: Print table for this result ──────────────────────────
            if not args.quiet:
                print_result_table(eval_result, i, total)
            
            # ── Step 4: Rate limit prevention delay ──────────────────────────
            # Add a small delay between evaluations to avoid hitting rate limits
            if i < total:  # Don't delay after the last question
                if not args.quiet:
                    print(f"  {DIM}  ⏱  Waiting 2s before next evaluation (rate limit prevention)...{RESET}", flush=True)
                time.sleep(2)

        except Exception as exc:
            print(f"\n  {RED}✗ Evaluation failed for question [{i}]: {exc}{RESET}")
            continue

    # ── Batch summary ─────────────────────────────────────────────────────────
    if not args.quiet and results:
        print_batch_summary(results)

    # ── Save JSON ─────────────────────────────────────────────────────────────
    if results:
        print(f"\n  {DIM}Saving JSON report...{RESET}", flush=True)
        try:
            json_path = save_json_report(results, TEST_CASES, args.output_dir)
            print(f"  {GREEN}✓ JSON report saved → {json_path}{RESET}")
        except Exception as exc:
            print(f"  {RED}✗ Could not save JSON report: {exc}{RESET}")
    else:
        print(f"\n  {YELLOW}No results to save.{RESET}")

    print()


if __name__ == "__main__":
    main()

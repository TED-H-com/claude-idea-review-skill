import subprocess
import sys
import time
from pathlib import Path
import tempfile

INIT_SCRIPT = Path("scripts/init_review.py").resolve()
RENDER_SCRIPT = Path("scripts/render_report.py").resolve()

def test_performance_benchmarks():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Benchmark 1: Debate prompt generation latency (16 rounds)
        start_time = time.perf_counter()
        init_result = subprocess.run(
            [
                sys.executable, str(INIT_SCRIPT),
                "--idea", "A performance benchmarking tool for AI workflows",
                "--rounds", "16",
                "--out", tmpdir
            ],
            capture_output=True,
            text=True,
            check=True
        )
        init_duration = time.perf_counter() - start_time

        workspace_dir = Path(init_result.stdout.strip())
        assert workspace_dir.exists()

        # Setting a generous threshold (3.0 seconds) to prevent flaky tests in CI
        assert init_duration < 3.0, f"Prompt generation latency too high: {init_duration:.4f}s"

        # Benchmark 2: Persona context switching throughput (Simulating AI writing rounds)
        start_time = time.perf_counter()
        for n in range(1, 17):
            round_file = workspace_dir / "rounds" / f"round-{n:02d}.md"
            content = round_file.read_text(encoding="utf-8")

            content = content.replace("## Optimist\n\n", "## Optimist\n\nPerformance is key to user satisfaction and this will scale brilliantly.\n\n")
            content = content.replace("## Skeptic\n\n", "## Skeptic\n\nMeasurements might be flaky across different CI environments.\n\n")
            content = content.replace("## Pragmatist\n\n", "## Pragmatist\n\nLet's set generous thresholds to avoid flaky tests.\n\n")
            content = content.replace("## Synthesizer\n\n", "## Synthesizer\n\nWe will balance strictness and flakiness by using reasonable limits.\n\n")

            round_file.write_text(content, encoding="utf-8")

        final_file = workspace_dir / "final.md"
        final_content = final_file.read_text(encoding="utf-8")
        final_content = final_content.replace("- Verdict:\n", "- Verdict: worth_building\n")
        final_file.write_text(final_content, encoding="utf-8")

        persona_duration = time.perf_counter() - start_time

        # File IO for 16 rounds should be very fast, setting a generous threshold (1.0 seconds)
        assert persona_duration < 1.0, f"Persona context switching throughput too low: {persona_duration:.4f}s"

        # Benchmark 3: Final markdown report assembly speed
        start_time = time.perf_counter()
        render_result = subprocess.run(
            [sys.executable, str(RENDER_SCRIPT), str(workspace_dir)],
            capture_output=True,
            text=True,
            check=True
        )
        render_duration = time.perf_counter() - start_time

        # Rendering report should be fast, setting a generous threshold (3.0 seconds)
        assert render_duration < 3.0, f"Report assembly speed too low: {render_duration:.4f}s"

        # Output the benchmark results to stdout if pytest is run with -s (for manual inspection)
        print(f"\n[Performance Benchmark Results]")
        print(f"Prompt generation latency (16 rounds): {init_duration:.4f}s")
        print(f"Persona context switching throughput:  {persona_duration:.4f}s")
        print(f"Markdown report assembly speed:        {render_duration:.4f}s")

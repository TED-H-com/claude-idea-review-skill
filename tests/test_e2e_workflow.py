import subprocess
import sys
from pathlib import Path
import tempfile
import re

INIT_SCRIPT = Path("scripts/init_review.py").resolve()
RENDER_SCRIPT = Path("scripts/render_report.py").resolve()

def test_full_workflow_simulation():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: Scaffold workspace
        init_result = subprocess.run(
            [sys.executable, str(INIT_SCRIPT), "--idea", "An automated AI video editor", "--rounds", "5", "--out", tmpdir],
            capture_output=True,
            text=True,
            check=True
        )
        workspace_dir = Path(init_result.stdout.strip())
        assert workspace_dir.exists()

        # Step 2: Mock LLM Persona Prompt Expansion (simulate Claude populating the rounds)
        for n in range(1, 6):
            round_file = workspace_dir / "rounds" / f"round-{n:02d}.md"
            content = round_file.read_text(encoding="utf-8")

            # Replace empty headers with content
            content = content.replace("## Optimist\n\n", "## Optimist\n\nThis is the best idea ever. It will save creators hundreds of hours.\n\n")
            content = content.replace("## Skeptic\n\n", "## Skeptic\n\nVideo editing is highly subjective. An AI might miss the artistic nuance.\n\n")
            content = content.replace("## Pragmatist\n\n", "## Pragmatist\n\nLet's start with a simple MVP that just auto-cuts silences.\n\n")
            content = content.replace("## Synthesizer\n\n", "## Synthesizer\n\nWe agree there's demand for saving time, but artistic edits are risky. We need to test the auto-cut MVP first.\n\n")

            round_file.write_text(content, encoding="utf-8")

        # Step 3: Mock Synthesis Consolidation (simulate Claude writing the final report)
        final_file = workspace_dir / "final.md"
        final_content = final_file.read_text(encoding="utf-8")

        final_content = final_content.replace("- Verdict:\n", "- Verdict: validate_first\n")
        final_content = final_content.replace("- Confidence:\n", "- Confidence: 75\n")
        final_content = final_content.replace("- One-line conclusion:\n", "- One-line conclusion: Build a basic silence-cutter MVP to validate demand before investing in complex AI models.\n")
        final_content = final_content.replace("- Strongest reason:\n", "- Strongest reason: Creators desperately need to save time on basic tasks.\n")
        final_content = final_content.replace("- Strongest counterargument:\n", "- Strongest counterargument: AI might fail to capture the creator's unique editing style.\n")

        final_file.write_text(final_content, encoding="utf-8")

        # Step 4: Render report
        render_result = subprocess.run(
            [sys.executable, str(RENDER_SCRIPT), str(workspace_dir)],
            capture_output=True,
            text=True,
            check=True
        )

        report_md_path = workspace_dir / "report.md"
        report_html_path = workspace_dir / "report.html"

        assert report_md_path.exists()
        assert report_html_path.exists()

        # Step 5: Verify content in rendered reports
        report_md_content = report_md_path.read_text(encoding="utf-8")
        report_html_content = report_html_path.read_text(encoding="utf-8")

        assert "This is the best idea ever. It will save creators hundreds of hours." in report_md_content
        assert "Verdict: validate_first" in report_md_content
        assert "Build a basic silence-cutter MVP to validate demand" in report_md_content

        assert "This is the best idea ever. It will save creators hundreds of hours." in report_html_content
        assert "Verdict: validate_first" in report_html_content
        assert "Build a basic silence-cutter MVP to validate demand" in report_html_content

import subprocess
import sys
from pathlib import Path
import tempfile
import shutil

SCRIPT_PATH = Path("scripts/init_review.py").resolve()

def test_init_review_parameter_constraints():
    # Test valid choices for --rounds
    for rounds in [5, 12, 16]:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "--idea", "test idea", "--rounds", str(rounds), "--out", tmpdir],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0

    # Test invalid choice for --rounds
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--idea", "test idea", "--rounds", "3", "--out", tmpdir],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0
        assert "invalid choice: '3'" in result.stderr

def test_init_review_output_templates():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--idea", "test idea", "--rounds", "5", "--out", tmpdir],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

        # The script prints the root directory of the workspace
        workspace_dir = Path(result.stdout.strip())

        # Verify directory structure
        assert workspace_dir.exists()
        assert (workspace_dir / "input.md").exists()
        assert (workspace_dir / "rounds").is_dir()
        assert (workspace_dir / "final.md").exists()

        # Verify 5 rounds were created
        for n in range(1, 6):
            round_file = workspace_dir / "rounds" / f"round-{n:02d}.md"
            assert round_file.exists()
            content = round_file.read_text(encoding="utf-8")
            assert f"# Round {n}" in content
            assert "## Optimist" in content
            assert "## Skeptic" in content
            assert "## Pragmatist" in content
            assert "## Synthesizer" in content

        # Verify final.md template
        final_content = (workspace_dir / "final.md").read_text(encoding="utf-8")
        expected_fields = [
            "- Verdict:",
            "- Confidence:",
            "- One-line conclusion:",
            "- Strongest reason:",
            "- Strongest counterargument:",
            "- Two-week validation plan:",
            "- Success threshold:",
            "- Kill criterion:",
            "- Next 3 actions:"
        ]
        for field in expected_fields:
            assert field in final_content

#!/usr/bin/env python3
"""Create a deterministic workspace for an idea review panel run."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


def sanitize_idea(text: str) -> str:
    """Sanitize the idea text to prevent prompt injection and context escape."""
    text = text.strip()
    # Escape markdown headings to prevent injecting fake sections
    text = re.sub(r"^(#+)\s", r"\\\1 ", text, flags=re.MULTILINE)
    # Neutralize XML-like tags to prevent system prompt / context escape
    text = re.sub(r"<(/?[a-zA-Z_][^>]*)>", r"&lt;\1&gt;", text)
    return text


def slugify(text: str) -> str:
    words = re.findall(r"[A-Za-z0-9\u4e00-\u9fff]+", text.lower())
    slug = "-".join(words[:8]).strip("-")
    return slug[:64] or "idea-review"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--idea", required=True, help="The raw idea text to review.")
    parser.add_argument("--rounds", type=int, default=5, choices=[5, 12, 16])
    parser.add_argument("--out", default=".idea-review", help="Base output directory.")
    args = parser.parse_args()

    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    root = Path(args.out) / f"{now}-{slugify(args.idea)}"
    rounds_dir = root / "rounds"
    rounds_dir.mkdir(parents=True, exist_ok=False)

    safe_idea = sanitize_idea(args.idea)
    (root / "input.md").write_text(
        f"# Original Idea\n\n{safe_idea}\n\n## Research Summary\n\n",
        encoding="utf-8",
    )
    for n in range(1, args.rounds + 1):
        (rounds_dir / f"round-{n:02d}.md").write_text(
            f"# Round {n}\n\n"
            "## Optimist\n\n"
            "## Skeptic\n\n"
            "## Pragmatist\n\n"
            "## Synthesizer\n\n",
            encoding="utf-8",
        )
    (root / "final.md").write_text(
        "# Final Report\n\n"
        "- Verdict:\n"
        "- Confidence:\n"
        "- One-line conclusion:\n"
        "- Strongest reason:\n"
        "- Strongest counterargument:\n"
        "- Two-week validation plan:\n"
        "- Success threshold:\n"
        "- Kill criterion:\n"
        "- Next 3 actions:\n",
        encoding="utf-8",
    )
    print(root)


if __name__ == "__main__":
    main()

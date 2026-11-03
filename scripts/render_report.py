#!/usr/bin/env python3
"""Render an idea review workspace into report.md and printable report.html."""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path


def read(path: Path) -> str:
    """Read and strip text from a file.

    Args:
        path: Path to the file.

    Returns:
        The stripped text content of the file.

    Raises:
        SystemExit: If the file is not found.
    """
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        raise SystemExit(f"missing required file: {path}") from None


def inline_markdown(text: str) -> str:
    """Parse and convert basic inline Markdown to HTML.

    Args:
        text: The raw markdown text.

    Returns:
        HTML string with properly escaped text and converted inline tags (code, strong, em, links).
    """
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        r'<a href="\2">\1</a>',
        escaped,
    )
    return escaped


def simple_markdown(md: str) -> str:
    """Convert simple block Markdown to HTML.

    Args:
        md: The raw block markdown text.

    Returns:
        HTML string with converted block tags (hr, h1-h4, ul, ol, p).
    """
    lines = md.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    in_list = False
    list_tag = "ul"

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append(f"</{list_tag}>")
            in_list = False
    
    def close_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph = []

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            close_paragraph()
            close_list()
            continue
        if re.match(r"^-{3,}$", line.strip()):
            close_paragraph()
            close_list()
            out.append("<hr>")
            continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            close_paragraph()
            close_list()
            level = min(len(heading.group(1)) + 1, 4)
            out.append(f"<h{level}>{inline_markdown(heading.group(2))}</h{level}>")
            continue
        bullet = re.match(r"^[-*]\s+(.+)$", line)
        if bullet:
            close_paragraph()
            if in_list and list_tag != "ul":
                close_list()
            if not in_list:
                out.append("<ul>")
                in_list = True
                list_tag = "ul"
            out.append(f"<li>{inline_markdown(bullet.group(1))}</li>")
            continue
        ordered = re.match(r"^\d+[.)]\s+(.+)$", line)
        if ordered:
            close_paragraph()
            if in_list and list_tag != "ol":
                close_list()
            if not in_list:
                out.append("<ol>")
                in_list = True
                list_tag = "ol"
            out.append(f"<li>{inline_markdown(ordered.group(1))}</li>")
            continue
        paragraph.append(line.strip())
    close_paragraph()
    close_list()
    return "\n".join(out)


def build_report_md(root: Path) -> str:
    """Combine input, round, and final files into a single Markdown report.

    Args:
        root: The root path of the review workspace.

    Returns:
        The combined markdown content string.
    """
    input_md = read(root / "input.md")
    final_md = read(root / "final.md")
    round_parts = []
    for path in sorted((root / "rounds").glob("round-*.md")):
        round_parts.append(read(path))
    return "\n\n---\n\n".join([final_md, input_md, *round_parts]).strip() + "\n"


def build_report_html(report_md: str, title: str) -> str:
    """Render the combined Markdown report into a complete HTML document.

    Args:
        report_md: The combined markdown report content.
        title: The title for the HTML document.

    Returns:
        The full HTML document string.
    """
    body = simple_markdown(report_md)
    safe_title = html.escape(title)
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172033;
      --muted: #64748b;
      --line: #d9e0ea;
      --paper: #ffffff;
      --wash: #f6f8fb;
      --accent: #0f766e;
    }}
    body {{
      margin: 0;
      background: var(--wash);
      color: var(--ink);
      font: 15px/1.65 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    .toolbar {{
      position: sticky;
      top: 0;
      z-index: 2;
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 12px 20px;
      border-bottom: 1px solid var(--line);
      background: rgba(255,255,255,.94);
      backdrop-filter: blur(10px);
    }}
    .toolbar strong {{ color: var(--accent); }}
    button {{
      border: 1px solid var(--accent);
      border-radius: 6px;
      background: var(--accent);
      color: white;
      font-weight: 800;
      padding: 8px 12px;
      cursor: pointer;
    }}
    main {{
      width: min(920px, calc(100% - 32px));
      margin: 24px auto 48px;
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 28px;
    }}
    h1 {{ margin: 0 0 18px; font-size: 28px; line-height: 1.2; }}
    h2 {{ margin: 28px 0 10px; padding-top: 18px; border-top: 1px solid var(--line); font-size: 20px; }}
    h3 {{ margin: 22px 0 8px; color: var(--accent); font-size: 17px; text-transform: uppercase; }}
    h4 {{ margin: 18px 0 8px; color: var(--accent); font-size: 15px; }}
    code {{ border-radius: 4px; background: #eef2f7; padding: 1px 4px; }}
    a {{ color: var(--accent); }}
    hr {{ margin: 28px 0; border: 0; border-top: 1px solid var(--line); }}
    p {{ margin: 8px 0; }}
    ul, ol {{ margin: 8px 0 14px 22px; padding: 0; }}
    li {{ margin: 4px 0; }}
    @media print {{
      body {{ background: white; }}
      .toolbar {{ display: none; }}
      main {{
        width: auto;
        margin: 0;
        border: 0;
        border-radius: 0;
        padding: 0;
      }}
      hr {{ break-before: page; }}
      h1, h2, h3, h4 {{ break-after: avoid; }}
      p, li {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <div class="toolbar">
    <strong>{safe_title}</strong>
    <button type="button" onclick="window.print()">Print / Save PDF</button>
  </div>
  <main>
    <h1>{safe_title}</h1>
{body}
  </main>
</body>
</html>
"""


def main() -> None:
    """Parse arguments and render the review workspace into Markdown and HTML reports."""
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", help="Review workspace containing input.md, rounds/, final.md")
    args = parser.parse_args()
    root = Path(args.workspace)
    if not root.exists() or not root.is_dir():
        print(f"workspace not found: {root}", file=sys.stderr)
        raise SystemExit(1)
    report_md = build_report_md(root)
    (root / "report.md").write_text(report_md, encoding="utf-8")
    title = root.name
    (root / "report.html").write_text(build_report_html(report_md, title), encoding="utf-8")
    print(root / "report.html")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Render an idea review workspace into report.md and printable report.html."""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        raise SystemExit(f"missing required file: {path}") from None


_CODE_RE = re.compile(r"`([^`]+)`")
_STRONG_RE = re.compile(r"\*\*([^*]+)\*\*")
_EM_RE = re.compile(r"\*([^*]+)\*")
_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")

_HR_RE = re.compile(r"^-{3,}$")
_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$")
_BULLET_RE = re.compile(r"^[-*]\s+(.+)$")
_ORDERED_RE = re.compile(r"^\d+[.)]\s+(.+)$")


def inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    escaped = _CODE_RE.sub(r"<code>\1</code>", escaped)
    escaped = _STRONG_RE.sub(r"<strong>\1</strong>", escaped)
    escaped = _EM_RE.sub(r"<em>\1</em>", escaped)
    escaped = _LINK_RE.sub(r'<a href="\2">\1</a>', escaped)
    return escaped


def simple_markdown(md: str) -> str:
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
        if paragraph:
            out.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph.clear()

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            close_paragraph()
            close_list()
            continue
        if _HR_RE.match(stripped):
            close_paragraph()
            close_list()
            out.append("<hr>")
            continue
        heading = _HEADING_RE.match(line)
        if heading:
            close_paragraph()
            close_list()
            level = min(len(heading.group(1)) + 1, 4)
            out.append(f"<h{level}>{inline_markdown(heading.group(2))}</h{level}>")
            continue
        bullet = _BULLET_RE.match(line)
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
        ordered = _ORDERED_RE.match(line)
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
        paragraph.append(stripped)
    close_paragraph()
    close_list()
    return "\n".join(out)


def build_report_md(root: Path) -> str:
    input_md = read(root / "input.md")
    final_md = read(root / "final.md")
    round_parts = []
    for path in sorted((root / "rounds").glob("round-*.md")):
        round_parts.append(read(path))
    return "\n\n---\n\n".join([final_md, input_md, *round_parts]).strip() + "\n"


def build_report_html(report_md: str, title: str) -> str:
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

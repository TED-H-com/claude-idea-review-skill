import sys
from pathlib import Path
import pytest
from unittest.mock import patch, mock_open

sys.path.insert(0, str(Path("scripts").resolve()))
import render_report

def test_inline_markdown():
    assert render_report.inline_markdown("A < B & C > D") == "A &lt; B &amp; C &gt; D"
    assert render_report.inline_markdown("Here is `code` block") == "Here is <code>code</code> block"
    assert render_report.inline_markdown("This is **bold** text") == "This is <strong>bold</strong> text"
    assert render_report.inline_markdown("This is *italic* text") == "This is <em>italic</em> text"
    assert render_report.inline_markdown("Check [this](https://example.com) out") == 'Check <a href="https://example.com">this</a> out'
    assert render_report.inline_markdown("**Bold** `code` with [link](http://test.com)") == '<strong>Bold</strong> <code>code</code> with <a href="http://test.com">link</a>'

def test_simple_markdown():
    md = """# Heading 1
## Heading 2
### Heading 3
#### Heading 4

This is a normal paragraph.
It can span multiple lines.

---

- Bullet 1
- Bullet 2

1. Item 1
2. Item 2"""

    html = render_report.simple_markdown(md)

    # Note from source: heading level = min(len(heading.group(1)) + 1, 4)
    # And it only matches #{1,3}
    assert "<h2>Heading 1</h2>" in html
    assert "<h3>Heading 2</h3>" in html
    assert "<h4>Heading 3</h4>" in html
    assert "<p>#### Heading 4</p>" in html # Not matched by #{1,3} regex

    assert "<p>This is a normal paragraph. It can span multiple lines.</p>" in html
    assert "<hr>" in html

    assert "<ul>\n<li>Bullet 1</li>\n<li>Bullet 2</li>\n</ul>" in html
    assert "<ol>\n<li>Item 1</li>\n<li>Item 2</li>\n</ol>" in html

def test_build_report_md(tmp_path):
    (tmp_path / "input.md").write_text("Input content", encoding="utf-8")
    (tmp_path / "final.md").write_text("Final verdict", encoding="utf-8")

    rounds_dir = tmp_path / "rounds"
    rounds_dir.mkdir()
    (rounds_dir / "round-01.md").write_text("Round 1", encoding="utf-8")
    (rounds_dir / "round-02.md").write_text("Round 2", encoding="utf-8")

    result = render_report.build_report_md(tmp_path)

    expected = "Final verdict\n\n---\n\nInput content\n\n---\n\nRound 1\n\n---\n\nRound 2\n"
    assert result == expected

def test_build_report_html():
    md = "# Final Verdict"
    title = "My <Safe> Title"

    html = render_report.build_report_html(md, title)

    assert "My &lt;Safe&gt; Title" in html # HTML Escaped title
    assert "<h2>Final Verdict</h2>" in html # Heading 1 gets converted to h2
    assert "<!doctype html>" in html
    assert "Print / Save PDF" in html

@patch("sys.argv", ["render_report.py", "non_existent_workspace"])
def test_main_workspace_not_found(capsys):
    with pytest.raises(SystemExit) as exc:
        render_report.main()

    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "workspace not found" in captured.err

def test_read_missing_file():
    with pytest.raises(SystemExit) as exc:
        render_report.read(Path("missing_file.md"))

    assert "missing required file" in str(exc.value)

def test_main_with_real_tmp_path(tmp_path, capsys):
    # Setup a valid workspace
    (tmp_path / "input.md").write_text("input", encoding="utf-8")
    (tmp_path / "final.md").write_text("final", encoding="utf-8")
    rounds_dir = tmp_path / "rounds"
    rounds_dir.mkdir()
    (rounds_dir / "round-01.md").write_text("round 1", encoding="utf-8")

    with patch("sys.argv", ["render_report.py", str(tmp_path)]):
        render_report.main()

    assert (tmp_path / "report.md").exists()
    assert (tmp_path / "report.html").exists()

    captured = capsys.readouterr()
    assert str(tmp_path / "report.html") in captured.out

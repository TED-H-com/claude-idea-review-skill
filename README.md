# Claude Idea Review Skill

**English** · [繁體中文](README.zh-TW.md)

A Claude Code skill that pressure-tests an idea over 5, 12, or 16 rounds of structured debate and saves a verdict with a printable report.

**Project page:** https://ted-h-com.github.io/claude-idea-review-skill/

An open-source skill for the **Personal IP Co-Building / Coaching Program** (個人 IP 陪跑計畫) and the **自由工坊 Discord community**. License: MIT.

Use it when you have a product, content, startup, feature, creator-IP, community, or business idea and want a structured review before you spend serious time building it.

## What it does

The skill runs a 5, 12, or 16-round review panel inside Claude Code (5 by default). Before the first round it:

1. Checks which optional provider CLIs are installed and answering: Codex CLI, Antigravity (`agy`) or Gemini CLI, and Grok CLI.
2. Researches the idea on the web when tools are available: competitors, pricing, demand, technical and platform limits, and legal or distribution constraints.

Four thinking personalities then argue through the rounds. Round 1 is first positions, the middle rounds are a clash, and in the final round every personality commits to build, validate, pivot, or stop. The result is a verdict with a kill criterion, saved as local files you can print.

The review itself is written by Claude, following `SKILL.md`. The three Python scripts only check providers, create the review folder, and render the report.

## Personalities

These are thinking personalities, not departments, roles, or a claim that four models are involved:

- `Optimist`: expands the strongest possible version of the idea.
- `Skeptic`: attacks weak assumptions, hidden costs, and reasons it could fail.
- `Pragmatist`: turns the debate into tests, MVP shape, constraints, and trade-offs.
- `Synthesizer`: integrates disagreement and tracks what evidence would change the conclusion.

After round 1, each personality has to respond to at least one earlier point from another personality.

## Providers and fallback

`scripts/check_providers.py --smoke` looks for each CLI on your `PATH` and sends every CLI it finds one short prompt, `Reply OK only.`

| Provider | CLI it looks for | Smoke test | Key variables it reports |
|---|---|---|---|
| Codex | `codex` | `codex exec`, prompt on stdin | `OPENAI_API_KEY` |
| Gemini | `agy` (Antigravity), else `gemini` | `-p "Reply OK only."` | `GEMINI_API_KEY`, `GOOGLE_API_KEY` |
| Grok | `grok` | `grok -p "Reply OK only."` | `XAI_API_KEY`, `GROK_API_KEY` |

It also reports whether `OPENROUTER_API_KEY` is set. It lists variable names only, never their values. A smoke test passes when the CLI exits with code 0 and prints something within 45 seconds.

What `SKILL.md` tells Claude to do with the result:

- A CLI that exists but cannot answer is reported as `測不到帳號` (account not reachable).
- For a missing provider, Claude asks once whether you have an API key, and whether you prefer the provider's own API or OpenRouter.
- It does not wait for keys. Without one, Claude simulates that provider's style and labels it, for example `Claude 模擬 Grok`.
- Simulated styles: Codex is rigorous and systematic, Grok is direct and practical-first, and Gemini is broad, weighing whole-system trade-offs.

Two caveats come from the script itself. `agy -p` can exit 0 with empty output when it is not attached to a terminal, so a failed Antigravity smoke test is inconclusive. When the `gemini` CLI is found but does not answer, the script adds a hint that Google moved its free, Pro, and Ultra consumer tiers to Antigravity in 2026, and that the Gemini CLI still works with a paid `GEMINI_API_KEY` or an Enterprise or Code Assist license.

## Review Criteria & Evaluation Rubrics

The panel evaluates your idea based on 5 core criteria: **Problem-Solution Fit**, **Market Demand**, **Execution**, **Differentiation**, and **Business Model**.

The final confidence score maps to a clear verdict:

- **80-100 (`worth_building`):** Strong signal across all criteria. Clear path to MVP and first revenue.
- **60-79 (`validate_first`):** Good potential, but relies on risky assumptions. Needs a low-cost test before building.
- **40-59 (`pivot`):** Core problem exists, but the solution or market segment is flawed. Needs significant adjustment.
- **0-39 (`not_worth_building`):** Fatal flaws in demand, feasibility, or economics. Better to kill the idea.

## Outputs

Each run gets its own folder under `.idea-review/`, in the directory where the review runs:

```text
.idea-review/<YYYYMMDD-HHMMSS>-<slug>/
├── input.md          your idea, then the research summary
├── rounds/
│   ├── round-01.md   one section per personality
│   └── ...
├── final.md          the verdict
├── report.md         final.md, then input.md, then every round
└── report.html       the same content as a printable page
```

The slug comes from the first eight words of the idea, and Chinese characters are kept. `report.html` is a static file: open it in a browser and use the **Print / Save PDF** button. When printed, the button bar is hidden and each part starts on a new page.

If you run a review inside a Git repository, add `.idea-review/` to that repository's `.gitignore` unless you want to commit the reviews.

## Requirements

- **Claude Code**. The review runs inside it.
- **Python 3.8+** on your `PATH`, used only by the helper scripts. They use the standard library only.
- **Optional:** Codex CLI, Antigravity (`agy`) or Gemini CLI, and Grok CLI for native cross-checks. None is required; Claude simulates any provider that is missing.

## Install

Clone it into your personal skills folder:

```bash
# macOS / Linux
git clone https://github.com/TED-H-com/claude-idea-review-skill.git \
  ~/.claude/skills/idea-review-panel
```

```powershell
# Windows (PowerShell)
git clone https://github.com/TED-H-com/claude-idea-review-skill.git `
  "$env:USERPROFILE\.claude\skills\idea-review-panel"
```

A running Claude Code session picks up the new skill without a restart. If `~/.claude/skills/` did not exist when the session started, run `/reload-skills` once.

To use it in one project only, clone it into that project's `.claude/skills/idea-review-panel/` instead.

Update later with:

```bash
git -C ~/.claude/skills/idea-review-panel pull
```

> **Windows note:** the helper scripts are called with `python3`, but on Windows the command is usually `python`. If typing `python` opens the Microsoft Store, that is a placeholder alias, not a real interpreter. Install Python from [python.org](https://www.python.org/downloads/) or run `winget install Python.Python.3.12`, then reopen your terminal.

## Usage

Ask Claude Code to validate an idea. The skill triggers from its description:

```text
幫我驗證這個點子：<你的 idea>
```

English works too, for example `Validate this idea: <your idea>`. You can also call it directly with `/idea-review-panel`.

The default is 5 rounds; ask for 12 or 16 for a deeper review. A Chinese request gets a Traditional Chinese review by default; otherwise the review follows your language. When it finishes, Claude replies with the verdict summary and the file paths.

## Usage Examples

You can provide a one-line idea or a detailed context. Here are some examples:

- **Software / SaaS:** "Validate this idea: A Notion-like workspace specifically for lawyers, focusing on secure document management and case linking."
- **Content / Creator:** "幫我驗證這個點子：一個專門教非工程師用 AI 工具自動化日常工作的 YouTube 頻道，一開始先做 Notion 和 Zapier 教學。"
- **Community / Business:** "Validate this idea: A paid Discord community for indie hackers building micro-SaaS, offering weekly teardowns and accountability groups."

## Helper scripts

The skill runs these for you. To run them by hand, use the installed path, and run them from the folder where `.idea-review/` should appear (on Windows, use `python` instead of `python3`):

```bash
SKILL=~/.claude/skills/idea-review-panel

# Which providers are installed and answering (sends one short prompt to each CLI found)
python3 "$SKILL/scripts/check_providers.py" --smoke

# Create a review folder: --rounds accepts 5, 12, or 16; --out changes the base folder
python3 "$SKILL/scripts/init_review.py" --idea "your idea" --rounds 5

# Render report.md and report.html from a review folder
python3 "$SKILL/scripts/render_report.py" .idea-review/<folder>
```

Without `--smoke`, `check_providers.py` only reports which CLIs and key variables exist, and sends no prompt.

## Final verdict format

`final.md` contains:

- `Verdict`: `worth_building`, `validate_first`, `pivot`, or `not_worth_building`
- `Confidence`: 0 to 100
- One-line conclusion
- Strongest reason
- Strongest counterargument
- Two-week validation plan
- Success threshold
- Kill criterion
- Next 3 actions

## Limits

- The review is driven by the instructions in `SKILL.md`, not by code. Round structure, research, and fallbacks depend on Claude following them, and results vary between runs.
- There is no API client in the repo. If you give Claude a key, how it calls that API is up to Claude in that session.
- A failed `agy` smoke test does not prove the account is unusable (see above).
- `render_report.py` handles headings, lists, paragraphs, and inline code, bold, italics, and links. Tables and fenced code blocks are not supported. The HTML is always marked `lang="zh-Hant"`, even for an English review.
- No tests, CI, or releases yet; install from the `main` branch.

## Related project

[ai-brainstorming](https://github.com/TED-H-com/ai-brainstorming) ([project page](https://ted-h-com.github.io/ai-brainstorming/)) is a web version of the same idea: the same 5, 12, or 16 rounds with a research, clash, and converge arc, but with five model seats called through OpenRouter, and a transcript that can be emailed when SMTP is configured. This skill runs inside your own Claude Code session and uses four personalities instead of model seats.

## License

MIT. See [LICENSE](LICENSE).

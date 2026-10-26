---
name: idea-review-panel
description: Validate product, startup, content, creator-IP, community, or business ideas with a 5/12/16-round Claude Code review panel.
---

# Idea Review Panel

Use this skill when the user asks Claude Code to validate, pressure-test, or decide whether an idea is worth building.

The skill is for idea validation, not casual encouragement. It should produce saved round-by-round analysis and a concrete final conclusion.

## Output

Create a review workspace unless the user asks for inline-only output:

```text
.idea-review/<short-slug>/
├── input.md
├── rounds/
│   ├── round-01.md
│   ├── round-02.md
│   └── ...
├── final.md
├── report.md
└── report.html
```

### Running the bundled scripts

The helper scripts live in this skill's `scripts/` directory. Reference them by absolute path: substitute `<skill-dir>` with the folder that contains this `SKILL.md` (Claude Code provides the skill's location when it loads). Run them from the user's working directory so the `.idea-review/` workspace is created where the user expects it, not inside the skill folder. On Windows, use `python` instead of `python3`.

Scaffold a workspace with:

```bash
python3 "<skill-dir>/scripts/init_review.py" --idea "<idea text>" --rounds 5
```

Render final reports with:

```bash
python3 "<skill-dir>/scripts/render_report.py" <review-workspace>
```

## Startup Checks

Before running the review:

1. Check which native CLIs/accounts are usable:

   ```bash
   python3 "<skill-dir>/scripts/check_providers.py" --smoke
   ```

2. If a CLI exists but cannot answer, say `測不到帳號` for that provider.
3. If Codex / Antigravity-Gemini / xAI-Grok is unavailable, ask once whether the user has an API key and whether they prefer original provider API or OpenRouter.
4. Do not block indefinitely waiting for keys. If no key is provided, continue with Claude simulation.
5. Do real web research first when tools are available.

Provider preference:

- Use Codex CLI for Codex-style analysis when available.
- Use Antigravity CLI (`agy`) or Gemini API for Gemini-style analysis when available.
- Use Grok CLI or xAI API for Grok-style analysis when available.
- Use Claude for orchestration and for any missing provider simulation.

## Personalities

Run 5 / 12 / 16 rounds. Default to 5.

These are thinking personalities, not departments, roles, or identity claims:

- `Optimist`: expands the strongest possible version of the idea and why it could work.
- `Skeptic`: attacks weak assumptions, hidden costs, and reasons it could fail.
- `Pragmatist`: converts the debate into tests, MVP shape, constraints, and tradeoffs.
- `Synthesizer`: integrates disagreement and tracks what evidence would change the conclusion.

When Claude simulates a missing provider/personality, use these style prompts:

- Codex simulation: rigorous, systematic, structured, careful about assumptions and implementation details.
- Grok simulation: direct, practical-first, skeptical of pretty words, willing to state uncomfortable points plainly.
- Gemini simulation: broad, comprehensive, whole-system thinking, many tradeoffs, and overall product quality.

Say `Claude 模擬 Codex/Grok/Gemini` when attribution matters.

## Research First

At the start of every review, gather current evidence from the web when tools are available. Look for:

- Direct competitors and adjacent products.
- Pricing/business model signals.
- Existing user behavior or market demand.
- Technical feasibility and current platform/API limits.
- Legal, policy, or distribution constraints.

Save the research summary near the top of `input.md` or in `rounds/round-01.md`. Later rounds must distinguish evidence from assumptions.

## Workflow

1. Capture the user's exact idea in `input.md`.
2. Run startup checks.
3. Do web research.
4. Choose 5 / 12 / 16 rounds.
5. For each round, write one section per personality in `rounds/round-NN.md`.
6. Each personality must reference at least one prior personality after round 1.
7. Keep disagreement visible. Do not converge too early.
8. Write `final.md`.
9. Generate `report.md` and printable `report.html`.
10. Reply with the verdict summary and file paths.

## Round Guidance

Round 1: first positions.

- Optimist makes the strongest case.
- Skeptic names the likely failure.
- Pragmatist proposes the smallest useful test.
- Synthesizer states the current decision tension.

Middle rounds: clash.

- Optimist must revise the strongest case if Skeptic found a real issue.
- Skeptic must attack a concrete premise, not vibe.
- Pragmatist must turn disagreement into an experiment.
- Synthesizer must state what evidence would change the verdict.

Final round: convergence.

- Each personality must commit to build / validate / pivot / stop.
- Synthesizer must name the deciding assumption.

## Usage Examples

When the user asks for a review, they can provide a one-line idea or a detailed context. Here are some examples to guide them:

- **Software / SaaS:** "Validate this idea: A Notion-like workspace specifically for lawyers, focusing on secure document management and case linking."
- **Content / Creator:** "幫我驗證這個點子：一個專門教非工程師用 AI 工具自動化日常工作的 YouTube 頻道，一開始先做 Notion 和 Zapier 教學。"
- **Community / Business:** "Validate this idea: A paid Discord community for indie hackers building micro-SaaS, offering weekly teardowns and accountability groups."

## Review Criteria & Evaluation Rubrics

The panel evaluates the idea across 5 core criteria:

1. **Problem-Solution Fit:** Does the proposed solution effectively address a real, painful problem?
2. **Market Demand:** Is there a sizable, reachable market willing to pay for this?
3. **Execution:** Can this specific team (or the user) realistically build and distribute this with current constraints?
4. **Differentiation:** How does it stand out against existing alternatives or the status quo?
5. **Business Model:** Is there a clear, viable path to revenue and sustainability?

The final verdict and confidence score are mapped to this rubric:

- **80-100 (`worth_building`):** Strong signal across all criteria. Clear path to MVP and first revenue. Minimal critical assumptions left unvalidated.
- **60-79 (`validate_first`):** Good potential, but relies on 1-2 risky assumptions (e.g., willing to pay, technical feasibility). Needs a specific, low-cost test before full build.
- **40-59 (`pivot`):** Core problem exists, but the current solution, market segment, or distribution channel is flawed. Needs significant adjustment.
- **0-39 (`not_worth_building`):** Fatal flaws in demand, feasibility, or unit economics. Better to kill the idea and move on.

## Final Report

`final.md` must include:

- `Verdict`: `worth_building`, `validate_first`, `pivot`, or `not_worth_building`.
- `Confidence`: 0-100.
- `One-line conclusion`.
- `Strongest reason`.
- `Strongest counterargument`.
- `Two-week validation plan`.
- `Success threshold`.
- `Kill criterion`.
- `Next 3 actions`.

`report.html` must:

- Show the final conclusion first.
- Show round-by-round sections after the conclusion.
- Include a visible Print / Save PDF button that calls `window.print()`.
- Include print CSS that hides controls and keeps sections readable.
- Be usable as a static local file.

## Tone

Default to Traditional Chinese when the user's request is Chinese. Otherwise use the user's language.

Be direct. The user wants a decision aid, not encouragement.

#!/usr/bin/env python3
"""Check which optional idea-review providers are available to Claude Code."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import asdict, dataclass


@dataclass
class ProviderStatus:
    """Represents the availability and status of an AI provider CLI."""
    provider: str
    cli: str | None
    cli_found: bool
    smoke_ok: bool | None
    api_env: list[str]
    openrouter_env: bool
    note: str


def run_smoke(cmd: list[str], stdin: str | None = None, timeout: int = 45) -> tuple[bool, str]:
    """Run a tiny prompt through a CLI to verify it can answer.

    Args:
        cmd: The command and its arguments to run.
        stdin: Optional input to send to the command via stdin.
        timeout: Maximum seconds to wait for the command to finish.

    Returns:
        A tuple containing a boolean indicating success (exit code 0 and non-empty stdout)
        and the last 500 characters of the combined stdout and stderr output.
    """
    try:
        res = subprocess.run(
            cmd,
            input=stdin,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except Exception as exc:
        return False, str(exc)
    combined = (res.stdout + "\n" + res.stderr).strip()
    return res.returncode == 0 and bool(res.stdout.strip()), combined[-500:]


def env_present(names: list[str]) -> list[str]:
    """Check which environment variables from a given list are currently set.

    Args:
        names: List of environment variable names to check.

    Returns:
        A list of environment variable names that are present and not empty.
    """
    return [name for name in names if os.environ.get(name)]


def check_codex(smoke: bool) -> ProviderStatus:
    """Check the availability of the Codex CLI and relevant API keys.

    Args:
        smoke: Whether to run a smoke test if the CLI is found.

    Returns:
        A ProviderStatus object containing the check results.
    """
    cli = shutil.which("codex")
    smoke_ok: bool | None = None
    note = "not checked"
    if cli and smoke:
        smoke_ok, note = run_smoke([cli, "exec"], "Reply OK only.\n")
    elif not cli:
        note = "codex cli not found"
    return ProviderStatus(
        provider="codex",
        cli=cli,
        cli_found=bool(cli),
        smoke_ok=smoke_ok,
        api_env=env_present(["OPENAI_API_KEY"]),
        openrouter_env=bool(os.environ.get("OPENROUTER_API_KEY")),
        note=note,
    )


def check_gemini(smoke: bool) -> ProviderStatus:
    """Check the availability of the Antigravity (agy) or Gemini CLI and relevant API keys.

    Args:
        smoke: Whether to run a smoke test if the CLI is found.

    Returns:
        A ProviderStatus object containing the check results.
    """
    cli = shutil.which("agy") or shutil.which("gemini")
    smoke_ok: bool | None = None
    note = "not checked"
    if cli and smoke:
        # Both Antigravity's `agy` and Google's `gemini` take `-p "<prompt>"` for a
        # one-shot headless answer. Caveat: `agy -p` can exit 0 with EMPTY stdout
        # under a non-TTY (piped) run, so a failed smoke for `agy` is inconclusive.
        smoke_ok, note = run_smoke([cli, "-p", "Reply OK only."])
        if smoke_ok is False and "gemini" in os.path.basename(cli).lower():
            # gemini CLI present but unable to answer. Likely cause from 2026 on:
            # Google moved the free/Pro/Ultra consumer tiers to Antigravity, so a
            # plain `gemini` login no longer serves requests. gemini CLI still works
            # with a paid Gemini API key or an Enterprise/Code Assist license.
            note = (
                f"{note}\n\nhint: gemini CLI found but did not answer. Google's 2026 "
                "transition moved free/Pro/Ultra tiers to Antigravity (agy); gemini CLI "
                "still works via a paid GEMINI_API_KEY or an Enterprise/Code Assist "
                "license. Consider using agy, or supply a paid API key."
            )
    elif not cli:
        note = "antigravity/gemini cli not found"
    return ProviderStatus(
        provider="gemini",
        cli=cli,
        cli_found=bool(cli),
        smoke_ok=smoke_ok,
        api_env=env_present(["GEMINI_API_KEY", "GOOGLE_API_KEY"]),
        openrouter_env=bool(os.environ.get("OPENROUTER_API_KEY")),
        note=note,
    )


def check_grok(smoke: bool) -> ProviderStatus:
    """Check the availability of the Grok CLI and relevant API keys.

    Args:
        smoke: Whether to run a smoke test if the CLI is found.

    Returns:
        A ProviderStatus object containing the check results.
    """
    cli = shutil.which("grok")
    smoke_ok: bool | None = None
    note = "not checked"
    if cli and smoke:
        # `grok -p "<prompt>"` is the headless form for both xAI's official
        # Grok CLI and the community grok-dev CLI. There is no `grok exec`.
        smoke_ok, note = run_smoke([cli, "-p", "Reply OK only."])
    elif not cli:
        note = "grok cli not found"
    return ProviderStatus(
        provider="grok",
        cli=cli,
        cli_found=bool(cli),
        smoke_ok=smoke_ok,
        # Official Grok CLI reads XAI_API_KEY; community grok-dev uses GROK_API_KEY.
        api_env=env_present(["XAI_API_KEY", "GROK_API_KEY"]),
        openrouter_env=bool(os.environ.get("OPENROUTER_API_KEY")),
        note=note,
    )


def main() -> None:
    """Parse arguments and print the JSON status array for all providers."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="Run a tiny prompt through found CLIs.")
    args = parser.parse_args()
    statuses = [check_codex(args.smoke), check_gemini(args.smoke), check_grok(args.smoke)]
    print(json.dumps([asdict(s) for s in statuses], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

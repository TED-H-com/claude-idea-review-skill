import sys
from pathlib import Path
import json
import pytest
import os
from unittest.mock import patch, MagicMock

# Add scripts directory to path to allow importing check_providers
sys.path.insert(0, str(Path("scripts").resolve()))
import check_providers

@patch("check_providers.shutil.which")
@patch("check_providers.subprocess.run")
def test_check_codex_cli_present_smoke_ok(mock_run, mock_which):
    mock_which.return_value = "/usr/bin/codex"

    mock_run_res = MagicMock()
    mock_run_res.returncode = 0
    mock_run_res.stdout = "OK\n"
    mock_run_res.stderr = ""
    mock_run.return_value = mock_run_res

    with patch.dict(os.environ, {"OPENAI_API_KEY": "fake_key"}):
        status = check_providers.check_codex(smoke=True)

    assert status.provider == "codex"
    assert status.cli == "/usr/bin/codex"
    assert status.cli_found is True
    assert status.smoke_ok is True
    assert status.api_env == ["OPENAI_API_KEY"]
    assert status.openrouter_env is False

@patch("check_providers.shutil.which")
@patch("check_providers.subprocess.run")
def test_check_codex_cli_present_smoke_fails(mock_run, mock_which):
    mock_which.return_value = "/usr/bin/codex"

    mock_run_res = MagicMock()
    mock_run_res.returncode = 1
    mock_run_res.stdout = ""
    mock_run_res.stderr = "Error occurred"
    mock_run.return_value = mock_run_res

    status = check_providers.check_codex(smoke=True)

    assert status.smoke_ok is False
    assert "Error occurred" in status.note

@patch("check_providers.shutil.which")
def test_check_codex_cli_missing(mock_which):
    mock_which.return_value = None

    status = check_providers.check_codex(smoke=False)

    assert status.cli is None
    assert status.cli_found is False
    assert status.smoke_ok is None
    assert status.note == "codex cli not found"

@patch("check_providers.shutil.which")
@patch("check_providers.subprocess.run")
def test_check_gemini_cli_present_smoke_ok(mock_run, mock_which):
    mock_which.return_value = "/usr/bin/agy"

    mock_run_res = MagicMock()
    mock_run_res.returncode = 0
    mock_run_res.stdout = "OK\n"
    mock_run_res.stderr = ""
    mock_run.return_value = mock_run_res

    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
        status = check_providers.check_gemini(smoke=True)

    assert status.provider == "gemini"
    assert status.cli == "/usr/bin/agy"
    assert status.cli_found is True
    assert status.smoke_ok is True
    assert status.api_env == ["GEMINI_API_KEY"]

@patch("check_providers.shutil.which")
@patch("check_providers.subprocess.run")
def test_check_gemini_cli_present_smoke_fails_with_fallback_hint(mock_run, mock_which):
    # Returning gemini specifically so it hits the hint path
    mock_which.side_effect = lambda cmd: "/usr/bin/gemini" if cmd == "gemini" else None

    mock_run_res = MagicMock()
    mock_run_res.returncode = 1
    mock_run_res.stdout = ""
    mock_run_res.stderr = "Auth failed"
    mock_run.return_value = mock_run_res

    status = check_providers.check_gemini(smoke=True)

    assert status.smoke_ok is False
    assert "Auth failed" in status.note
    assert "gemini CLI found but did not answer" in status.note
    assert "transition moved free/Pro/Ultra tiers to Antigravity (agy)" in status.note

@patch("check_providers.shutil.which")
def test_check_gemini_cli_missing(mock_which):
    mock_which.return_value = None

    status = check_providers.check_gemini(smoke=False)

    assert status.cli is None
    assert status.cli_found is False
    assert status.smoke_ok is None
    assert status.note == "antigravity/gemini cli not found"


@patch("check_providers.shutil.which")
@patch("check_providers.subprocess.run")
def test_check_grok_cli_present_smoke_ok(mock_run, mock_which):
    mock_which.return_value = "/usr/bin/grok"

    mock_run_res = MagicMock()
    mock_run_res.returncode = 0
    mock_run_res.stdout = "OK\n"
    mock_run_res.stderr = ""
    mock_run.return_value = mock_run_res

    with patch.dict(os.environ, {"XAI_API_KEY": "fake_key"}):
        status = check_providers.check_grok(smoke=True)

    assert status.provider == "grok"
    assert status.cli == "/usr/bin/grok"
    assert status.cli_found is True
    assert status.smoke_ok is True
    assert status.api_env == ["XAI_API_KEY"]

@patch("check_providers.shutil.which")
def test_check_grok_cli_missing(mock_which):
    mock_which.return_value = None

    status = check_providers.check_grok(smoke=False)

    assert status.cli is None
    assert status.cli_found is False
    assert status.smoke_ok is None
    assert status.note == "grok cli not found"


@patch("sys.argv", ["check_providers.py", "--smoke"])
@patch("check_providers.check_codex")
@patch("check_providers.check_gemini")
@patch("check_providers.check_grok")
def test_main(mock_check_grok, mock_check_gemini, mock_check_codex, capsys):
    mock_check_codex.return_value = check_providers.ProviderStatus("codex", "/usr/bin/codex", True, True, [], False, "ok")
    mock_check_gemini.return_value = check_providers.ProviderStatus("gemini", "/usr/bin/agy", True, True, [], False, "ok")
    mock_check_grok.return_value = check_providers.ProviderStatus("grok", "/usr/bin/grok", True, True, [], False, "ok")

    check_providers.main()

    captured = capsys.readouterr()
    output = json.loads(captured.out)

    assert len(output) == 3
    assert output[0]["provider"] == "codex"
    assert output[1]["provider"] == "gemini"
    assert output[2]["provider"] == "grok"

    mock_check_codex.assert_called_once_with(True)
    mock_check_gemini.assert_called_once_with(True)
    mock_check_grok.assert_called_once_with(True)

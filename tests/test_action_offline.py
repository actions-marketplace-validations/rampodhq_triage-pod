from __future__ import annotations

from pathlib import Path

from pytest import MonkeyPatch

from triagepod.interfaces.github_action.main import run_action


def test_offline_action_runs_with_sample_event(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    summary = tmp_path / "summary.md"
    fixture = Path("tests/fixtures/issues_opened.json").resolve()
    config = Path("examples/oss-library.yml").resolve()

    monkeypatch.setenv("TRIAGEPOD_OFFLINE", "true")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(fixture))
    monkeypatch.setenv("GITHUB_EVENT_NAME", "issues")
    monkeypatch.setenv("INPUT_CONFIG_PATH", str(config))
    monkeypatch.setenv("INPUT_DRY_RUN", "true")
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))

    result = run_action()

    assert result.classification.classification.value == "bug"
    assert result.actions.dry_run is True

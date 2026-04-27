from __future__ import annotations

import os
import sys
from pathlib import Path

from pydantic import ValidationError

from triagepod.application.config import TriagePodConfig
from triagepod.application.ports import ConfigRepository
from triagepod.application.use_cases import RunTriageUseCase
from triagepod.domain.models import Repository, TriageRequest, TriageResult
from triagepod.infrastructure.config_repository import (
    ConfigLoadError,
    GitHubConfigRepository,
    LocalConfigRepository,
)
from triagepod.infrastructure.github import (
    GitHubClient,
    GitHubCommentRepository,
    GitHubDiscussionCapabilityService,
    GitHubIssueRepository,
    GitHubLabelService,
    OfflineCommentRepository,
    OfflineIssueRepository,
    OfflineLabelService,
    StaticDiscussionCapabilityService,
    issue_from_event,
    load_event,
    repository_from_event,
)
from triagepod.infrastructure.logger import configure_logging
from triagepod.infrastructure.renderer import ProfessionalCommentRenderer


class ActionError(RuntimeError):
    pass


def main() -> None:
    try:
        result = run_action()
        write_step_summary(result)
    except Exception as exc:
        print(f"TriagePod failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def run_action() -> TriageResult:
    logger = configure_logging(os.getenv("INPUT_LOG_LEVEL", "INFO"))
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        msg = "GITHUB_EVENT_PATH is required"
        raise ActionError(msg)

    payload = load_event(event_path)
    event_name = os.getenv("GITHUB_EVENT_NAME", "issues")
    event_action = str(payload.get("action") or "")
    if event_name != "issues" or event_action != "opened":
        msg = "TriagePod V1 supports only the issues.opened event"
        raise ActionError(msg)

    repository = repository_from_event(payload)
    request = TriageRequest(
        repository=repository,
        issue=issue_from_event(payload),
        event_name=event_name,
        event_action=event_action,
        event_id=os.getenv("GITHUB_RUN_ID"),
    )

    config_path = os.getenv("INPUT_CONFIG_PATH", ".github/triagepod.yml")
    dry_run_override = parse_optional_bool(os.getenv("INPUT_DRY_RUN", ""))
    offline = parse_optional_bool(os.getenv("TRIAGEPOD_OFFLINE", "")) is True

    if offline:
        config = load_config(LocalConfigRepository(), repository, config_path, dry_run_override)
        use_case = RunTriageUseCase(
            issue_repository=OfflineIssueRepository(),
            comment_repository=OfflineCommentRepository(),
            label_service=OfflineLabelService(),
            discussion_capability_service=StaticDiscussionCapabilityService(
                repository.has_discussions
            ),
            comment_renderer=ProfessionalCommentRenderer(),
            logger=logger,
        )
        return use_case.run(request, config)

    token = os.getenv("INPUT_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not token:
        msg = "github_token input is required for GitHub Action execution"
        raise ActionError(msg)

    client = GitHubClient(token=token)
    config = load_config(GitHubConfigRepository(client), repository, config_path, dry_run_override)
    use_case = RunTriageUseCase(
        issue_repository=GitHubIssueRepository(client),
        comment_repository=GitHubCommentRepository(client),
        label_service=GitHubLabelService(client),
        discussion_capability_service=GitHubDiscussionCapabilityService(client),
        comment_renderer=ProfessionalCommentRenderer(),
        logger=logger,
    )
    return use_case.run(request, config)


def load_config(
    repository: ConfigRepository, repo: Repository, path: str, dry_run_override: bool | None
) -> TriagePodConfig:
    try:
        config = repository.load(repo, path)
    except (ConfigLoadError, ValidationError) as exc:
        msg = f"Unable to load TriagePod config: {exc}"
        raise ActionError(msg) from exc

    if dry_run_override is None:
        return config
    return config.model_copy(
        update={"automation": config.automation.model_copy(update={"dry_run": dry_run_override})}
    )


def parse_optional_bool(value: str) -> bool | None:
    if not value:
        return None
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    msg = f"Invalid boolean value: {value}"
    raise ActionError(msg)


def write_step_summary(result: TriageResult) -> None:
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    lines = [
        "## TriagePod summary",
        "",
        f"- Classification: `{result.classification.classification.value}`",
        f"- Missing-info status: `{result.missing_info.status.value}`",
        f"- Duplicate candidates: `{len(result.duplicates)}`",
        f"- Label suggestions: `{len(result.label_suggestions)}`",
        f"- Dry-run: `{str(result.actions.dry_run).lower()}`",
    ]
    Path(summary_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

from __future__ import annotations

from triagepod.application.analyzers import (
    Classifier,
    DiscussionRouter,
    DuplicateAnalyzer,
    LabelEngine,
    MissingInfoAnalyzer,
)
from triagepod.application.config import TriagePodConfig
from triagepod.domain.models import (
    ConfidenceBand,
    Issue,
    IssueClassification,
    MissingInfoStatus,
    Repository,
    TriageRequest,
)


def make_request(title: str, body: str, labels: tuple[str, ...] = ()) -> TriageRequest:
    return TriageRequest(
        repository=Repository(owner="octo", name="demo", full_name="octo/demo"),
        issue=Issue(
            number=1,
            title=title,
            body=body,
            url="https://api.github.com/repos/octo/demo/issues/1",
            html_url="https://github.com/octo/demo/issues/1",
            labels=labels,
        ),
        event_name="issues",
        event_action="opened",
    )


def test_missing_info_analyzer_reports_specific_fields() -> None:
    result = MissingInfoAnalyzer().analyze(make_request("Bug", "not working"), TriagePodConfig())

    assert result.status == MissingInfoStatus.INCOMPLETE
    assert {field.key for field in result.missing_fields} >= {"reproduction_steps", "version"}
    assert result.rationale


def test_duplicate_analyzer_returns_ranked_candidates() -> None:
    request = make_request("CLI crashes on init", "running init crashes with stack trace")
    candidate = Issue(
        number=2,
        title="CLI crashes when running init",
        body="init crashes with stack trace",
        url="",
        html_url="https://github.com/octo/demo/issues/2",
    )

    result = DuplicateAnalyzer().analyze(request, [candidate], TriagePodConfig())

    assert result[0].issue_number == 2
    assert result[0].confidence in {ConfidenceBand.MEDIUM, ConfidenceBand.HIGH}


def test_classifier_detects_support_before_bug_terms() -> None:
    request = make_request("Question: how do I fix auth error?", "Can someone help with API usage?")

    result = Classifier().classify(request, TriagePodConfig())

    assert result.classification == IssueClassification.SUPPORT


def test_label_engine_deduplicates_existing_labels() -> None:
    config = TriagePodConfig()
    request = make_request("Crash", "bug with reproduction steps", labels=("bug",))
    classification = Classifier().classify(request, config)
    missing = MissingInfoAnalyzer().analyze(request, config)

    result = LabelEngine().suggest(request, classification, missing, (), config)

    assert "bug" not in {suggestion.label for suggestion in result}


def test_discussion_router_requires_availability() -> None:
    request = make_request("How do I configure this?", "question about setup")
    router = DiscussionRouter()

    disabled = router.suggest(request, TriagePodConfig(), discussions_enabled=False)
    enabled = router.suggest(request, TriagePodConfig(), discussions_enabled=True)

    assert disabled.should_route is False
    assert enabled.should_route is True

from __future__ import annotations

from triagepod.application.analyzers import Classifier, LabelEngine, MissingInfoAnalyzer
from triagepod.application.config import TriagePodConfig
from triagepod.domain.models import Issue, Repository, TriageRequest, TriageResult
from triagepod.infrastructure.renderer import COMMENT_MARKER, ProfessionalCommentRenderer


def test_renderer_includes_marker_and_professional_sections() -> None:
    config = TriagePodConfig()
    request = TriageRequest(
        repository=Repository(owner="octo", name="demo", full_name="octo/demo"),
        issue=Issue(
            number=1,
            title="Bug: install fails",
            body="not working",
            url="",
            html_url="https://github.com/octo/demo/issues/1",
        ),
        event_name="issues",
        event_action="opened",
    )
    classification = Classifier().classify(request, config)
    missing = MissingInfoAnalyzer().analyze(request, config)
    labels = LabelEngine().suggest(request, classification, missing, (), config)

    body = ProfessionalCommentRenderer().render(
        TriageResult(
            classification=classification,
            missing_info=missing,
            label_suggestions=labels,
        )
    )

    assert COMMENT_MARKER in body
    assert "**Assessment**" in body
    assert "**Details requested**" in body
    assert "low quality" not in body.lower()

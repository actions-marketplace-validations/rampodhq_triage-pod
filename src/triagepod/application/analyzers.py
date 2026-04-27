from __future__ import annotations

import re
from collections.abc import Iterable

from rapidfuzz import fuzz

from triagepod.application.config import TriagePodConfig
from triagepod.domain.models import (
    ClassificationResult,
    ConfidenceBand,
    DuplicateCandidate,
    Issue,
    IssueClassification,
    LabelSuggestion,
    MissingField,
    MissingInfoResult,
    MissingInfoStatus,
    RoutingSuggestion,
    TriageRequest,
)

FIELD_PROMPTS = {
    "reproduction_steps": "Please add clear steps to reproduce the behavior.",
    "expected_behavior": "Please describe what you expected to happen.",
    "actual_behavior": "Please describe what actually happened.",
    "version": "Please include the affected package, app, or CLI version.",
    "environment": "Please include the relevant environment details.",
}

LOW_SIGNAL_PATTERNS = (
    re.compile(r"\b(not working|does not work|broken|help pls|help please)\b", re.IGNORECASE),
    re.compile(r"^\s*(bug|issue|problem|error)\s*$", re.IGNORECASE),
)


def normalize_text(value: str) -> str:
    lowered = value.lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", lowered)).strip()


def confidence_from_score(score: float) -> ConfidenceBand:
    if score >= 0.88:
        return ConfidenceBand.HIGH
    if score >= 0.72:
        return ConfidenceBand.MEDIUM
    return ConfidenceBand.LOW


class MissingInfoAnalyzer:
    def analyze(self, request: TriageRequest, config: TriagePodConfig) -> MissingInfoResult:
        if not config.features.missing_info_check:
            return MissingInfoResult(status=MissingInfoStatus.UNCERTAIN)

        text = normalize_text(f"{request.issue.title}\n{request.issue.body}")
        missing = []
        rationale: list[str] = []

        for field in config.required_fields:
            field_tokens = field.replace("_", " ")
            if field_tokens not in text:
                missing.append(
                    MissingField(key=field, prompt=FIELD_PROMPTS.get(field, f"Please add {field}."))
                )

        if len(request.issue.body.strip()) < 80:
            rationale.append("The issue body is short for maintainers to investigate effectively.")

        has_low_signal_text = any(
            pattern.search(request.issue.body) or pattern.search(request.issue.title)
            for pattern in LOW_SIGNAL_PATTERNS
        )
        if has_low_signal_text:
            rationale.append("The issue appears to contain low-signal placeholder wording.")

        status = (
            MissingInfoStatus.INCOMPLETE if missing or rationale else MissingInfoStatus.COMPLETE
        )
        return MissingInfoResult(
            status=status,
            missing_fields=tuple(missing),
            rationale=tuple(rationale),
        )


class DuplicateAnalyzer:
    def analyze(
        self, request: TriageRequest, candidates: Iterable[Issue], config: TriagePodConfig
    ) -> tuple[DuplicateCandidate, ...]:
        if not config.features.duplicate_detection:
            return ()

        source = normalize_text(f"{request.issue.title} {request.issue.body}")
        scored: list[DuplicateCandidate] = []

        for issue in candidates:
            candidate_text = normalize_text(f"{issue.title} {issue.body}")
            score = fuzz.token_set_ratio(source, candidate_text) / 100
            if score < config.duplicate_detection.similarity_threshold:
                continue
            scored.append(
                DuplicateCandidate(
                    issue_number=issue.number,
                    title=issue.title,
                    html_url=issue.html_url,
                    score=round(score, 3),
                    confidence=confidence_from_score(score),
                    rationale="Title and body are similar to this open issue.",
                )
            )

        return tuple(
            sorted(scored, key=lambda candidate: candidate.score, reverse=True)[
                : config.duplicate_detection.max_candidates
            ]
        )


class Classifier:
    BUG_TERMS = ("bug", "error", "exception", "crash", "fails", "failure", "regression", "broken")
    FEATURE_TERMS = ("feature", "enhancement", "proposal", "request", "add support")
    DOCS_TERMS = ("docs", "documentation", "readme", "guide", "typo")
    SUPPORT_TERMS = ("how do i", "question", "help", "can someone", "usage")

    def classify(self, request: TriageRequest, config: TriagePodConfig) -> ClassificationResult:
        text = normalize_text(f"{request.issue.title} {request.issue.body}")
        checks = (
            (
                IssueClassification.SUPPORT,
                self.SUPPORT_TERMS,
                "The issue is phrased as a usage question.",
            ),
            (
                IssueClassification.DOCS,
                self.DOCS_TERMS,
                "The issue refers to documentation or guides.",
            ),
            (
                IssueClassification.FEATURE,
                self.FEATURE_TERMS,
                "The issue asks for a new or changed capability.",
            ),
            (
                IssueClassification.BUG,
                self.BUG_TERMS,
                "The issue describes a failure or incorrect behavior.",
            ),
        )
        for classification, terms, rationale in checks:
            if any(term in text for term in terms):
                return ClassificationResult(classification, ConfidenceBand.MEDIUM, rationale)
        return ClassificationResult(
            IssueClassification.OTHER,
            ConfidenceBand.LOW,
            "No high-confidence rule matched the issue text.",
        )


class LabelEngine:
    def suggest(
        self,
        request: TriageRequest,
        classification: ClassificationResult,
        missing_info: MissingInfoResult,
        duplicates: tuple[DuplicateCandidate, ...],
        config: TriagePodConfig,
    ) -> tuple[LabelSuggestion, ...]:
        if not config.features.label_suggestions:
            return ()

        existing = set(request.issue.labels)
        labels = config.labels
        suggestions: list[LabelSuggestion] = []

        class_labels = getattr(labels, classification.classification.value)
        for label in class_labels:
            if label not in existing:
                suggestions.append(
                    LabelSuggestion(label, classification.rationale, classification.confidence)
                )

        if missing_info.status == MissingInfoStatus.INCOMPLETE:
            suggestions.extend(
                LabelSuggestion(
                    label,
                    "The issue is missing required intake details.",
                    ConfidenceBand.HIGH,
                )
                for label in labels.needs_info
                if label not in existing
            )

        if duplicates:
            suggestions.extend(
                LabelSuggestion(
                    label,
                    "The issue has likely duplicate candidates.",
                    ConfidenceBand.MEDIUM,
                )
                for label in labels.duplicate
                if label not in existing
            )

        deduped: dict[str, LabelSuggestion] = {}
        for suggestion in suggestions:
            deduped.setdefault(suggestion.label, suggestion)
        return tuple(deduped.values())


class DiscussionRouter:
    def suggest(
        self, request: TriageRequest, config: TriagePodConfig, discussions_enabled: bool
    ) -> RoutingSuggestion:
        routing = config.discussion_routing
        if not config.features.discussion_routing or not routing.enabled or not discussions_enabled:
            return RoutingSuggestion(False)

        text = normalize_text(f"{request.issue.title} {request.issue.body}")
        if any(pattern.lower() in text for pattern in routing.question_patterns):
            return RoutingSuggestion(
                True,
                "This looks like a usage or support question rather than a trackable issue.",
                routing.category,
            )
        return RoutingSuggestion(False)

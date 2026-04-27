from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class IssueClassification(StrEnum):
    BUG = "bug"
    FEATURE = "feature"
    DOCS = "docs"
    SUPPORT = "support"
    OTHER = "other"


class ConfidenceBand(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MissingInfoStatus(StrEnum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    UNCERTAIN = "uncertain"


@dataclass(frozen=True)
class Repository:
    owner: str
    name: str
    full_name: str
    default_branch: str = "main"
    has_discussions: bool = False


@dataclass(frozen=True)
class Issue:
    number: int
    title: str
    body: str
    url: str
    html_url: str
    labels: tuple[str, ...] = ()
    author: str | None = None
    state: str = "open"
    created_at: datetime | None = None


@dataclass(frozen=True)
class TriageRequest:
    repository: Repository
    issue: Issue
    event_name: str
    event_action: str
    event_id: str | None = None


@dataclass(frozen=True)
class DuplicateCandidate:
    issue_number: int
    title: str
    html_url: str
    score: float
    confidence: ConfidenceBand
    rationale: str


@dataclass(frozen=True)
class MissingField:
    key: str
    prompt: str


@dataclass(frozen=True)
class MissingInfoResult:
    status: MissingInfoStatus
    missing_fields: tuple[MissingField, ...] = ()
    rationale: tuple[str, ...] = ()


@dataclass(frozen=True)
class ClassificationResult:
    classification: IssueClassification
    confidence: ConfidenceBand
    rationale: str


@dataclass(frozen=True)
class LabelSuggestion:
    label: str
    reason: str
    confidence: ConfidenceBand


@dataclass(frozen=True)
class RoutingSuggestion:
    should_route: bool
    reason: str | None = None
    category: str | None = None


@dataclass(frozen=True)
class TriageActions:
    comment_posted: bool = False
    labels_applied: tuple[str, ...] = ()
    dry_run: bool = False


@dataclass(frozen=True)
class TriageResult:
    classification: ClassificationResult
    missing_info: MissingInfoResult
    duplicates: tuple[DuplicateCandidate, ...] = ()
    label_suggestions: tuple[LabelSuggestion, ...] = ()
    routing: RoutingSuggestion = field(default_factory=lambda: RoutingSuggestion(False))
    actions: TriageActions = field(default_factory=TriageActions)

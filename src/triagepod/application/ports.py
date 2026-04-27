from __future__ import annotations

from typing import Protocol

from triagepod.application.config import TriagePodConfig
from triagepod.domain.models import (
    ClassificationResult,
    DuplicateCandidate,
    Issue,
    Repository,
    TriageRequest,
    TriageResult,
)


class ConfigRepository(Protocol):
    def load(self, repository: Repository, path: str) -> TriagePodConfig: ...


class IssueRepository(Protocol):
    def list_open_issues(
        self, repository: Repository, exclude_number: int
    ) -> tuple[Issue, ...]: ...


class CommentRepository(Protocol):
    def upsert_triage_comment(self, request: TriageRequest, body: str) -> bool: ...


class LabelService(Protocol):
    def apply_labels(self, request: TriageRequest, labels: tuple[str, ...]) -> tuple[str, ...]: ...


class DiscussionCapabilityService(Protocol):
    def has_discussions_enabled(self, repository: Repository) -> bool: ...


class AiClassifier(Protocol):
    def refine_classification(
        self, request: TriageRequest, current: ClassificationResult
    ) -> ClassificationResult: ...


class AiDuplicateExplainer(Protocol):
    def explain_candidates(
        self, request: TriageRequest, candidates: tuple[DuplicateCandidate, ...]
    ) -> tuple[DuplicateCandidate, ...]: ...


class CommentRenderer(Protocol):
    def render(self, result: TriageResult) -> str: ...


class ResultLogger(Protocol):
    def info(self, event: str, **kwargs: object) -> None: ...
    def warning(self, event: str, **kwargs: object) -> None: ...
    def error(self, event: str, **kwargs: object) -> None: ...

from __future__ import annotations

from triagepod.domain.models import ClassificationResult, DuplicateCandidate, TriageRequest


class OpenAICompatibleAdapter:
    """Placeholder adapter for the V1 AI extension point.

    The rules-first behavior remains authoritative until a provider contract is enabled and tested.
    """

    def refine_classification(
        self, request: TriageRequest, current: ClassificationResult
    ) -> ClassificationResult:
        return current

    def explain_candidates(
        self, request: TriageRequest, candidates: tuple[DuplicateCandidate, ...]
    ) -> tuple[DuplicateCandidate, ...]:
        return candidates

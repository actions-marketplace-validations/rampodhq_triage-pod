from __future__ import annotations

from dataclasses import replace

from triagepod.application.analyzers import (
    Classifier,
    DiscussionRouter,
    DuplicateAnalyzer,
    LabelEngine,
    MissingInfoAnalyzer,
)
from triagepod.application.config import TriagePodConfig
from triagepod.application.ports import (
    AiClassifier,
    AiDuplicateExplainer,
    CommentRenderer,
    CommentRepository,
    DiscussionCapabilityService,
    IssueRepository,
    LabelService,
    ResultLogger,
)
from triagepod.domain.models import (
    ClassificationResult,
    DuplicateCandidate,
    TriageActions,
    TriageRequest,
    TriageResult,
)


class NoopAiClassifier:
    def refine_classification(
        self, request: TriageRequest, current: ClassificationResult
    ) -> ClassificationResult:
        return current


class NoopAiDuplicateExplainer:
    def explain_candidates(
        self, request: TriageRequest, candidates: tuple[DuplicateCandidate, ...]
    ) -> tuple[DuplicateCandidate, ...]:
        return candidates


class RunTriageUseCase:
    def __init__(
        self,
        issue_repository: IssueRepository,
        comment_repository: CommentRepository,
        label_service: LabelService,
        discussion_capability_service: DiscussionCapabilityService,
        comment_renderer: CommentRenderer,
        logger: ResultLogger,
        ai_classifier: AiClassifier | None = None,
        ai_duplicate_explainer: AiDuplicateExplainer | None = None,
    ) -> None:
        self.issue_repository = issue_repository
        self.comment_repository = comment_repository
        self.label_service = label_service
        self.discussion_capability_service = discussion_capability_service
        self.comment_renderer = comment_renderer
        self.logger = logger
        self.missing_info_analyzer = MissingInfoAnalyzer()
        self.duplicate_analyzer = DuplicateAnalyzer()
        self.classifier = Classifier()
        self.label_engine = LabelEngine()
        self.discussion_router = DiscussionRouter()
        self.ai_classifier = ai_classifier or NoopAiClassifier()
        self.ai_duplicate_explainer = ai_duplicate_explainer or NoopAiDuplicateExplainer()

    def run(self, request: TriageRequest, config: TriagePodConfig) -> TriageResult:
        self.logger.info(
            "triage_started",
            repository=request.repository.full_name,
            issue=request.issue.number,
            dry_run=config.automation.dry_run,
        )
        candidates = self.issue_repository.list_open_issues(
            request.repository,
            request.issue.number,
        )
        missing_info = self.missing_info_analyzer.analyze(request, config)
        duplicates = self.duplicate_analyzer.analyze(request, candidates, config)
        classification = self.classifier.classify(request, config)

        if config.features.ai and config.ai.provider:
            classification = self.ai_classifier.refine_classification(request, classification)
            duplicates = self.ai_duplicate_explainer.explain_candidates(request, duplicates)

        labels = self.label_engine.suggest(
            request,
            classification,
            missing_info,
            duplicates,
            config,
        )
        discussions_enabled = self.discussion_capability_service.has_discussions_enabled(
            request.repository
        )
        routing = self.discussion_router.suggest(request, config, discussions_enabled)

        result = TriageResult(
            classification=classification,
            missing_info=missing_info,
            duplicates=duplicates,
            label_suggestions=labels,
            routing=routing,
            actions=TriageActions(dry_run=config.automation.dry_run),
        )

        if config.automation.dry_run:
            self.logger.info("triage_dry_run_completed", issue=request.issue.number)
            return result

        comment_posted = False
        if config.automation.auto_comment:
            comment_posted = self.comment_repository.upsert_triage_comment(
                request, self.comment_renderer.render(result)
            )

        applied: tuple[str, ...] = ()
        if config.automation.auto_apply_labels:
            applied = self.label_service.apply_labels(
                request, tuple(suggestion.label for suggestion in labels)
            )

        completed = replace(
            result,
            actions=TriageActions(
                comment_posted=comment_posted,
                labels_applied=applied,
                dry_run=False,
            ),
        )
        self.logger.info(
            "triage_completed",
            issue=request.issue.number,
            comment_posted=comment_posted,
            labels_applied=applied,
        )
        return completed

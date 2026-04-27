from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class FeatureConfig(StrictModel):
    duplicate_detection: bool = True
    missing_info_check: bool = True
    label_suggestions: bool = True
    discussion_routing: bool = True
    ai: bool = False


class LabelConfig(StrictModel):
    bug: tuple[str, ...] = ("bug",)
    feature: tuple[str, ...] = ("enhancement",)
    docs: tuple[str, ...] = ("documentation",)
    support: tuple[str, ...] = ("support",)
    needs_info: tuple[str, ...] = ("needs-info",)
    duplicate: tuple[str, ...] = ("duplicate",)


class DuplicateDetectionConfig(StrictModel):
    max_candidates: int = Field(default=3, ge=1, le=10)
    similarity_threshold: float = Field(default=0.78, ge=0.0, le=1.0)
    search_open_issues: bool = True


class DiscussionRoutingConfig(StrictModel):
    enabled: bool = True
    question_patterns: tuple[str, ...] = ("how do i", "can someone help", "question")
    category: str = "Q&A"

    @field_validator("question_patterns")
    @classmethod
    def require_patterns(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value:
            msg = "discussion_routing.question_patterns must contain at least one pattern"
            raise ValueError(msg)
        return value


class CommentConfig(StrictModel):
    tone: Literal["professional", "friendly"] = "professional"
    include_confidence: bool = True
    include_explanations: bool = True


class AutomationConfig(StrictModel):
    auto_comment: bool = True
    auto_apply_labels: bool = False
    dry_run: bool = False


class IgnoreRulesConfig(StrictModel):
    labels: tuple[str, ...] = ()
    users: tuple[str, ...] = ()


class AiConfig(StrictModel):
    provider: str | None = None
    model: str | None = None
    timeout_seconds: float = Field(default=8.0, gt=0.0, le=30.0)


class TriagePodConfig(StrictModel):
    version: Literal[1] = 1
    features: FeatureConfig = Field(default_factory=FeatureConfig)
    required_fields: tuple[str, ...] = (
        "reproduction_steps",
        "expected_behavior",
        "actual_behavior",
        "version",
        "environment",
    )
    labels: LabelConfig = Field(default_factory=LabelConfig)
    duplicate_detection: DuplicateDetectionConfig = Field(default_factory=DuplicateDetectionConfig)
    discussion_routing: DiscussionRoutingConfig = Field(default_factory=DiscussionRoutingConfig)
    comments: CommentConfig = Field(default_factory=CommentConfig)
    automation: AutomationConfig = Field(default_factory=AutomationConfig)
    ignore_rules: IgnoreRulesConfig = Field(default_factory=IgnoreRulesConfig)
    ai: AiConfig = Field(default_factory=AiConfig)

    @field_validator("required_fields")
    @classmethod
    def require_unique_fields(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(field.strip().lower() for field in value if field.strip())
        if len(set(normalized)) != len(normalized):
            msg = "required_fields must not contain duplicates"
            raise ValueError(msg)
        return normalized

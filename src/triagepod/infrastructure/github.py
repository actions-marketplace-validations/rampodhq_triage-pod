from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from triagepod.domain.models import Issue, Repository, TriageRequest
from triagepod.infrastructure.renderer import COMMENT_MARKER


class GitHubApiError(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token: str, base_url: str = "https://api.github.com") -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=httpx.Timeout(10.0),
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "triagepod-action/0.1.0",
            },
        )

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError)),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        response = self.client.request(method, path, **kwargs)
        if response.status_code >= 400:
            msg = f"GitHub API {method} {path} failed with {response.status_code}: {response.text}"
            raise GitHubApiError(msg)
        return response

    def get_json(self, path: str) -> dict[str, Any]:
        payload = self.request("GET", path).json()
        if not isinstance(payload, dict):
            msg = f"GitHub API {path} returned an unexpected response"
            raise GitHubApiError(msg)
        return payload

    def get_list(self, path: str) -> list[dict[str, Any]]:
        payload = self.request("GET", path).json()
        if not isinstance(payload, list):
            msg = f"GitHub API {path} returned an unexpected list response"
            raise GitHubApiError(msg)
        return [item for item in payload if isinstance(item, dict)]


class GitHubIssueRepository:
    def __init__(self, client: GitHubClient) -> None:
        self.client = client

    def list_open_issues(self, repository: Repository, exclude_number: int) -> tuple[Issue, ...]:
        payload = self.client.get_list(
            f"/repos/{repository.full_name}/issues?state=open&per_page=100"
        )
        issues = []
        for item in payload:
            if item.get("pull_request") or item.get("number") == exclude_number:
                continue
            issues.append(issue_from_payload(item))
        return tuple(issues)


class GitHubCommentRepository:
    def __init__(self, client: GitHubClient) -> None:
        self.client = client

    def upsert_triage_comment(self, request: TriageRequest, body: str) -> bool:
        path = f"/repos/{request.repository.full_name}/issues/{request.issue.number}/comments"
        comments = self.client.get_list(f"{path}?per_page=100")
        existing_id = next(
            (
                comment.get("id")
                for comment in comments
                if isinstance(comment.get("body"), str) and COMMENT_MARKER in comment["body"]
            ),
            None,
        )
        if existing_id is not None:
            self.client.request(
                "PATCH",
                f"/repos/{request.repository.full_name}/issues/comments/{existing_id}",
                json={"body": body},
            )
            return True
        self.client.request("POST", path, json={"body": body})
        return True


class GitHubLabelService:
    def __init__(self, client: GitHubClient) -> None:
        self.client = client

    def apply_labels(self, request: TriageRequest, labels: tuple[str, ...]) -> tuple[str, ...]:
        if not labels:
            return ()
        path = f"/repos/{request.repository.full_name}/issues/{request.issue.number}/labels"
        self.client.request("POST", path, json={"labels": list(labels)})
        return labels


class GitHubDiscussionCapabilityService:
    def __init__(self, client: GitHubClient) -> None:
        self.client = client

    def has_discussions_enabled(self, repository: Repository) -> bool:
        payload = self.client.get_json(f"/repos/{repository.full_name}")
        return bool(payload.get("has_discussions"))


class OfflineIssueRepository:
    def list_open_issues(self, repository: Repository, exclude_number: int) -> tuple[Issue, ...]:
        return ()


class OfflineCommentRepository:
    def __init__(self) -> None:
        self.last_body: str | None = None

    def upsert_triage_comment(self, request: TriageRequest, body: str) -> bool:
        self.last_body = body
        return True


class OfflineLabelService:
    def apply_labels(self, request: TriageRequest, labels: tuple[str, ...]) -> tuple[str, ...]:
        return labels


class StaticDiscussionCapabilityService:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def has_discussions_enabled(self, repository: Repository) -> bool:
        return self.enabled


def repository_from_event(payload: Mapping[str, Any]) -> Repository:
    repo = require_mapping(payload, "repository")
    owner_payload = require_mapping(repo, "owner")
    full_name = require_str(repo, "full_name")
    owner = require_str(owner_payload, "login")
    return Repository(
        owner=owner,
        name=require_str(repo, "name"),
        full_name=full_name,
        default_branch=str(repo.get("default_branch") or "main"),
        has_discussions=bool(repo.get("has_discussions", False)),
    )


def issue_from_event(payload: Mapping[str, Any]) -> Issue:
    return issue_from_payload(require_mapping(payload, "issue"))


def issue_from_payload(payload: Mapping[str, Any]) -> Issue:
    labels = tuple(
        label["name"]
        for label in payload.get("labels", [])
        if isinstance(label, dict) and isinstance(label.get("name"), str)
    )
    user = payload.get("user")
    author = (
        user.get("login") if isinstance(user, dict) and isinstance(user.get("login"), str) else None
    )
    return Issue(
        number=int(payload.get("number", 0)),
        title=str(payload.get("title") or ""),
        body=str(payload.get("body") or ""),
        url=str(payload.get("url") or ""),
        html_url=str(payload.get("html_url") or ""),
        labels=labels,
        author=author,
        state=str(payload.get("state") or "open"),
        created_at=parse_datetime(payload.get("created_at")),
    )


def load_event(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as event_file:
        payload = json.load(event_file)
    if not isinstance(payload, dict):
        msg = "GitHub event payload must be a JSON object"
        raise ValueError(msg)
    return payload


def require_mapping(payload: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        msg = f"GitHub event payload is missing object field '{key}'"
        raise ValueError(msg)
    return value


def require_str(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        msg = f"GitHub event payload is missing string field '{key}'"
        raise ValueError(msg)
    return value


def parse_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

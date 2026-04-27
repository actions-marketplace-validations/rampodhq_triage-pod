from __future__ import annotations

import base64
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import ValidationError
from ruamel.yaml import YAML

from triagepod.application.config import TriagePodConfig
from triagepod.domain.models import Repository

if TYPE_CHECKING:
    from triagepod.infrastructure.github import GitHubClient


class ConfigLoadError(RuntimeError):
    pass


class LocalConfigRepository:
    def load(self, repository: Repository, path: str) -> TriagePodConfig:
        config_path = Path(path)
        if not config_path.exists():
            return TriagePodConfig()
        return parse_config(config_path.read_text(encoding="utf-8"))


class GitHubConfigRepository:
    def __init__(self, client: GitHubClient) -> None:
        self.client = client

    def load(self, repository: Repository, path: str) -> TriagePodConfig:
        payload = self.client.get_json(f"/repos/{repository.full_name}/contents/{path}")
        encoded = payload.get("content")
        if not isinstance(encoded, str):
            msg = f"Config file {path} did not contain base64 content"
            raise ConfigLoadError(msg)
        return parse_config(base64.b64decode(encoded).decode("utf-8"))


def parse_config(content: str) -> TriagePodConfig:
    yaml = YAML(typ="safe")
    try:
        loaded = yaml.load(content) or {}
    except Exception as exc:  # pragma: no cover - ruamel exception types are broad
        msg = f"Unable to parse triagepod config: {exc}"
        raise ConfigLoadError(msg) from exc

    if not isinstance(loaded, dict):
        msg = "TriagePod config must be a YAML mapping"
        raise ConfigLoadError(msg)

    try:
        return TriagePodConfig.model_validate(cast_mapping(loaded))
    except ValidationError as exc:
        msg = f"Invalid TriagePod config: {exc}"
        raise ConfigLoadError(msg) from exc


def cast_mapping(value: dict[Any, Any]) -> dict[str, Any]:
    return {str(key): item for key, item in value.items()}

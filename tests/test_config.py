from __future__ import annotations

import pytest

from triagepod.infrastructure.config_repository import ConfigLoadError, parse_config


def test_parse_config_applies_defaults() -> None:
    config = parse_config("version: 1\n")

    assert config.automation.auto_comment is True
    assert config.automation.auto_apply_labels is False
    assert config.features.duplicate_detection is True


def test_parse_config_rejects_unknown_keys() -> None:
    with pytest.raises(ConfigLoadError, match="extra_forbidden"):
        parse_config("version: 1\nunknown: true\n")


def test_parse_config_rejects_duplicate_required_fields() -> None:
    with pytest.raises(ConfigLoadError, match="required_fields must not contain duplicates"):
        parse_config("version: 1\nrequired_fields:\n  - version\n  - version\n")

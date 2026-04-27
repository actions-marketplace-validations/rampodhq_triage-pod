# TriagePod

TriagePod is a GitHub-native issue triage assistant. Version 1 ships as a Docker-based GitHub Action that analyzes newly opened issues and produces professional, configurable intake guidance.

## V1 capabilities

- Duplicate suggestions from open issues.
- Missing-information checks from repo-local YAML config.
- Rules-first classification for bug, feature, docs, support, and other.
- Label suggestions, with optional auto-labeling.
- Discussions routing suggestions when enabled and available.
- Dry-run mode for safe rollout.
- Optional AI extension points, disabled by default.

## GitHub Action usage

```yaml
name: TriagePod

on:
  issues:
    types: [opened]

permissions:
  contents: read
  issues: write

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          config_path: .github/triagepod.yml
```

## Local development

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run bandit -r src
uv run pip-audit
uv run triagepod-action
```

For deterministic local smoke tests, set `TRIAGEPOD_OFFLINE=true`, `GITHUB_EVENT_PATH` to a fixture, and `INPUT_CONFIG_PATH` to an example config.

## Configuration

Create `.github/triagepod.yml` in the target repository. See `examples/` for starting points.

```yaml
version: 1

features:
  duplicate_detection: true
  missing_info_check: true
  label_suggestions: true
  discussion_routing: true

required_fields:
  - reproduction_steps
  - expected_behavior
  - actual_behavior
  - version
  - environment

automation:
  auto_comment: true
  auto_apply_labels: false
  dry_run: false
```

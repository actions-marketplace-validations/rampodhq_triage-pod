FROM ghcr.io/astral-sh/uv:0.9.16-python3.12-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN uv sync --frozen --no-dev

ENTRYPOINT ["uv", "run", "--no-dev", "triagepod-action"]

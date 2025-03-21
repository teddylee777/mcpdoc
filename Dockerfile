# Multi-stage build using UV package manager
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS uv

# Set up working directory
WORKDIR /app

# Enable bytecode compilation for performance
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install dependencies using lockfile (without installing the project yet)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Add the rest of the source code and install the project
# 의존성과 프로젝트를 분리하여 설치하면 레이어 캐싱이 최적화됩니다
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Final stage with minimal image
FROM python:3.12-slim-bookworm

# Install git for source control operations
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed dependencies and virtual environment
COPY --from=uv /root/.local /root/.local
COPY --from=uv --chown=app:app /app/.venv /app/.venv

# Add virtual environment binaries to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy all application files
COPY . /app

# Default command to run the application
# 실행 명령은 필요에 따라 수정하세요
ENTRYPOINT ["python", "-m", "mcpdoc"]
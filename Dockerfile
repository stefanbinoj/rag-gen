FROM python:3.12-slim

WORKDIR /app

# Install curl, bash, ca-certificates and any system deps you need
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates bash gcc build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install uv (astral)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:/root/.cargo/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_HTTP_TIMEOUT=300

# Copy lock files so uv can resolve
COPY pyproject.toml .python-version uv.lock ./

# Install python declared by .python-version and sync deps
RUN uv python install
RUN uv sync --frozen --no-install-project --no-dev

# Copy application code
COPY . .

# Ensure run.sh executable
RUN chmod +x ./run.sh

EXPOSE 8000

CMD ["./run.sh"]

# ==== simple single-stage (uv) ====
FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /code
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
# чтобы бинарники из .venv были в PATH (на всякий случай)

# 1) ставим зависимости
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 2) копируем код
COPY app ./app

# 3) старт
CMD ["uv", "run", "uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000"]

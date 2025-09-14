# ===== build stage (uv) =====
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS build
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project
# скопируем приложение
COPY app ./app
COPY main.py ./main.py
# соберём в венв (wheelhouse внутри uv-кэша, но для простоты — layer с проектом)
RUN uv pip install -e . --system

# ===== run stage =====
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY --from=build /usr/local /usr/local
COPY app ./app
COPY main.py ./main.py
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

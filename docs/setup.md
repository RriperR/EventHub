# Установка и запуск

## Требования
- Python 3.10+
- Docker + Docker Compose
- uv (рекомендуется для управления зависимостями)

## Шаги

```bash
# Установить зависимости
uv sync

# Запустить ClickHouse
docker compose up -d clickhouse

# Запуск API
uv run uvicorn app.main:app --reload
```

## Переменные окружения
- `CH_HOST` — хост ClickHouse (по умолчанию `localhost`).
- `CH_PORT` — порт (по умолчанию `8123`).
- `CH_DATABASE` — имя БД (`eventhub`).
- `CH_USER` / `CH_PASSWORD` — учётные данные (если нужны).

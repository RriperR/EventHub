# EventHub

EventHub — проект микросервиса на **FastAPI** с GraphQL и ClickHouse.

## 🚀 Возможности
- GraphQL API для записи и чтения событий.
- Хранение событий в ClickHouse.
- Поддержка метрик Prometheus.
- Логирование с request_id.
- Настройка через .env.

## 📦 Установка и запуск

```bash
# Клонировать проект
git clone https://github.com/yourname/eventhub.git
cd eventhub

# Установить зависимости
uv sync

# Запустить инфраструктуру
docker compose up -d clickhouse

# Запуск API
uv run uvicorn app.main:app --reload
```

## 🔗 Документация
- [Архитектура](docs/architecture.md)
- [Установка](docs/setup.md)
- [GraphQL API](docs/graphql.md)
- [Разработка](docs/dev.md)

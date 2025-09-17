# Руководство разработчика

## Структура проекта
- `app/core` — конфиг, логирование, метрики, middleware.
- `app/api` — REST-роуты (например, healthcheck).
- `app/graphql` — схема GraphQL (Query, Mutation).
- `app/storage/clickhouse` — работа с ClickHouse.

## Кодстайл
- PEP8
- Модерн-типизация (Python 3.10+, `str | None` вместо `Optional[str]`)
- Логирование в JSON-формате

## Запуск тестов (планируется)
```bash
pytest
```

# Архитектура EventHub

EventHub построен как микросервис для приёма и анализа событий.

## Компоненты
- **FastAPI** — основной сервер, REST + GraphQL слой.
- **Strawberry GraphQL** — схема и резолверы.
- **ClickHouse** — хранилище событий (events_enriched).
- **Prometheus/Grafana** — метрики и мониторинг.
- **Sentry** (планируется) — сбор ошибок.

## Поток данных
1. Клиент отправляет GraphQL mutation `createEvent`.
2. FastAPI → Strawberry валидирует входные данные.
3. `client.py` сохраняет событие в ClickHouse.
4. Для чтения выполняется GraphQL query `events`.

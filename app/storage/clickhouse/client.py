from typing import Any

import clickhouse_connect
from clickhouse_connect.driver.client import Client

from app.core.config import settings

_client: Client | None = None


def _build_client(database: str | None = None) -> Client:
    return clickhouse_connect.get_client(
        host=settings.ch_host,
        port=settings.ch_port,
        secure=settings.ch_secure,              # https если True
        username=settings.ch_user,
        password=settings.ch_password,
        database=(database or settings.ch_database),
        connect_timeout=settings.ch_connect_timeout,
        send_receive_timeout=settings.ch_send_receive_timeout,
    )


def get_client() -> Client:
    global _client
    if _client is None:
        _client = _build_client()
    return _client


DDL_EVENTS = """
CREATE TABLE IF NOT EXISTS events_enriched
(
  id UUID,
  ts DateTime,
  event_type LowCardinality(String),
  tenant_id UUID,
  actor_id Nullable(UUID),
  patient_id Nullable(UUID),
  props JSON,
  _ingested_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (tenant_id, event_type, ts, actor_id, id);
""".strip()


def init_db() -> None:
    # создаём БД на системном подключении
    admin = _build_client(database="default")
    admin.command(f"CREATE DATABASE IF NOT EXISTS {settings.ch_database}")
    admin.close()

    cl = get_client()
    cl.command(DDL_EVENTS)


def close_client() -> None:
    global _client
    if _client is not None:
        try:
            _client.close()
        finally:
            _client = None


def _null_if_empty(value: str | None) -> str | None:
    """Пустые строки → None, чтобы писать в Nullable(UUID)."""
    if value is None:
        return None
    v = value.strip()
    return v if v else None


def insert_event(
    *,
    id: str,
    ts,  # datetime.datetime или строка
    event_type: str,
    tenant_id: str,
    actor_id: str | None,
    patient_id: str | None,
    props: dict[str, Any] | None,
) -> None:
    """
    Пишем в таблицу с типами UUID.
    ClickHouse сам приведёт строку-UUID к типу UUID.
    Для nullable колонок пустые строки превращаем в NULL.
    """
    cl = get_client()
    cl.insert(
        "events_enriched",
        [[
            id,                        # UUID
            ts,                        # DateTime
            event_type,                # LowCardinality(String)
            tenant_id,                 # UUID
            _null_if_empty(actor_id),  # Nullable(UUID)
            _null_if_empty(patient_id),# Nullable(UUID)
            props or {},               # JSON
        ]],
        column_names=[
            "id", "ts", "event_type", "tenant_id",
            "actor_id", "patient_id", "props",
        ],
    )


def select_events(
    *,
    tenant_id: str | None = None,
    patient_id: str | None = None,
    limit: int = 50,
    deduplicate: bool = True,  # по умолчанию «склеиваем» дубли по id
) -> list[dict[str, Any]]:
    """
    Читаем последние события. Если deduplicate=True — используем FINAL,
    чтобы ReplacingMergeTree отдал по одной записи на id.
    """
    cl = get_client()
    where = []
    parameters: dict[str, Any] = {"lim": limit}

    if tenant_id:
        where.append("tenant_id = {tenant:UUID}")
        parameters["tenant"] = tenant_id
    if patient_id:
        where.append("patient_id = {pid:UUID}")
        parameters["pid"] = patient_id

    where_sql = f" WHERE {' AND '.join(where)}" if where else ""
    final_hint = " FINAL" if deduplicate else ""

    sql = f"""
        SELECT id, ts, event_type, tenant_id, actor_id, patient_id, props
        FROM events_enriched{final_hint}
        {where_sql}
        ORDER BY ts DESC
        LIMIT {{lim:UInt32}}
    """

    rows = cl.query(sql, parameters=parameters).named_results()
    return [dict(r) for r in rows]

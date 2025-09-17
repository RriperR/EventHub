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
  id String,
  ts DateTime,
  event_type LowCardinality(String),
  tenant_id String,
  actor_id String,
  patient_id String,
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
    cl = get_client()
    cl.insert(
        "events_enriched",
        [[id, ts, event_type, tenant_id, actor_id or "", patient_id or "", props or {}]],
        column_names=["id", "ts", "event_type", "tenant_id", "actor_id", "patient_id", "props"],
    )


def select_events(
    *, tenant_id: str | None = None, patient_id: str | None = None, limit: int = 50
) -> list[dict[str, Any]]:
    cl = get_client()
    where = []
    parameters: dict[str, Any] = {"lim": limit}

    if tenant_id:
        where.append("tenant_id = {tenant:String}")
        parameters["tenant"] = tenant_id
    if patient_id:
        where.append("patient_id = {pid:String}")
        parameters["pid"] = patient_id

    where_sql = f" WHERE {' AND '.join(where)}" if where else ""
    sql = f"""
        SELECT id, ts, event_type, tenant_id, actor_id, patient_id, props
        FROM events_enriched
        {where_sql}
        ORDER BY ts DESC
        LIMIT {{lim:UInt32}}
    """

    rows = cl.query(sql, parameters=parameters).named_results()
    return [dict(r) for r in rows]


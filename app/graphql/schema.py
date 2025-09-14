import datetime as dt
import strawberry


@strawberry.type
class Event:
    id: str
    ts: dt.datetime
    type: str
    tenant_id: str
    actor_id: str | None
    patient_id: str | None

# Временный in-memory источник (потом заменим на Mongo/ClickHouse)
_FAKE_EVENTS = [
    Event(id="1", ts=dt.datetime.utcnow(), type="patient.created", tenant_id="t1", actor_id="u1", patient_id="p1"),
    Event(id="2", ts=dt.datetime.utcnow(), type="record.added", tenant_id="t1", actor_id="u1", patient_id="p1"),
]

@strawberry.type
class Query:
    @strawberry.field
    def ping(self) -> str:
        return "pong"

    @strawberry.field
    def events(self) -> list[Event]:
        return _FAKE_EVENTS

schema = strawberry.Schema(Query)

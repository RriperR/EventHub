import datetime as dt

import strawberry
from strawberry.scalars import JSON

from app.storage.clickhouse.client import insert_event, select_events


@strawberry.type
class Event:
    id: str
    ts: dt.datetime
    type: str
    tenant_id: str
    actor_id: str | None
    patient_id: str | None
    props: JSON | None


@strawberry.input
class CreateEventInput:
    id: str
    ts: dt.datetime
    type: str
    tenant_id: str
    actor_id: str | None = None
    patient_id: str | None = None
    props: JSON | None = None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_event(self, data: CreateEventInput) -> bool:
        # clickhouse-connect умеет datetime → DateTime
        insert_event(
            id=data.id,
            ts=data.ts,
            event_type=data.type,
            tenant_id=data.tenant_id,
            actor_id=data.actor_id,
            patient_id=data.patient_id,
            props=data.props,  # JSON scalar → dict
        )
        return True


@strawberry.type
class Query:
    @strawberry.field
    def events(
        self,
        tenant_id: str | None = None,
        patient_id: str | None = None,
        limit: int = 50,
    ) -> list[Event]:
        rows = select_events(
            tenant_id=tenant_id,
            patient_id=patient_id,
            limit=limit,
        )
        out: list[Event] = []
        for r in rows:
            out.append(
                Event(
                    id=r["id"],
                    ts=r["ts"],  # драйвер отдаёт datetime
                    type=r["event_type"],
                    tenant_id=r["tenant_id"],
                    actor_id=r["actor_id"] or None,
                    patient_id=r["patient_id"] or None,
                    props=r.get("props") or None,
                )
            )
        return out


schema = strawberry.Schema(query=Query, mutation=Mutation)

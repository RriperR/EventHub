import logging
from datetime import datetime, timezone

import grpc
from google.protobuf.json_format import MessageToDict
from google.protobuf.struct_pb2 import Struct
from google.protobuf.timestamp_pb2 import Timestamp

from app.storage.clickhouse.client import insert_event
from app.docere.eventhub.v1 import events_pb2_grpc, events_pb2


def _pb_ts_to_dt(ts: Timestamp) -> datetime:
    # gRPC Timestamp -> Python datetime (UTC)
    return datetime.fromtimestamp(ts.seconds + ts.nanos / 1e9, tz=timezone.utc)


def _struct_to_dict(s: Struct | None) -> dict:
    if not s:
        return {}
    # быстрый и безопасный способ
    return MessageToDict(s, preserving_proto_field_name=True)


class EventIngestServicer(events_pb2_grpc.EventIngestServicer):
    async def PublishEvent(
        self, request: events_pb2.PublishEventRequest, context: grpc.aio.ServicerContext
    ) -> events_pb2.PublishEventResponse:
        e = request.event
        try:
            insert_event(
                id=e.id,
                ts=_pb_ts_to_dt(e.ts),
                event_type=e.type,
                tenant_id=e.tenant_id,
                actor_id=e.actor_id or None,
                patient_id=e.patient_id or None,
                props=_struct_to_dict(e.props),
            )
            return events_pb2.PublishEventResponse(ok=True, message="ok")
        except Exception as exc:  # noqa: BLE001
            logging.getLogger("grpc").exception("PublishEvent failed")
            await context.abort(grpc.StatusCode.INTERNAL, f"insert failed: {exc}")

    async def PublishEvents(
        self, request_iterator, context: grpc.aio.ServicerContext
    ) -> events_pb2.PublishEventsResponse:
        accepted = 0
        failed = 0
        async for e in request_iterator:
            try:
                insert_event(
                    id=e.id,
                    ts=_pb_ts_to_dt(e.ts),
                    event_type=e.type,
                    tenant_id=e.tenant_id,
                    actor_id=e.actor_id or None,
                    patient_id=e.patient_id or None,
                    props=_struct_to_dict(e.props),
                )
                accepted += 1
            except Exception:
                logging.getLogger("grpc").exception("PublishEvents item failed")
                failed += 1
        return events_pb2.PublishEventsResponse(accepted=accepted, failed=failed)


async def serve_grpc(bind: str = "[::]:50051") -> None:
    server = grpc.aio.server()
    events_pb2_grpc.add_EventIngestServicer_to_server(EventIngestServicer(), server)
    server.add_insecure_port(bind)  # в проде: mTLS
    await server.start()
    logging.getLogger("grpc").info("gRPC server started on %s", bind)
    await server.wait_for_termination()

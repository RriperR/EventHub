import asyncio
import grpc

from datetime import datetime, timezone

from google.protobuf.struct_pb2 import Struct
from google.protobuf.timestamp_pb2 import Timestamp

from docere.eventhub.v1 import events_pb2, events_pb2_grpc


async def main():
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = events_pb2_grpc.EventIngestStub(channel)

        ts = Timestamp()
        ts.FromDatetime(datetime.now(tz=timezone.utc))

        props = Struct()
        props.update({"source": "local-test", "ip": "127.0.0.1"})

        req = events_pb2.PublishEventRequest(
            event=events_pb2.Event(
                id="e-grpc-1",
                tenant_id="t1",
                type="patient.created",
                actor_id="u1",
                patient_id="p1",
                ts=ts,
                props=props,
            )
        )
        resp = await stub.PublishEvent(req)
        print(resp)

if __name__ == "__main__":
    asyncio.run(main())

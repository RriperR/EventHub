import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from strawberry.fastapi import GraphQLRouter

from app.core.config import settings
from app.core.logger import setup_logging
from app.core.request_id import RequestIdMiddleware, RequestIdFilter
from app.core.metrics import MetricsMiddleware, prometheus_asgi_app
from app.api import api_router
from app.graphql.schema import schema
from app.storage.clickhouse.client import init_db, close_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    close_client()
    logging.getLogger("app").info("Application shutdown")



def create_app() -> FastAPI:
    setup_logging(settings.log_level)
    # добавим фильтр, чтобы в JSON логах всегда было поле request_id
    logging.getLogger().addFilter(RequestIdFilter())

    app = FastAPI(
        title=settings.app_name,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    # middlewares
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(MetricsMiddleware)

    # routers
    gql_router = GraphQLRouter(schema)
    app.include_router(api_router)
    app.include_router(gql_router, prefix="/graphql")

    # /metrics — отдельным ASGI приложением (без FastAPI роутера, чтобы не мешать метрике путей)
    if settings.prometheus_enabled:
        app.mount("/metrics", prometheus_asgi_app())

    # простой лог каждого запроса (пример)
    @app.middleware("http")
    async def add_request_id_to_log(request: Request, call_next):
        logger = logging.getLogger("app.request")
        logger.info("request_start", extra={"request_id": getattr(request.state, "request_id", "")})
        response = await call_next(request)
        logger.info("request_end", extra={"request_id": getattr(request.state, "request_id", "")})
        return response

    return app

app = create_app()

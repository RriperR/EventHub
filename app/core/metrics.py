import time
from prometheus_client import Counter, Histogram, CollectorRegistry, CONTENT_TYPE_LATEST, generate_latest


registry = CollectorRegistry()
http_requests_total = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "path", "status"], registry=registry
)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds", "HTTP request latency seconds", ["method", "path"], registry=registry
)

def prometheus_asgi_app():
    # простейший ASGI эндпоинт для /metrics
    async def app(scope, receive, send):
        if scope["type"] != "http":
            return
        data = generate_latest(registry)
        headers = [(b"content-type", CONTENT_TYPE_LATEST.encode())]
        await send({"type": "http.response.start", "status": 200, "headers": headers})
        await send({"type": "http.response.body", "body": data})
    return app


# middleware для метрик
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path_tmpl = request.scope.get("route").path if request.scope.get("route") else request.url.path
        method = request.method
        start = time.perf_counter()
        response = await call_next(request)
        dur = time.perf_counter() - start
        http_requests_total.labels(method=method, path=path_tmpl, status=str(response.status_code)).inc()
        http_request_duration_seconds.labels(method=method, path=path_tmpl).observe(dur)
        return response

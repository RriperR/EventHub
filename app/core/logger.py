import logging
from pythonjsonlogger import jsonlogger


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s"
    handler.setFormatter(jsonlogger.JsonFormatter(fmt))
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

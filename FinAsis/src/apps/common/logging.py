import json
import logging
import datetime
import uuid
from typing import Any, Dict
from threading import local

_request_local = local()


def set_request_context(request_id: str | None = None, tenant: Any = None, user: Any = None, path: str | None = None):
    _request_local.context = {
        "request_id": request_id,
        "tenant": getattr(tenant, 'code', None) if tenant else None,
        "user": getattr(user, 'id', None) if user and getattr(user, 'is_authenticated', False) else None,
        "path": path,
    }


def get_request_context() -> Dict[str, Any]:
    return getattr(_request_local, 'context', {})


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        base = {
            "level": record.levelname,
            "ts": datetime.datetime.utcnow().isoformat(timespec='milliseconds') + 'Z',
            "logger": record.name,
            "message": record.getMessage(),
        }
        ctx = get_request_context()
        if ctx:
            base.update({k: v for k, v in ctx.items() if v is not None})
        if record.exc_info:
            base['exception'] = self.formatException(record.exc_info)
        return json.dumps(base, ensure_ascii=False)


def generate_request_id() -> str:
    return uuid.uuid4().hex

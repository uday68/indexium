import uuid
import contextvars
from typing import Optional

_trace_id_ctx = contextvars.ContextVar("trace_id", default="")


def generate_trace_id() -> str:
    """Generate a unique trace/request ID."""
    return str(uuid.uuid4())


def set_current_trace_id(trace_id: str):
    _trace_id_ctx.set(trace_id)


def get_current_trace_id() -> str:
    tid = _trace_id_ctx.get()
    if not tid:
        tid = generate_trace_id()
        _trace_id_ctx.set(tid)
    return tid

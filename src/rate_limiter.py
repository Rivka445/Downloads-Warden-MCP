"""Rate limiting decorator for MCP tools."""

from datetime import datetime, timedelta
from functools import wraps
from typing import Callable

from exceptions import DownloadsWardenError

_last_calls: dict[str, datetime] = {}
_RATE_LIMIT_SECONDS = 5


def rate_limited(func: Callable) -> Callable:
    """Prevent a tool from being called more than once every _RATE_LIMIT_SECONDS seconds."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        tool_name = func.__name__
        last = _last_calls.get(tool_name)
        if last and datetime.now() - last < timedelta(seconds=_RATE_LIMIT_SECONDS):
            remaining = _RATE_LIMIT_SECONDS - (datetime.now() - last).seconds
            raise DownloadsWardenError(
                f"Tool '{tool_name}' was called too recently. Wait {remaining}s before retrying."
            )
        _last_calls[tool_name] = datetime.now()
        return await func(*args, **kwargs)
    return wrapper


def clear_rate_limit_cache() -> None:
    """Clear all rate limit timestamps. Used in tests."""
    _last_calls.clear()

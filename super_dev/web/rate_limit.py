"""In-memory sliding-window rate limiting ASGI middleware for the Super Dev Web API."""

import collections
import json
import os
import time
from collections.abc import Callable, Coroutine
from typing import Any


class RateLimitMiddleware:
    """ASGI middleware that enforces per-IP request rate limits using a sliding window.

    Configuration via environment variables:
        SUPER_DEV_RATE_LIMIT  – max requests per window (default: 100)
        SUPER_DEV_RATE_WINDOW – window size in seconds (default: 60)
    """

    def __init__(self, app: Any) -> None:
        self.app = app
        raw_limit = os.getenv("SUPER_DEV_RATE_LIMIT", "100")
        raw_window = os.getenv("SUPER_DEV_RATE_WINDOW", "60")
        self.max_requests: int = max(int(raw_limit), 0) if raw_limit.lstrip("-").isdigit() else 100
        self.window: int = max(int(raw_window), 1) if raw_window.lstrip("-").isdigit() else 60
        # Map[client_ip, deque[timestamp]]
        self._hits: dict[str, collections.deque[float]] = collections.defaultdict(
            lambda: collections.deque()
        )

    def _client_ip(self, scope: dict[str, Any]) -> str:
        """Extract client IP from X-Forwarded-For header or remote_addr."""
        for name, value in scope.get("headers", []):
            if name == b"x-forwarded-for":
                return str(value.decode("utf-8", errors="replace").split(",")[0].strip())
        client = scope.get("client")
        if isinstance(client, list | tuple) and len(client) > 0:
            return str(client[0])
        return "unknown"

    def _cleanup(self, ip: str, now: float) -> None:
        """Remove timestamps older than 2× window and prune empty entries."""
        cutoff = now - 2 * self.window
        dq = self._hits.get(ip)
        if dq is None:
            return
        while dq and dq[0] < cutoff:
            dq.popleft()
        if not dq:
            del self._hits[ip]

    async def __call__(
        self, scope: dict[str, Any], receive: Callable[[], Coroutine], send: Callable
    ) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        ip = self._client_ip(scope)
        now = time.monotonic()
        self._cleanup(ip, now)

        dq = self._hits[ip]
        # Drop timestamps outside the current window
        cutoff = now - self.window
        while dq and dq[0] < cutoff:
            dq.popleft()

        if self.max_requests > 0 and len(dq) >= self.max_requests:
            oldest = dq[0]
            retry_after = int(oldest + self.window - now) + 1
            retry_after = max(retry_after, 1)
            body = json.dumps(
                {"detail": "Rate limit exceeded", "retry_after": retry_after}
            ).encode()
            await send(
                {
                    "type": "http.response.start",
                    "status": 429,
                    "headers": [
                        [b"content-type", b"application/json"],
                        [b"retry-after", str(retry_after).encode()],
                    ],
                }
            )
            await send({"type": "http.response.body", "body": body})
            return

        dq.append(now)
        await self.app(scope, receive, send)

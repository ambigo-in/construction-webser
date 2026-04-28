"""
Very small in-memory rate limiter.

Notes:
- Per-process only (won't scale across multiple workers/instances).
- Good enough for MVP and local development; swap to Redis for production.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import time
from typing import Dict, List, Tuple

from fastapi import HTTPException, status


@dataclass
class RateLimitResult:
    allowed: bool
    retry_after_seconds: int


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._hits: Dict[str, List[float]] = {}

    def hit(self, key: str, *, limit: int, window_seconds: int) -> RateLimitResult:
        now = time.time()
        window_start = now - window_seconds
        arr = self._hits.get(key, [])
        # prune
        arr = [t for t in arr if t >= window_start]
        if len(arr) >= limit:
            oldest = min(arr) if arr else now
            retry_after = max(1, int((oldest + window_seconds) - now))
            self._hits[key] = arr
            return RateLimitResult(allowed=False, retry_after_seconds=retry_after)
        arr.append(now)
        self._hits[key] = arr
        return RateLimitResult(allowed=True, retry_after_seconds=0)


limiter = InMemoryRateLimiter()


def enforce_rate_limit(key: str, *, limit: int, window_seconds: int) -> None:
    res = limiter.hit(key, limit=limit, window_seconds=window_seconds)
    if res.allowed:
        return
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Rate limit exceeded",
        headers={"Retry-After": str(res.retry_after_seconds)},
    )


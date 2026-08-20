import time
from collections import defaultdict, deque

from fastapi import HTTPException


class RateLimiter:

    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: int = 60
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)

    def check(self, client_id: str) -> None:

        now = time.time()

        request_times = self.requests[client_id]

        while (
            request_times
            and now - request_times[0] >= self.window_seconds
        ):
            request_times.popleft()

        if len(request_times) >= self.max_requests:

            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )

        request_times.append(now)
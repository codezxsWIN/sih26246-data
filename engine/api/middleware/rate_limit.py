import time
from collections import defaultdict
from fastapi import Request, HTTPException

class RateLimiter:
    """Sliding-window IP rate limiter. No external dependencies."""
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max = max_requests
        self.window = window_seconds
        self.hits: dict[str, list[float]] = defaultdict(list)

    def check(self, request: Request) -> None:
        ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        # Prune expired timestamps
        self.hits[ip] = [t for t in self.hits[ip] if now - t < self.window]
        if len(self.hits[ip]) >= self.max:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.max} requests per {self.window}s allowed."
            )
        self.hits[ip].append(now)

chatbot_limiter = RateLimiter(max_requests=10, window_seconds=60)

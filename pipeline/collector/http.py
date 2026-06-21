from __future__ import annotations

import time
from typing import Any

import httpx

_RETRYABLE_STATUSES = {500, 502, 503, 504}


def _should_retry(status_code: int, attempts_left: int) -> bool:
    return status_code in _RETRYABLE_STATUSES and attempts_left > 0


class ResilientClient:
    def __init__(
        self,
        transport: httpx.BaseTransport | None = None,
        timeout: float = 20.0,
        max_retries: int = 2,
        backoff: float = 0.5,
    ) -> None:
        self._timeout = timeout
        self._max_retries = max_retries
        self._backoff = backoff
        self._client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            transport=transport,
        )

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        attempts = self._max_retries + 1
        last_exc: Exception | None = None
        for attempt in range(attempts):
            try:
                response = self._client.request(method, url, **kwargs)
            except Exception as exc:
                last_exc = exc
                if attempt == attempts - 1:
                    raise
                time.sleep(self._backoff * (attempt + 1))
                continue

            if response.status_code in {401, 403, 429}:
                return response

            if _should_retry(response.status_code, attempts - attempt - 1):
                time.sleep(self._backoff * (attempt + 1))
                continue

            return response

        if last_exc is not None:
            raise last_exc
        return httpx.Response(status_code=500, text="retry loop exhausted")

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("POST", url, **kwargs)

    def close(self) -> None:
        self._client.close()

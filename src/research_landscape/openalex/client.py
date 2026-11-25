"""Bounded, sequential OpenAlex requests. Never log credential-bearing URLs."""

import json
from time import monotonic, sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


class OpenAlexClient:
    def __init__(self, api_key, *, timeout_seconds, max_attempts, min_interval_seconds):
        self.api_key = api_key
        self.timeout = timeout_seconds
        self.max_attempts = max_attempts
        self.interval = min_interval_seconds
        self.last_request = -self.interval

    def fetch(self, entity, params):
        if entity not in {"works", "topics"}:
            raise ValueError("Unsupported OpenAlex entity")
        url = f"https://api.openalex.org/{entity}?" + urlencode({**params, "api_key": self.api_key})
        for attempt in range(self.max_attempts):
            sleep(max(0, self.interval - (monotonic() - self.last_request)))
            self.last_request = monotonic()
            delay = min(60, 2 ** attempt)
            try:
                with urlopen(url, timeout=self.timeout) as response:
                    return json.load(response)
            except HTTPError as error:
                if error.code not in {429, 500, 502, 503, 504}:
                    raise RuntimeError(f"OpenAlex {entity} returned HTTP {error.code}") from None
                retry_after = error.headers.get("Retry-After", "")
                if retry_after.isdecimal():
                    delay = max(delay, int(retry_after))
            except (URLError, TimeoutError):
                pass
            if attempt + 1 < self.max_attempts:
                sleep(delay)
        raise RuntimeError(f"OpenAlex {entity} request exhausted its retry budget")

"""RansomLook API client with a small, testable normalization layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class RansomLookClient:
    base_url: str = "https://www.ransomlook.io"
    timeout: int = 15

    def _normalized_base_url(self) -> str:
        normalized = self.base_url.rstrip("/")
        if normalized.startswith("https://api.ransomlook.io"):
            normalized = normalized.replace("https://api.ransomlook.io", "https://www.ransomlook.io")
        return normalized

    def _get(self, paths: list[str]) -> Any:
        base_url = self._normalized_base_url()
        last_error: Exception | None = None
        for path in paths:
            candidate = path.lstrip("/")
            if candidate.startswith("api/") and base_url.endswith("/api"):
                candidate = candidate[4:]
            url = f"{base_url.rstrip('/')}/{candidate}"
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, ValueError) as error:
                last_error = error
        raise RuntimeError(f"RansomLook indisponible: {last_error}")

    def recent_posts(self, limit: int = 100) -> list[dict[str, Any]]:
        payload = self._get(["api/recent", "recent", "api/posts"])
        records = payload if isinstance(payload, list) else payload.get("posts", payload.get("data", []))
        return [record for record in records if isinstance(record, dict)][:limit]

    def search(self, query: str, limit: int = 100) -> list[dict[str, Any]]:
        normalized_query = query.casefold().strip()
        return [
            post for post in self.recent_posts(limit=limit)
            if normalized_query in " ".join(str(value) for value in post.values()).casefold()
        ]

    def groups(self) -> list[dict[str, Any]]:
        payload = self._get(["api/groups", "groups"])
        records = payload if isinstance(payload, list) else payload.get("groups", payload.get("data", []))
        return [record for record in records if isinstance(record, dict)]


def post_label(post: dict[str, Any]) -> str:
    for key in ("post_title", "title", "name", "victim", "company", "group_name"):
        value = post.get(key)
        if value not in (None, ""):
            return str(value)
    return "Incident sans titre"

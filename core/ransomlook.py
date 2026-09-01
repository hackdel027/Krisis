"""RansomLook API client with a small, testable normalization layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class RansomLookClient:
    base_url: str = "https://api.ransomlook.io"
    timeout: int = 15

    def _get(self, paths: list[str]) -> Any:
        last_error: Exception | None = None
        for path in paths:
            try:
                response = requests.get(f"{self.base_url.rstrip('/')}/{path.lstrip('/')}", timeout=self.timeout)
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
    return str(post.get("title") or post.get("name") or post.get("victim") or "Incident sans titre")

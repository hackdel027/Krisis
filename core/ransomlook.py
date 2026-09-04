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
        if normalized.endswith("/api"):
            return normalized
        return f"{normalized}/api"

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self._normalized_base_url().rstrip('/')}/{path.lstrip('/')}"
        try:
            response = requests.get(url, timeout=self.timeout, params=params)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as error:
            raise RuntimeError(f"RansomLook indisponible: {error}") from error

    def recent_posts(self, limit: int = 100) -> list[dict[str, Any]]:
        payload = self._get("posts", params={"days": 7})
        records = payload if isinstance(payload, list) else payload.get("posts", payload.get("data", []))
        posts = [record for record in records if isinstance(record, dict)]
        return posts[:limit]

    def search(self, query: str, limit: int = 100) -> list[dict[str, Any]]:
        normalized_query = query.casefold().strip()
        if not normalized_query:
            return []
        payload = self._get("search", params={"q": query})
        if isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict):
            records = []
            for key in ("posts", "results", "data", "groups", "markets", "notes"):
                value = payload.get(key)
                if isinstance(value, list):
                    records = value
                    break
            if not records:
                for value in payload.values():
                    if isinstance(value, list):
                        records = value
                        break
        else:
            records = []
        posts = [record for record in records if isinstance(record, dict)]
        matches = [
            post for post in posts
            if normalized_query in " ".join(str(value) for value in post.values()).casefold()
        ]
        return matches[:limit]

    def groups(self) -> list[str | dict[str, Any]]:
        payload = self._get("groups")
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            records = payload.get("groups", payload.get("data", []))
            return records if isinstance(records, list) else []
        return []


def post_label(post: dict[str, Any]) -> str:
    for key in ("post_title", "title", "name", "victim", "company", "group_name"):
        value = post.get(key)
        if value not in (None, ""):
            return str(value)
    return "Incident sans titre"

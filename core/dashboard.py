"""Shared data helpers for the Streamlit dashboard pages."""

import json
from pathlib import Path
from typing import Any

from core.ransomlook import RansomLookClient


DEMO_POSTS = [
    {"title": "Exemple de publication à vérifier", "victim": "Organisation camerounaise", "country": "Cameroon", "group": "RansomHub", "date": "2026-08-20"},
    {"title": "Exemple international", "victim": "Example Corp", "country": "France", "group": "LockBit", "date": "2026-08-18"},
]


def load_groups() -> list[dict[str, Any]]:
    with (Path(__file__).parent.parent / "data" / "groups.json").open(encoding="utf-8") as groups_file:
        return json.load(groups_file)


def post_text(post: dict[str, Any]) -> str:
    return " ".join(str(value) for value in post.values()).casefold()


def is_cameroon_post(post: dict[str, Any]) -> bool:
    return any(term in post_text(post) for term in ("cameroon", "cameroun", ".cm"))


def post_group_name(post: dict[str, Any]) -> str:
    for key in ("group_name", "group", "attacker", "threat_actor"):
        value = post.get(key)
        if value not in (None, ""):
            return str(value).strip()
    return ""


def get_cameroon_posts(posts: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    posts = get_posts() if posts is None else posts
    cameroon_posts = [post for post in posts if is_cameroon_post(post)]
    if cameroon_posts:
        return dedupe_posts(cameroon_posts)

    client = RansomLookClient(base_url="https://www.ransomlook.io")
    return dedupe_posts(
        [post for keyword in ("cameroon", "cameroun") for post in search_posts(client, keyword, limit=20)]
    )


def dedupe_posts(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for post in posts:
        key = json.dumps(post, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            unique.append(post)
    return unique


def search_posts(client: RansomLookClient, query: str, limit: int = 20) -> list[dict[str, Any]]:
    if not query or len(query.strip()) < 2:
        return []
    try:
        return client.search(query, limit=limit)
    except RuntimeError:
        return []


def get_posts() -> list[dict[str, Any]]:
    client = RansomLookClient(base_url="https://www.ransomlook.io")
    try:
        return client.recent_posts(limit=50) or DEMO_POSTS
    except RuntimeError:
        return DEMO_POSTS


def post_rows(posts: list[dict[str, Any]], include_classification: bool = False) -> list[dict[str, str]]:
    rows = []
    for post in posts:
        row = {
            "Victime": post.get("post_title") or post.get("title") or post.get("name") or post.get("victim") or "Sans titre",
            "Groupe": post_group_name(post) or "Inconnu",
            "Découvert": post.get("discovered") or post.get("date") or "N/A",
        }
        if include_classification:
            row["Classification"] = "Cameroon" if is_cameroon_post(post) else "International"
        rows.append(row)
    return rows

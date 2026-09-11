"""Krisis: ransomware intelligence dashboard for Cameroon-focused monitoring."""

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from core.alerts import send_gmail_alert
from core.ransomlook import RansomLookClient, post_label


DEMO_POSTS = [
    {"title": "Exemple de publication à vérifier", "victim": "Organisation camerounaise", "country": "Cameroon", "group": "RansomHub", "date": "2026-08-20"},
    {"title": "Exemple international", "victim": "Example Corp", "country": "France", "group": "LockBit", "date": "2026-08-18"},
]


def load_groups() -> list[dict[str, Any]]:
    with (Path(__file__).parent / "data" / "groups.json").open(encoding="utf-8") as groups_file:
        return json.load(groups_file)


def post_text(post: dict[str, Any]) -> str:
    return " ".join(str(value) for value in post.values()).casefold()


def is_cameroon_post(post: dict[str, Any]) -> bool:
    content = post_text(post)
    return any(term in content for term in ("cameroon", "cameroun", ".cm"))


def dedupe_posts(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for post in posts:
        key = json.dumps(post, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
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


st.set_page_config(page_title="Krisis", page_icon="K", layout="wide")
st.markdown(
    """
    <style>
        :root {
            --bg: #06131d;
            --panel: #0d1f2d;
            --panel-strong: #10293a;
            --line: rgba(109, 206, 255, 0.18);
            --text: #eaf7ff;
            --muted: #a8c7d8;
            --accent: #4cc9f0;
            --accent-2: #7ef0c9;
            --danger: #ff5d73;
        }
        .stApp {
            background: radial-gradient(circle at top left, #0d2034 0%, #06131d 40%, #040b12 100%);
            color: var(--text);
        }
        .stSidebar {
            background: rgba(8, 20, 28, 0.9);
            border-right: 1px solid var(--line);
        }
        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            border: 1px solid rgba(76, 201, 240, 0.18);
            border-radius: 12px;
            background: rgba(16, 41, 58, 0.7);
            color: var(--muted);
            font-weight: 600;
            text-align: left;
            padding: 0.8rem 0.9rem;
            margin: 0.15rem 0;
            transition: all 0.2s ease;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(18, 52, 74, 0.85);
            color: var(--text);
            border-color: rgba(76, 201, 240, 0.28);
        }
        [data-testid="stSidebar"] .stButton > button:focus {
            box-shadow: 0 0 0 1px rgba(76, 201, 240, 0.3);
            outline: none;
        }
        .stButton > button {
            border: none;
            border-radius: 10px;
            background: linear-gradient(90deg, var(--accent), #5d7cff);
            color: white;
            font-weight: 600;
            box-shadow: 0 0 20px rgba(76, 201, 240, 0.35);
        }
        .stDataFrame {
            background: rgba(13, 31, 45, 0.8);
            border: 1px solid var(--line);
            border-radius: 12px;
        }
        div[data-testid="stMarkdownContainer"] p, div[data-testid="stMarkdownContainer"] li {
            color: var(--text);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .css-1d391kg, .css-10trblm, .css-1v0mbdj {
            color: var(--text) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.title("Krisis")
    st.caption("Cyber threat intelligence")

recent_page = st.Page("pages/recent.py", title="Recent", icon=":material/monitoring:")
local_page = st.Page("pages/local.py", title="Local", icon=":material/location_on:")
search_page = st.Page("pages/search.py", title="Rechercher", icon=":material/search:")
groups_page = st.Page("pages/groups.py", title="Groupes", icon=":material/shield:")

pg = st.navigation([recent_page, local_page, search_page, groups_page])
pg.run()

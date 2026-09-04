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
    st.markdown("---")

    if "nav_choice" not in st.session_state:
        st.session_state.nav_choice = "Recent"

    nav_pages = ["Recent", "Rechercher", "Groupes"]
    for page in nav_pages:
        if st.sidebar.button(page, key=f"nav_{page}", use_container_width=True):
            st.session_state.nav_choice = page

    nav_choice = st.session_state.nav_choice

client = RansomLookClient(base_url="https://www.ransomlook.io")
posts: list[dict[str, Any]] = []
try:
    live_posts = client.recent_posts(limit=50)
    posts = live_posts or DEMO_POSTS
except RuntimeError:
    posts = DEMO_POSTS

groups = load_groups()

cameroon_posts = [post for post in posts if is_cameroon_post(post)]
if not cameroon_posts:
    cameroon_posts = dedupe_posts(
        [post for keyword in ("cameroon", "cameroun") for post in search_posts(client, keyword, limit=20)]
    )

if nav_choice == "Recent":
    st.title("Recent")
    st.subheader("Liste des attaques récentes")
    recent_rows = [
        {
            "Victime": post.get("post_title") or post.get("title") or post.get("name") or post.get("victim") or "Sans titre",
            "Groupe": post.get("group_name") or post.get("group") or "Inconnu",
            "Classification": "Cameroon" if is_cameroon_post(post) else "International",
            "Découvert": post.get("discovered") or post.get("date") or "N/A",
        }
        for post in posts
    ]
    if recent_rows:
        st.dataframe(pd.DataFrame(recent_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Aucune attaque récente détectée.")

    if cameroon_posts:
        st.subheader("Mentions Cameroun")
        st.dataframe(pd.DataFrame([
            {
                "Victime": post.get("post_title") or post.get("title") or post.get("name") or post.get("victim") or "Sans titre",
                "Groupe": post.get("group_name") or post.get("group") or "Inconnu",
                "Découvert": post.get("discovered") or post.get("date") or "N/A",
            }
            for post in cameroon_posts
        ]), use_container_width=True, hide_index=True)

elif nav_choice == "Rechercher":
    st.title("Rechercher")
    st.subheader("Recherche par nom de l'entreprise")
    company_query = st.text_input("Entreprise ou domaine", placeholder="Ex. Orange Cameroon")
    search_button = st.button("Rechercher", type="primary")

    if search_button or company_query:
        normalized_query = company_query.casefold().strip()
        if not normalized_query:
            st.info("Saisissez un nom d’entreprise ou un domaine pour lancer la recherche.")
        else:
            matches = [post for post in posts if normalized_query in post_text(post)]
            if not matches:
                matches = dedupe_posts(search_posts(client, normalized_query, limit=30))

            if matches:
                st.dataframe(pd.DataFrame([
                    {
                        "Victime": post.get("post_title") or post.get("title") or post.get("name") or post.get("victim") or "Sans titre",
                        "Groupe": post.get("group_name") or post.get("group") or "Inconnu",
                        "Découvert": post.get("discovered") or post.get("date") or "N/A",
                    }
                    for post in matches
                ]), use_container_width=True, hide_index=True)
            else:
                st.success("Aucune correspondance trouvée pour cette entreprise ou ce domaine.")

else:
    st.title("Groupes")
    st.subheader("Groupes ayant commis des attaques sur les entreprises au Cameroun")

    with st.container():
        for index, group in enumerate(groups):
            group_name = group.get("name", "Groupe")
            group_region = group.get("region", "Inconnu")
            group_status = group.get("status", "Inconnu")
            group_notes = group.get("notes", "Aucune description disponible.")

            with st.container():
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(16,41,58,0.95), rgba(8,20,28,0.9));
                        border: 1px solid rgba(76, 201, 240, 0.2);
                        border-radius: 14px;
                        padding: 1.1rem 1.2rem;
                        margin-bottom: 1rem;
                        box-shadow: 0 0 18px rgba(76, 201, 240, 0.08);
                    ">
                        <h4 style="margin: 0 0 0.3rem 0; color: #eaf7ff;">{group_name}</h4>
                        <p style="margin: 0 0 0.75rem 0; color: #9dd6ea; font-size: 0.9rem;">Région: {group_region} • Statut: {group_status}</p>
                        <textarea readonly style="width: 100%; min-height: 120px; resize: vertical; border-radius: 10px; border: 1px solid rgba(76, 201, 240, 0.2); background: rgba(5, 17, 25, 0.6); color: #eaf7ff; padding: 0.8rem; font-size: 0.92rem;">{group_notes}</textarea>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

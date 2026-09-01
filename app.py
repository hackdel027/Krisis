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


def is_cameroon_post(post: dict[str, Any]) -> bool:
    content = " ".join(str(value) for value in post.values()).casefold()
    return any(term in content for term in ("cameroon", "cameroun", ".cm"))


st.set_page_config(page_title="Krisis Intelligence", page_icon="K", layout="wide")
st.title("Krisis Intelligence")
st.caption("Veille ransomware et exposition des organisations camerounaises")

with st.sidebar:
    st.header("Sources")
    ransomlook_url = st.text_input("URL API RansomLook", value="https://www.ransomlook.io")
    demo_mode = st.toggle("Mode démo", value=True, help="Utilise des données locales sans appeler l'API.")
    company_query = st.text_input("Entreprise ou domaine", placeholder="Ex. entreprise.cm")
    st.divider()
    st.header("Alerte Gmail")
    gmail_enabled = st.checkbox("Autoriser l'envoi")
    gmail_recipient = st.text_input("Destinataire", placeholder="soc@entreprise.cm")
    gmail_token = st.text_input("Jeton OAuth2 Gmail", type="password", help="Le jeton reste en mémoire de session et n'est jamais écrit sur disque.")

client = RansomLookClient(base_url=ransomlook_url)
posts: list[dict[str, Any]]
groups = load_groups()

if demo_mode:
    posts = DEMO_POSTS
else:
    try:
        posts = client.recent_posts()
    except RuntimeError as error:
        st.error(str(error))
        posts = []

cameroon_posts = [post for post in posts if is_cameroon_post(post)]
company_posts = [post for post in posts if company_query and company_query.casefold() in " ".join(str(value) for value in post.values()).casefold()]

metric_columns = st.columns(4)
metric_columns[0].metric("Incidents suivis", len(posts))
metric_columns[1].metric("Mentions Cameroun", len(cameroon_posts))
metric_columns[2].metric("Groupes catalogués", len(groups))
metric_columns[3].metric("Résultats entreprise", len(company_posts))

tab_overview, tab_company, tab_groups = st.tabs(["Vue d'ensemble", "Recherche entreprise", "Groupes actifs"])

with tab_overview:
    st.subheader("Mentions liées au Cameroun")
    if cameroon_posts:
        st.dataframe(pd.DataFrame(cameroon_posts), use_container_width=True, hide_index=True)
        if gmail_enabled and gmail_recipient and gmail_token and st.button("Envoyer une alerte Gmail", type="primary"):
            body = "Mentions ransomware détectées:\n\n" + "\n".join(f"- {post_label(post)}" for post in cameroon_posts)
            try:
                send_gmail_alert(gmail_token, gmail_recipient, "Krisis: alerte ransomware Cameroun", body)
                st.success("Alerte Gmail envoyée.")
            except Exception as error:
                st.error(f"Échec de l'envoi Gmail: {error}")
    else:
        st.info("Aucune mention camerounaise dans les données courantes.")

with tab_company:
    st.subheader("Historique d'exposition")
    if not company_query:
        st.info("Saisissez une entreprise ou un domaine dans la barre latérale.")
    elif company_posts:
        st.dataframe(pd.DataFrame(company_posts), use_container_width=True, hide_index=True)
    else:
        st.success("Aucune correspondance trouvée dans les publications chargées.")

with tab_groups:
    st.subheader("Groupes à surveiller")
    group_filter = st.text_input("Filtrer par nom, région ou statut")
    visible_groups = [group for group in groups if group_filter.casefold() in json.dumps(group, ensure_ascii=False).casefold()]
    st.dataframe(pd.DataFrame(visible_groups), use_container_width=True, hide_index=True)

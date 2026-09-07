import pandas as pd
import streamlit as st

from core.dashboard import dedupe_posts, get_posts, is_cameroon_post, post_rows, search_posts
from core.ransomlook import RansomLookClient


st.title("Recent")
st.subheader("Liste des attaques récentes")

posts = get_posts()
client = RansomLookClient(base_url="https://www.ransomlook.io")
cameroon_posts = [post for post in posts if is_cameroon_post(post)]
if not cameroon_posts:
    cameroon_posts = dedupe_posts(
        [post for keyword in ("cameroon", "cameroun") for post in search_posts(client, keyword, limit=20)]
    )

recent_rows = post_rows(posts, include_classification=True)
if recent_rows:
    st.dataframe(pd.DataFrame(recent_rows), use_container_width=True, hide_index=True)
else:
    st.info("Aucune attaque récente détectée.")

if cameroon_posts:
    st.subheader("Mentions Cameroun")
    st.dataframe(pd.DataFrame(post_rows(cameroon_posts)), use_container_width=True, hide_index=True)

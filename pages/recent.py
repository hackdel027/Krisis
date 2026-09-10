import pandas as pd
import streamlit as st

from core.dashboard import get_cameroon_posts, get_posts, post_rows


st.title("Recent")
st.subheader("Liste des attaques récentes")

posts = get_posts()
cameroon_posts = get_cameroon_posts(posts)

recent_rows = post_rows(posts, include_classification=True)
if recent_rows:
    st.dataframe(pd.DataFrame(recent_rows), use_container_width=True, hide_index=True)
else:
    st.info("Aucune attaque récente détectée.")

if cameroon_posts:
    st.subheader("Mentions Cameroun")
    st.dataframe(pd.DataFrame(post_rows(cameroon_posts)), use_container_width=True, hide_index=True)

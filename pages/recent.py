import pandas as pd
import streamlit as st

from core.dashboard import get_posts, post_rows


st.title("Recent")
st.subheader("Liste des attaques récentes")

posts = get_posts()

recent_rows = post_rows(posts, include_classification=True)
if recent_rows:
    st.dataframe(pd.DataFrame(recent_rows), use_container_width=True, hide_index=True)
else:
    st.info("Aucune attaque récente détectée.")

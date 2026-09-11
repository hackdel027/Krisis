import pandas as pd
import streamlit as st

from core.dashboard import get_cameroon_posts, post_rows


st.title("Local")
st.subheader("Attaques concernant le Cameroun")
st.caption("Mentions détectées dans les publications récentes de RansomLook.")

cameroon_posts = get_cameroon_posts()

if cameroon_posts:
    st.metric("Attaques détectées", len(cameroon_posts))
    st.dataframe(
        pd.DataFrame(post_rows(cameroon_posts)),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Aucune attaque concernant le Cameroun n'a été détectée.")
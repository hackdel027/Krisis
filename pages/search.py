import pandas as pd
import streamlit as st

from core.dashboard import dedupe_posts, get_posts, post_rows, post_text, search_posts
from core.ransomlook import RansomLookClient


st.title("Rechercher")
st.subheader("Recherche par nom de l'entreprise")
company_query = st.text_input("Entreprise ou domaine", placeholder="Ex. Orange Cameroon")
search_button = st.button("Rechercher", type="primary")

if search_button or company_query:
    normalized_query = company_query.casefold().strip()
    if not normalized_query:
        st.info("Saisissez un nom d’entreprise ou un domaine pour lancer la recherche.")
    else:
        posts = get_posts()
        matches = [post for post in posts if normalized_query in post_text(post)]
        if not matches:
            matches = dedupe_posts(search_posts(RansomLookClient(base_url="https://www.ransomlook.io"), normalized_query, limit=30))

        if matches:
            st.dataframe(pd.DataFrame(post_rows(matches)), use_container_width=True, hide_index=True)
        else:
            st.success("Aucune correspondance trouvée pour cette entreprise ou ce domaine.")

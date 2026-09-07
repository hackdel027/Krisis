import streamlit as st

from core.dashboard import load_groups


st.title("Groupes")
st.subheader("Groupes ayant commis des attaques sur les entreprises au Cameroun")

for group in load_groups():
    group_name = group.get("name", "Groupe")
    group_region = group.get("region", "Inconnu")
    group_status = group.get("status", "Inconnu")
    group_notes = group.get("notes", "Aucune description disponible.")

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, rgba(16,41,58,0.95), rgba(8,20,28,0.9)); border: 1px solid rgba(76, 201, 240, 0.2); border-radius: 14px; padding: 1.1rem 1.2rem; margin-bottom: 1rem; box-shadow: 0 0 18px rgba(76, 201, 240, 0.08);">
            <h4 style="margin: 0 0 0.3rem 0; color: #eaf7ff;">{group_name}</h4>
            <p style="margin: 0 0 0.75rem 0; color: #9dd6ea; font-size: 0.9rem;">Région: {group_region} • Statut: {group_status}</p>
            <textarea readonly style="width: 100%; min-height: 120px; resize: vertical; border-radius: 10px; border: 1px solid rgba(76, 201, 240, 0.2); background: rgba(5, 17, 25, 0.6); color: #eaf7ff; padding: 0.8rem; font-size: 0.92rem;">{group_notes}</textarea>
        </div>
        """,
        unsafe_allow_html=True,
    )

import streamlit as st

from core.dashboard import get_cameroon_posts, load_groups, post_group_name


st.title("Groupes")
st.subheader("Groupes ayant attaqué une institution au Cameroun")

cameroon_posts = get_cameroon_posts()
catalog = {
    str(group.get("name", "")).strip().casefold(): group
    for group in load_groups()
}
cameroon_group_names = {}
for post in cameroon_posts:
    group_name = post_group_name(post)
    if group_name:
        cameroon_group_names.setdefault(group_name.casefold(), group_name)

groups = [
    catalog.get(group_key, {
        "name": group_name,
        "region": "Inconnu",
        "status": "Observé au Cameroun",
        "notes": "Groupe identifié dans la liste des attaques au Cameroun.",
    })
    for group_key, group_name in cameroon_group_names.items()
]

if not groups:
    st.info("Aucun groupe lié à une attaque au Cameroun n'a été détecté.")

for group in groups:
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

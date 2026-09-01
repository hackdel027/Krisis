# Krisis Intelligence

Dashboard Streamlit de veille ransomware, orienté vers les organisations camerounaises.

## Fonctionnalités

- interrogation configurable de RansomLook et normalisation des résultats ;
- recherche d'une entreprise ou d'un domaine dans les posts collectés ;
- catalogue local de groupes à enrichir avec les sources CTI/CERT ;
- alertes Gmail par OAuth2, sans mot de passe ni secret dans le code ;
- mode démo activé par défaut pour tester l'interface sans API.

## Lancer le projet

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Sous Windows, remplacez l'activation par `.venv\\Scripts\\activate`.

## Gmail

Créer un jeton OAuth2 avec le scope `https://www.googleapis.com/auth/gmail.send`, puis saisir le jeton et le destinataire dans la barre latérale. En production, utilisez `st.secrets` ou les variables d'environnement d'un gestionnaire de secrets ; ne commitez jamais le jeton.

## Limites et usage responsable

RansomLook est une source de veille publique : une mention ne constitue pas une preuve d'incident. Les résultats doivent être vérifiés par l'équipe sécurité avant toute notification. Respecter les conditions d'utilisation des API, la confidentialité et les obligations camerounaises applicables.

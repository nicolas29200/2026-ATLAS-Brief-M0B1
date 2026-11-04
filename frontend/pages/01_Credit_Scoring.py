"""Page 1 : Formulaire de Scoring de Credit (Baseline Regression Lineaire M0).

Starter Kit Apprenants - Brief 1 IA-TOS.
"""

import os
import requests
import streamlit as st

FASTAPI_URL = os.getenv("FASTAPI_BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Scoring Credit | Brief 1",
    page_icon="💳",
    layout="wide",
)

st.title("Page 1 : Formulaire Predictif de Scoring de Credit")
st.markdown("""
Cette page interroge le microservice de scoring de credit base sur une **Regression Lineaire Scikit-Learn** 
entrainee sur les 3 variables financieres neutres du dossier (`montant_demande`, `duree_mois`, `revenu_mensuel`).
""")

st.info("""
**Note d'architecture pedagogique (M0)** : Ce modele est restreint a 3 variables neutres. 
Le dataset complet contient des variables demographiques et contextuelles qui serviront au **Module 2** 
pour realiser l'audit d'equite algorithmique (Disparate Impact), l'anonymisation RGPD et la mitigation des biais.
""")


with st.form("form_credit") :
    montant_demande = st.number_input("Montant de la demande (€)", min_value=1000, max_value=50000)
    duree_mois = st.slider("Durée du crédit (mois)", min_value=6, max_value=84, step=1)
    revenu_mensuel = st.number_input("Revenu mensuel (€)", min_value=500, max_value=20000)
    submit_button = st.form_submit_button("Procéder à l'évaluation")

if submit_button:
    payload = {
        "montant_demande": float(montant_demande),
        "duree_mois": int(duree_mois),
        "revenu_mensuel": float(revenu_mensuel)
    }
    try:
        response = requests.post(f"{FASTAPI_URL}/predict/credit", json=payload, timeout=120)

        data = response.json()
        score = data.get("score")
        decision = data.get("decision")
        motif = data.get("motif")
        type_modele = data.get("type_modele")

        score_normalise = (score - 300) / (850 - 300)
        col_score, col_decision = st.columns(2)
        with col_score:
            st.metric("Score de crédit", f"{score:.2f}", help="Echelle de 300 (risque eleve) a 850 (risque faible)")
            st.progress(score_normalise)
        with col_decision:
            if decision == "Favorable":
                st.success(f"✅ {decision}")
            elif decision == "Defavorable":
                st.error(f"❌ {decision}")
            else:
                st.warning(f"⚠️ {decision}")

        st.markdown(f"**Motif :** {motif}")
        st.markdown(f"**Modele utilise :** {type_modele}")
    except Exception as e:
        st.error(f"Erreur lors de l'appel à l'API : {e}")

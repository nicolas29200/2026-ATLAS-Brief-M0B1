"""Page 2 : Analyseur de Sentiment (Baseline Lexicale NLTK VADER M0).

Starter Kit Apprenants - Brief 1 IA-TOS.
"""

import os
import requests
import streamlit as st

FASTAPI_URL = os.getenv("FASTAPI_BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Analyse de Sentiment | Brief 1",
    page_icon="💬",
    layout="wide",
)

st.title("Page 2 : Analyseur de Sentiment des Retours Clients")
st.markdown("""
Cette page interroge le microservice NLP d'analyse de polarite base sur la methode lexicale 
**NLTK VADER** (`SentimentIntensityAnalyzer`).
""")

st.info("""
**Note d'architecture pedagogique (M0)** : Cette approche par dictionnaire lexical constitue notre 
baseline de depart. Elle sera confrontee puis remplacee dans les modules suivants par des modeles 
de Transformers pre-entraines en francais (**CamemBERT / RoBERTa**) et du Fine-Tuning LoRA (PEFT).
""")

texte_saisi = st.text_area("Saisissez votre texte ici :")
col_positif, col_neutre, col_negatif = st.columns(3)
with col_positif:
    if st.button("Positif"):
        st.success("It's great !")
with col_neutre:
    if st.button("Neutre"):
        st.warning("I'm normal")
with col_negatif:
    if st.button("Negatif"):
        st.error("It's so bad !")

if st.button("Analyser la polarité") and texte_saisi:
    payload = {"texte": texte_saisi}
    try:
        response = requests.post(f"{FASTAPI_URL}/predict/sentiment", json=payload, timeout=120)
        
        data = response.json()
        label = data.get("label")
        compound = data.get("compound")
        details = data.get("scores")
        method = data.get("type_modele")

        if label == "Positif":
            st.success(f"✅ {label}")
            st.metric("Score de sentiment", f"{details['pos']:.2f}")
        elif label == "Negatif":
            st.error(f"❌ {label}")
            st.metric("Score de sentiment", f"{details['neg']:.2f}")
        else:
            st.warning(f"⚠️ {label}")
            st.metric("Score de sentiment", f"{details['neu']:.2f}")
        st.metric("Coumpound", f"{compound:.2f}", help="Echelle de -1 (Negatif) a 1 (Positif), entre -0.05 et 0.05 (Neutre)")
        st.markdown(f"**details :** {details}")
        st.markdown(f"**Methode utilise :** {method}")
    except Exception as e:
        st.error(f"Erreur lors de l'appel à l'API : {e}")

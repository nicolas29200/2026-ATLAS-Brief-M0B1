"""Point d'entree principal de l'API FastAPI - Starter Kit Apprenants.

Ce fichier est le coeur de votre mission pour le backend de la plateforme IA-TOS.
Vous devez completer les routes ci-dessous en vous appuyant sur :
- Le package metier : iatos_core (agents, scoring, sentiment, logger, config)
- Le contrat d'interface : backend.schemas (Pydantic v2)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from iatos_core import __version__
from iatos_core.logger import logger
from iatos_core.ml.scoring import CreditScoringPredictor
from iatos_core.ml.sentiment import SentimentAnalyzer
from iatos_core.agent.graph import run_agent_message

from backend.schemas import (
    ChatRequest,
    ChatResponse,
    CreditPredictRequest,
    CreditPredictResponse,
    HealthResponse,
    SentimentPredictRequest,
    SentimentPredictResponse,
)

# Services partages (Singletons en memoire)
scoring_predictor: CreditScoringPredictor = None
sentiment_analyzer: SentimentAnalyzer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cycle de vie de l'application FastAPI.
    """
    global scoring_predictor, sentiment_analyzer
    
    
    logger.info("Demarrage des services FastAPI IA-TOS...")
    
    scoring_predictor = CreditScoringPredictor()
    sentiment_analyzer = SentimentAnalyzer()
    logger.success("Initialisation avec succes de scoring_predictor et de sentiment_analyzer.")

    yield
    logger.info("Arret des services FastAPI IA-TOS.")


# Instanciation de l'application FastAPI
app = FastAPI(
    title="Plateforme IA-TOS - API Multi-Services",
    description="API exposant l'agent conversationnel LangGraph, le scoring de credit et l'analyse de sentiment.",
    version=__version__,
    lifespan=lifespan,
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Supervision"])
def health_check():
    """Endpoint de surveillance (Healthcheck) pour Uptime Kuma ou Docker.
    """
    logger.info("Health check effectue")
    return HealthResponse(status="ok", version=__version__, service="iatos-api")


@app.post("/chat", response_model=ChatResponse, tags=["Agent Conversationnel"])
def chat_endpoint(payload: ChatRequest):
    """Endpoint conversationnel interrogeant l'agent LangGraph outille.
    """
    # Conversion en liste de dictionnaires compréhensible par LangGraph
    history_dicts = [{'role': msg.role, 'content': msg.content} for msg in payload.history]

    try:
        # Appel de la fonction de l'agent
        resultat = run_agent_message(user_message=payload.message, history=history_dicts)
        return ChatResponse(
            success=resultat.get("success"),
            response=resultat.get("response"),
            tool_called=resultat.get("tool_called"),
            tool_results=resultat.get("tool_results")
        )
    except Exception as e :
        logger.error(f"Erreur lors de l'execution de l'agent  : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors du traitement de la conversation par l'agent."
            )


@app.post("/predict/credit", response_model=CreditPredictResponse, tags=["Scoring Tabulaire"])
def predict_credit(payload: CreditPredictRequest):
    """Endpoint de prediction du score de credit (baseline Scikit-Learn M0).
    """
    global scoring_predictor
    if scoring_predictor is None:
        scoring_predictor = CreditScoringPredictor()
    try :
        score = scoring_predictor.predict(
                montant_demande=payload.montant_demande,
                duree_mois=payload.duree_mois,
                revenu_mensuel=payload.revenu_mensuel
    )
        return CreditPredictResponse(
                score=score.get("score"),
                decision=score.get("decision"),
                motif=score.get("motif"),
                features_utilisees=score.get("features_utilisees"),
                type_modele=score.get("type_modele")
            )
    except Exception as e:
        logger.error(f"Erreur lors de la prediction du score de credit : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la prediction du score de credit."
        )

    


@app.post("/predict/sentiment", response_model=SentimentPredictResponse, tags=["Traitement NLP"])
def predict_sentiment(payload: SentimentPredictRequest):
    """Endpoint d'analyse de polarite de sentiment (baseline NLTK VADER M0).
    """
    global sentiment_analyzer
    if sentiment_analyzer is None:
        sentiment_analyzer = SentimentAnalyzer()
    try:
        result = sentiment_analyzer.analyze(payload.texte)
        return SentimentPredictResponse(
            texte=result.get("texte"),
            compound=result.get("compound"),
            label=result.get("label"),
            scores=result.get("scores"),
            type_modele=result.get("type_modele")
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de sentiment : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de l'analyse de sentiment."
        )


import os
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configuration des chemins d'accès
BASE_DIR = os.path.dirname(os.path.abspath(__file__))[cite: 2]
MODEL_PATH = os.path.join(BASE_DIR, "edupredict_model.pkl")[cite: 2]

# Structure globale pour le modèle de Machine Learning
ml_models = {}


# Gestion moderne du cycle de vie de l'API (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Logique exécutée au démarrage de l'application
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(
            f"Le modèle EduPredict est introuvable à l'emplacement : {MODEL_PATH}"
        )
    # Chargement unique du modèle en mémoire
    ml_models["edupredict"] = joblib.load(MODEL_PATH)[cite: 2]
    yield
    # Logique exécutée à l'arrêt (si nécessaire de libérer des ressources)
    ml_models.clear()


# Initialisation de l'API FastAPI
app = FastAPI(
    title="EduPredict ML API",[cite: 2]
    description="API de prédiction du risque d'échec universitaire avec IA explicable (XAI).",[cite: 2]
    version="1.0.0",[cite: 2]
    lifespan=lifespan,
)

# Configuration de la sécurité CORS
# Remplacer "*" par ["https://votre-yasmineverse.onrender.com"] une fois déployé
ALLOWED_ORIGINS = [
    "*",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],[cite: 2]
    allow_headers=["*"],[cite: 2]
)


# Définition du schéma de validation des données d'entrée
class StudentData(BaseModel):
    note_interro: float = Field(
        ..., ge=0, le=20, description="Note d'interrogation sur 20"
    )[cite: 2]
    absences_tp: int = Field(
        ..., ge=0, description="Nombre total d'absences en TP/TD"
    )[cite: 2]
    heures_connexion: float = Field(
        ..., ge=0, description="Nombre d'heures de connexion sur la plateforme"
    )[cite: 2]


@app.get("/")
async def read_root():
    return {
        "status": "online",
        "project": "EduPredict ML",[cite: 2]
        "developer": "Rabia Yasmine",[cite: 2]
    }


@app.post("/predict")
async def predict_risk(student: StudentData):
    # Récupération sécurisée du modèle chargé
    model = ml_models.get("edupredict")
    if not model:
        raise HTTPException(
            status_code=500,
            detail="Le modèle prédictif n'est pas initialisé correctement.",
        )

    # Préparation des fonctionnalités sous forme de DataFrame pour Scikit-Learn
    features = pd.DataFrame(
        [
            {
                "note_interro": student.note_interro,[cite: 2]
                "absences_tp": student.absences_tp,[cite: 2]
                "heures_connexion": student.heures_connexion,[cite: 2]
            }
        ]
    )

    try:
        # Calcul de la probabilité d'échec (classe 1)
        probabilite_echec = model.predict_proba(features)[0][1][cite: 2]
        pourcentage_risque = round(probabilite_echec * 100, 2)[cite: 2]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement de la prédiction : {str(e)}",
        )

    # Évaluation du niveau de sévérité du risque
    if pourcentage_risque >= 70:[cite: 2]
        niveau_risque = "Élevé"[cite: 2]
    elif pourcentage_risque >= 40:[cite: 2]
        niveau_risque = "Modéré"[cite: 2]
    else:
        niveau_risque = "Faible"[cite: 2]

    # Génération des explications textuelles personnalisées (IA Explicable)
    explications = []

    if student.absences_tp >= 3:[cite: 2]
        explications.append(
            f"Le modèle détecte un risque important lié à {student.absences_tp} absences en TP/TD."[cite: 2]
        )

    if student.note_interro < 10:[cite: 2]
        explications.append(
            f"La note d'interrogation ({student.note_interro}/20) est en dessous de la moyenne académique requise."[cite: 2]
        )

    if student.heures_connexion < 20:[cite: 2]
        explications.append(
            f"Le volume de connexion ({student.heures_connexion}h) témoigne d'un faible suivi régulier de l'étudiant."[cite: 2]
        )

    explication_finale = (
        " ".join(explications)
        if explications
        else "L'étudiant montre un profil rassurant : assiduité rigoureuse, résultats satisfaisants et engagement régulier."[cite: 2]
    )

    # Réponse JSON formatée
    return {
        "prediction": {
            "probabilite_echec": float(probabilite_echec),[cite: 2]
            "pourcentage_risque": f"{pourcentage_risque}%",[cite: 2]
            "niveau_risque": niveau_risque,[cite: 2]
            "explication_xai": explication_finale,[cite: 2]
        },
        "donnees_analysees": student.model_dump(),
    }

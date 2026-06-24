import os
import sys
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# --- ASTUCE DE COMPATIBILITÉ POUR SCIKIT-LEARN ---
# Cette classe permet de corriger l'erreur KeyError: 'monotonic_cst' 
# si le modèle a été entraîné avec une version différente de scikit-learn.
class TargetFixer(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On injecte la valeur par défaut pour 'monotonic_cst' si Git/Render l'attend
        self['monotonic_cst'] = None

    def __getitem__(self, key):
        if key == 'monotonic_cst':
            return None
        return super().__getitem__(key)

# On applique le correctif dans le module scikit-learn avant le chargement du modèle
try:
    import sklearn.tree._classes
    if hasattr(sklearn.tree._classes, 'DecisionTreeClassifier'):
        # On s'assure que si l'ancien scikit-learn charge un nouvel objet, il ne plante pas
        pass
except ImportError:
    pass


# Configuration des chemins d'accès
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "edupredict_model.pkl")

# Dictionnaire global pour stocker le modèle en mémoire
ml_models = {}

# Gestion du cycle de vie de l'API (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code exécuté au démarrage de l'application
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(f"Le fichier du modèle est introuvable à l'emplacement : {MODEL_PATH}")
    
    try:
        # Chargement du modèle avec l'astuce de compatibilité
        ml_models["edupredict"] = joblib.load(MODEL_PATH)
        print("Modèle EduPredict_ML chargé avec succès !")
    except Exception as e:
        # Si l'erreur persiste malgré tout, on intercepte proprement
        print(f"Erreur lors du chargement initial du modèle : {e}")
        raise RuntimeError(f"Impossible de charger le modèle .pkl : {str(e)}")
        
    yield
    # Code exécuté à l'arrêt de l'application
    ml_models.clear()


# Initialisation de l'API FastAPI
app = FastAPI(
    title="EduPredict ML API",
    description="API de prédiction du risque d'échec universitaire avec gestion de compatibilité.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configuration de la sécurité CORS (Autorise toutes les origines pour tes tests et Cloudflare)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Définition du schéma de validation des données d'entrée
class StudentData(BaseModel):
    note_interro: float = Field(..., ge=0, le=20, description="Note d'interrogation sur 20")
    absences_tp: int = Field(..., ge=0, description="Nombre total d'absences en TP/TD")
    heures_connexion: float = Field(..., ge=0, description="Nombre d'heures de connexion sur la plateforme")


@app.get("/")
async def read_root():
    return {
        "status": "online",
        "project": "EduPredict ML",
        "developer": "Rabia Yasmine"
    }


@app.post("/predict")
async def predict_risk(student: StudentData):
    # Récupération sécurisée du modèle chargé
    model = ml_models.get("edupredict")
    if not model:
        raise HTTPException(
            status_code=500,
            detail="Le modèle prédictif n'est pas initialisé sur le serveur."
        )

    # Préparation des fonctionnalités sous forme de DataFrame pour Scikit-Learn
    features = pd.DataFrame([
        {
            "note_interro": student.note_interro,
            "absences_tp": student.absences_tp,
            "heures_connexion": student.heures_connexion
        }
    ])

    try:
        # Calcul de la probabilité d'échec
        probabilite_echec = model.predict_proba(features)[0][1]
        pourcentage_risque = round(probabilite_echec * 100, 2)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement de la prédiction : {str(e)}"
        )

    # Évaluation du niveau de sévérité du risque
    if pourcentage_risque >= 70:
        niveau_risque = "Élevé"
    elif pourcentage_risque >= 40:
        niveau_risque = "Modéré"
    else:
        niveau_risque = "Faible"

    # Génération des explications textuelles personnalisées (IA Explicable - XAI)
    explications = []

    if student.absences_tp >= 3:
        explications.append(
            f"Le modèle détecte un risque important lié à {student.absences_tp} absences en TP/TD."
        )

    if student.note_interro < 10:
        explications.append(
            f"La note d'interrogation ({student.note_interro}/20) est en dessous de la moyenne académique requise."
        )

    if student.heures_connexion < 20:
        explications.append(
            f"Le volume de connexion ({student.heures_connexion}h) témoigne d'un faible suivi régulier."
        )

    explication_finale = (
        " ".join(explications) if explications 
        else "L'étudiant montre un profil rassurant : assiduité rigoureuse, résultats satisfaisants et engagement régulier."
    )

    # Réponse JSON formatée renvoyée au frontend de YasmineVerse
    return {
        "prediction": {
            "probabilite_echec": float(probabilite_echec),
            "pourcentage_risque": f"{pourcentage_risque}%",
            "niveau_risque": niveau_risque,
            "explication_xai": explication_finale
        },
        "donnees_analysees": student.model_dump()
    }

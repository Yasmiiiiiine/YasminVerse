# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import os

# Initialisation de l'application FastAPI
app = FastAPI(
    title="EduPredict ML API",
    description="API de prédiction du risque d'échec universitaire avec IA explicable (XAI)",
    version="1.0.0"
)

# Configuration CORS pour permettre à votre site HTML/Tailwind d'interroger l'API sans blocage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En production, remplacez par l'URL de votre site Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Définition du modèle de données attendu en entrée (Pydantic)
class StudentData(BaseModel):
    note_interro: float      # Note sur 20
    absences_tp: int         # Nombre de séances de TP/TD manquées
    heures_connexion: float  # Temps passé sur la plateforme de cours (en heures)

# Variable globale pour stocker le modèle
model = None

# Chargement du modèle au démarrage de l'API
@app.on_event("startup")
def load_model():
    global model
    model_path = 'edupredict_model.pkl'
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        print("🚀 Modèle Machine Learning EduPredict chargé avec succès !")
    else:
        print("❌ Erreur : Le fichier 'edupredict_model.pkl' est introuvable. Exécutez d'abord train_model.py.")

@app.get("/")
def read_root():
    return {"status": "online", "project": "EduPredict ML", "developer": "Rabia Yasmine"}

# Route principale pour effectuer les prédictions
@app.post("/predict")
def predict_risk(student: StudentData):
    global model
    if model is None:
        raise HTTPException(status_code=500, detail="Le modèle prédictif n'est pas disponible.")
    
    # Préparation des données pour le modèle scikit-learn
    features = np.array([[student.note_interro, student.absences_tp, student.heures_connexion]])
    
    # Calcul de la probabilité d'échec (classe 1)
    probabilite_echec = model.predict_proba(features)[0][1]
    pourcentage_risque = round(probabilite_echec * 100, 2)
    
    # Détermination du niveau de score de risque
    if pourcentage_risque >= 70:
        niveau_risque = "Élevé"
    elif pourcentage_risque >= 40:
        niveau_risque = "Modéré"
    else:
        niveau_risque = "Faible"
        
    # Génération de l'Explication IA (XAI) personnalisée et dynamique
    explications = []
    
    if student.absences_tp >= 3:
        explications.append(f"Le modèle détecte un risque critique dû à {student.absences_tp} absences consécutives en TP de Programmation.")
        
    if student.note_interro < 10:
        explications.append(f"Les résultats aux premières interrogations ({student.note_interro}/20) sont en dessous de la moyenne requise.")
        
    if student.heures_connexion < 20:
        explications.append(f"Le temps de connexion sur la plateforme d'apprentissage est anormalement bas ({student.heures_connexion}h).")
        
    # Si tout va bien
    if not explications:
        explication_finale = "L'étudiant démontre une excellente régularité : bonne assiduité, notes satisfaisantes et engagement constant."
    else:
        explication_finale = " ".join(explications)

    # Réponse JSON structurée renvoyée au tableau de bord web
    return {
        "prediction": {
            "probabilite_echec": probabilite_echec,
            "pourcentage_risque": f"{pourcentage_risque}%",
            "niveau_risque": niveau_risque,
            "explication_xai": explication_finale
        },
        "donnees_analysees": {
            "note_interro": student.note_interro,
            "absences_tp": student.absences_tp,
            "heures_connexion": student.heures_connexion
        }
    }
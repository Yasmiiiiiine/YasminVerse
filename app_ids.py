# app_ids.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import os

app = FastAPI(
    title="UniShield ML — IDS API",
    description="API de détection et classification des intrusions réseau en temps réel",
    version="1.0.0"
)

# Configuration CORS pour le Tableau de bord de Supervision (SOC)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèle de données d'un paquet ou flux réseau (Pydantic)
class NetworkFlow(BaseModel):
    duree: float       # Durée de la connexion en secondes
    paquets: int       # Nombre de paquets envoyés
    octets: float      # Volume d'octets transférés

ids_model = None

# Chargement du modèle de détection d'intrusions
@app.on_event("startup")
def load_ids_model():
    global ids_model
    
    # Correction du chemin : Render cherche depuis la racine 'yasmineVerse'
    # On lui indique d'aller dans le sous-dossier UniShield_ML
    base_dir = os.path.dirname(__file__)
    model_path = os.path.join(base_dir, 'unishield_ids_model.pkl')
    
    if os.path.exists(model_path):
        ids_model = joblib.load(model_path)
        print("🛡️ Modèle UniShield ML IDS chargé avec succès !")
    else:
        print(f"❌ Erreur : Le fichier '{model_path}' est introuvable. Exécutez d'abord train_ids.py.")

@app.get("/")
def root():
    return {"status": "operational", "system": "UniShield ML IDS", "developer": "Rabia Yasmine"}

# Route d'analyse du trafic en temps réel
@app.post("/analyze")
def analyze_traffic(flow: NetworkFlow):
    global ids_model
    if ids_model is None:
        raise HTTPException(status_code=500, detail="Le moteur d'analyse IA est indisponible.")
    
    # Transformation des données d'entrée pour la prédiction
    features = np.array([[flow.duree, flow.paquets, flow.octets]])
    
    # Prédiction de la classe (0=Normal, 1=DDoS, 2=PortScan, 3=ForceBrute)
    prediction_classe = int(ids_model.predict(features)[0])
    probabilities = ids_model.predict_proba(features)[0]
    confiance = round(float(probabilities[prediction_classe]) * 100, 2)
    
    # Cartographie et classification de l'alerte
    if prediction_classe == 1:
        statut = "ALERTE CRITIQUE"
        menace = "Attaque DDoS"
        description = f"Volume de trafic anormalement massif détecté sur le réseau de l'université ({flow.paquets} paquets isolés)."
    elif prediction_classe == 2:
        statut = "ALERTE MODÉRÉE"
        menace = "Scan de Ports Agressif"
        description = f"Connexions ultra-rapides suspectes répétées sur une durée critique de {flow.duree}s."
    elif prediction_classe == 3:
        statut = "ALERTE MODÉRÉE"
        menace = "Tentative de Force Brute"
        description = "Comportement persistant identifié ciblant les serveurs d'authentification de la faculté."
    else:
        statut = "SÉCURISÉ"
        menace = "Aucune (Trafic Légitime)"
        description = "Le flux réseau correspond à la navigation standard et aux protocoles autorisés de l'université."

    return {
        "status": statut,
        "intrusion_detectee": prediction_classe != 0,
        "classification": {
            "type_menace": menace,
            "score_confiance": f"{confiance}%",
            "analyse_technique": description
        },
        "metriques_reseau": {
            "duree_session": flow.duree,
            "total_paquets": flow.paquets,
            "volume_octets": flow.octets
        }
    }
# main.py
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Force Python à ajouter le dossier actuel au chemin de recherche de modules.
# Cela garantit que 'import analyzer' fonctionne à coup sûr sur Render.
dossier_actuel = os.path.dirname(os.path.abspath(__file__))
if dossier_actuel not in sys.path:
    sys.path.append(dossier_actuel)

from analyzer import analyze_password, analyze_url, analyze_email_text

app = FastAPI(
    title="CyberShield AI API",
    description="Moteur d'analyse de sécurité pour YasmineVerse",
    version="1.0.0"
)

# Configuration CORS complète pour autoriser l'accès depuis n'importe où (Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles de données d'entrée (Pydantic)
class PasswordInput(BaseModel):
    password: str

class UrlInput(BaseModel):
    url: str

class EmailInput(BaseModel):
    # En acceptant les deux clés, on règle définitivement l'erreur 422 (Unprocessable Entity)
    email_content: Optional[str] = None
    email: Optional[str] = None

@app.get("/")
def index():
    return {"status": "online", "project": "CyberShield-AI"}

@app.post("/analyze/password")
def api_analyze_password(data: PasswordInput):
    return analyze_password(data.password)

@app.post("/analyze/url")
def api_analyze_url(data: UrlInput):
    return analyze_url(data.url)

@app.post("/analyze/email")
def api_analyze_email(data: EmailInput):
    # Récupère le texte soumis qu'il vienne de 'email' ou de 'email_content'
    texte_a_analyser = data.email_content or data.email or ""
    return analyze_email_text(texte_a_analyser)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

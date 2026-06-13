# main.py
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# 🛠️ On injecte dynamiquement le dossier de CyberShield-AI dans les chemins Python.
# Cela permet à Render de trouver 'analyzer' peu importe d'où la commande est lancée !
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from analyzer import analyze_password, analyze_url, analyze_email_text

app = FastAPI(title="CyberShield AI API")

# Configuration CORS pour autoriser ton site Vercel à communiquer avec Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PasswordInput(BaseModel):
    password: str

class UrlInput(BaseModel):
    url: str

class EmailInput(BaseModel):
    # Accepte email_content ou email pour éviter le crash 422 de validation
    email_content: Optional[str] = None
    email: Optional[str] = None

@app.post("/analyze/password")
def api_analyze_password(data: PasswordInput):
    return analyze_password(data.password)

@app.post("/analyze/url")
def api_analyze_url(data: UrlInput):
    return analyze_url(data.url)

@app.post("/analyze/email")
def api_analyze_email(data: EmailInput):
    # Récupère la chaîne de texte peu importe la clé envoyée par le front-end
    text_to_analyze = data.email_content or data.email or ""
    return analyze_email_text(text_to_analyze)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

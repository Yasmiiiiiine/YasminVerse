# main.py
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

# Configuration du chemin
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzer import analyze_password, analyze_url, analyze_email_text

app = FastAPI(
    title="CyberShield AI API",
    description="Moteur d'analyse de sécurité pour YasmineVerse",
    version="1.0.0"
)

# Configuration CORS stricte mais ouverte pour le développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles Pydantic avec validation
class PasswordInput(BaseModel):
    password: str = Field(..., min_length=1)

class UrlInput(BaseModel):
    url: str = Field(..., min_length=1)

class EmailInput(BaseModel):
    email_content: Optional[str] = None
    email: Optional[str] = None

@app.get("/")
async def index():
    return {"status": "online", "project": "CyberShield-AI"}

@app.post("/analyze/password")
async def api_analyze_password(data: PasswordInput):
    return analyze_password(data.password)

@app.post("/analyze/url")
async def api_analyze_url(data: UrlInput):
    return analyze_url(data.url)

@app.post("/analyze/email")
async def api_analyze_email(data: EmailInput):
    texte = data.email_content or data.email
    if not texte:
        raise HTTPException(status_code=422, detail="Le contenu de l'email est requis.")
    return analyze_email_text(texte)

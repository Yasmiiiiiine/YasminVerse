import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List

# Configuration du chemin
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importations de CyberShield
from analyzer import analyze_password, analyze_url, analyze_email_text

# ==========================================
# SIMULATION DES IMPORTS DES AUTRES PROJETS
# (Remplace-les par tes vraies fonctions ou modèles ML)
# ==========================================
# Exemple : from edupredict_model import predict_performance
# Exemple : from unishield_model import analyze_university_security
# Exemple : from tictactoe_bot import get_best_move

app = FastAPI(
    title="YasmineVerse Gateway API",
    description="Moteur centralisé pour toutes les applications de YasmineVerse",
    version="1.0.0"
)

# Configuration CORS (Parfait pour Cloudflare Pages et tes tests locaux)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# MODÈLES PYDANTIC POUR CHAQUE APPLICATION
# ==========================================

# --- CyberShield ---
class PasswordInput(BaseModel):
    password: str = Field(..., min_length=1)

class UrlInput(BaseModel):
    url: str = Field(..., min_length=1)

class EmailInput(BaseModel):
    email_content: Optional[str] = None
    email: Optional[str] = None

# --- EduPredict ML ---
class EduPredictInput(BaseModel):
    # Ajuste ces champs selon les données que ton modèle prend (Exemple : notes, absences...)
    notes: List[float]
    absences: int
    study_hours: float

# --- UniShield ML ---
class UniShieldInput(BaseModel):
    # Ajuste selon ce que ton modèle UniShield réclame
    logs_content: str = Field(..., min_length=1)

# --- Tic-Tac-Toe ---
class TicTacToeInput(BaseModel):
    board: List[str] = Field(..., min_length=9, max_length=9) # Le plateau de 9 cases
    player: str = "O" # Le joueur humain ou le bot

# ==========================================
# ROUTES DE L'API (AIGUILLAGE YASMINEVERSE)
# ==========================================

@app.get("/")
async def index():
    return {
        "status": "online", 
        "project": "YasmineVerse Gateway",
        "modules": ["CyberShield-AI", "EduPredict_ML", "UniShield_ML", "Tic-Tac-Toe"]
    }

# --- 1. ROUTES CYBERSHIELD AI ---
@app.post("/api/cybershield/analyze/password")
async def api_analyze_password(data: PasswordInput):
    return analyze_password(data.password)

@app.post("/api/cybershield/analyze/url")
async def api_analyze_url(data: UrlInput):
    return analyze_url(data.url)

@app.post("/api/cybershield/analyze/email")
async def api_analyze_email(data: EmailInput):
    texte = data.email_content or data.email
    if not texte:
        raise HTTPException(status_code=422, detail="Le contenu de l'email est requis.")
    return analyze_email_text(texte)

# --- 2. ROUTE EDUPREDICT ML ---
@app.post("/api/edupredict/predict")
async def api_edupredict(data: EduPredictInput):
    try:
        # Ici, tu appelles ton vrai modèle de prédiction d'étudiants
        # Exemple : prediction = predict_performance(data.notes, data.absences)
        # En attendant, voici un retour de test :
        return {"prediction": "Pass", "probability": 0.85, "details": "Simulation EduPredict"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 3. ROUTE UNISHIELD ML ---
@app.post("/api/unishield/analyze")
async def api_unishield(data: UniShieldInput):
    try:
        # Ici, tu appelles ton modèle d'analyse UniShield
        return {"status": "secure", "threat_level": "low", "details": "Simulation UniShield"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 4. ROUTE TIC-TAC-TOE (BOT PYTHON) ---
@app.post("/api/tictactoe/play")
async def api_tictactoe(data: TicTacToeInput):
    try:
        # Logique simplifiée pour que le bot joue sur la première case vide disponible
        board = data.board.copy()
        bot_move = -1
        
        for i, cell in enumerate(board):
            if cell == "" or cell == " ":
                board[i] = "X"  # Le bot prend cette case
                bot_move = i
                break
                
        if bot_move == -1:
            return {"status": "draw", "board": board, "bot_move": None}
            
        return {"status": "ongoing", "board": board, "bot_move": bot_move}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

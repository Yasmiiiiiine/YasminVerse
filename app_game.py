# app_game.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
from typing import List

app = FastAPI(
    title="YasmineVerse — Tic-Tac-Toe Engine",
    description="API de logique pour le jeu Tic-Tac-Toe avec adversaire IA/Robot",
    version="1.0.0"
)

# Configuration CORS pour permettre à l'interface de jouer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BoardState(BaseModel):
    board: List[str] # Un tableau de 9 chaînes ("X", "O", ou "")

def verifier_victoire(b: List[str], symbole: str) -> bool:
    # Combinaisons gagnantes du plateau 3x3
    combos = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # Lignes
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # Colonnes
        [0, 4, 8], [2, 4, 6]             # Diagonales
    ]
    return any(all(b[idx] == symbole for idx in combo) for combo in combos)

@app.get("/")
def root():
    return {"status": "ready", "game": "Tic-Tac-Toe Engine", "developer": "Rabia Yasmine"}

@app.post("/play")
def computer_move(state: BoardState):
    board = state.board
    
    # 1. Vérifier si le joueur humain (X) a déjà gagné
    if verifier_victoire(board, "X"):
        return {"status": "gagne_humain", "board": board, "message": "Félicitations, vous avez gagné !"}
        
    # 2. Trouver les cases vides disponibles
    cases_vides = [i for i, cell in enumerate(board) if cell == ""]
    
    # S'il n'y a plus de place et que personne n'a gagné -> Match nul
    if not cases_vides:
        return {"status": "egalite", "board": board, "message": "Match nul !"}
        
    # 3. Logique de l'ordinateur (O) : Choix d'un coup parmi les cases vides
    # L'ordinateur essaie d'abord de gagner s'il a une opportunité
    coup_choisi = None
    for coup in cases_vides:
        copie_board = list(board)
        copie_board[coup] = "O"
        if verifier_victoire(copie_board, "O"):
            coup_choisi = coup
            break
            
    # Sinon, il joue au hasard
    if coup_choisi == None:
        coup_choisi = random.choice(cases_vides)
        
    board[coup_choisi] = "O"
    
    # 4. Vérifier si l'ordinateur a gagné après son coup
    if verifier_victoire(board, "O"):
        return {"status": "gagne_ordinateur", "board": board, "message": "L'ordinateur a gagné ! Recommencez !"}
        
    # Vérifier à nouveau l'égalité s'il s'agissait de la dernière case
    if not [i for i, cell in enumerate(board) if cell == ""]:
        return {"status": "egalite", "board": board, "message": "Match nul !"}
        
    return {"status": "en_cours", "board": board, "message": "À votre tour !"}
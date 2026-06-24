import os
from urllib.parse import urljoin

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


PROJECT_URLS = {
    "cybershield": os.getenv("CYBERSHIELD_URL", "https://cybershield-ai-zb94.onrender.com"),
    "unishield": os.getenv("UNISHIELD_URL", "https://yasmineverse-unishield.onrender.com"),
    "edupredict": os.getenv("EDUPREDICT_URL", "https://edupredict-ml-5sm1.onrender.com"), # MODIFIÉ ICI
    "tictactoe": os.getenv("TICTACTOE_URL", "https://yasmineverse-tictactoe.onrender.com"),
}

app = FastAPI(
    title="YasmineVerse Gateway",
    description="Porte d'entrée FastAPI pour le portfolio et les projets Render de Rabia Yasmine.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")


def get_project_url(project: str) -> str:
    url = PROJECT_URLS.get(project)
    if not url:
        raise HTTPException(status_code=404, detail="Projet introuvable dans YasmineVerse.")
    return url.rstrip("/") + "/"


@app.get("/")
def home():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))


@app.get("/health")
def health():
    return {"status": "online", "service": "YasmineVerse", "projects": list(PROJECT_URLS)}


@app.get("/projects")
def projects():
    return {
        "gateway": "YasmineVerse",
        "routes": {
            name: {
                "open": f"/go/{name}",
                "api": f"/api/{name}/",
                "render": url,
            }
            for name, url in PROJECT_URLS.items()
        },
    }


@app.api_route("/go/{project}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def go_to_project(project: str):
    return RedirectResponse(get_project_url(project), status_code=307)


@app.api_route(
    "/api/{project}/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
def redirect_to_project_api(project: str, path: str, request: Request):
    target = urljoin(get_project_url(project), path)
    if request.url.query:
        target = f"{target}?{request.url.query}"
    return RedirectResponse(target, status_code=307)

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()

@app.get("/cybershield")
async def redirect_cyber():
    return RedirectResponse("https://cybershield-aii.onrender.com")

@app.get("/unishield")
async def redirect_uni():
    return RedirectResponse("https://unishield-ml.onrender.com")

@app.get("/edupredict")
async def redirect_edu():
    return RedirectResponse("https://edupredict-ml-5sm1.onrender.com")

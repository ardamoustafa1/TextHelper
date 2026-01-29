from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router
from app.core.nlp_engine import nlp_engine
import uvicorn
import os

app = FastAPI(
    title="TextHelper Ultimate API",
    description="Enterprise-grade NLP backend for TextHelper",
    version="2.0.0"
)

# CORS - Allow all
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("==================================================")
    print("  TEXTHELPER ULTIMATE - IPHONE INTELLIGENCE MODE  ")
    print("==================================================")
    print("  [INIT] Triggering heavy model loading...")
    await nlp_engine.load_models()
    print("  [OK] User Dictionary Loaded")
    print("  [OK] N-gram Context Engine Active")
    print("  [OK] Hybrid Decision Core Ready")
    print("==================================================")

# Mount Static Files (CSS, JS)
# Assuming run from 'python_backend', and static files are one level up in 'TextHelper'
# We need to serve the parent directory accurately.
# BASE_DIR = c:\Users\ARDA\OneDrive\Masaüstü\TextHelper
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # python_backend
ROOT_DIR = os.path.dirname(BASE_DIR) # TextHelper

print(f"[DEBUG] ROOT_DIR: {ROOT_DIR}")
HTML_PATH = os.path.join(ROOT_DIR, "index_ultimate.html")
print(f"[DEBUG] HTML_PATH: {HTML_PATH}")

app.mount("/css", StaticFiles(directory=os.path.join(ROOT_DIR, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(ROOT_DIR, "js")), name="js")

@app.get("/")
async def read_index():
    if os.path.exists(HTML_PATH):
        return FileResponse(HTML_PATH)
    return {"error": "Index file not found", "path": HTML_PATH}

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    # Disable reload to prevent Windows multiprocessing spawn errors
    print("Starting Server in STABLE COMPATIBILITY MODE...")
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=False)

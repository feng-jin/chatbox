"""FastAPI app entry: routes, static, CORS, init_db."""
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.api.routes_chat import router as chat_router
from backend.app.api.routes_files import router as files_router
from backend.app.api.routes_session import router as session_router
from backend.app.db.database import init_db

app = FastAPI(title="Chatbox API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session_router)
app.include_router(chat_router)
app.include_router(files_router)

@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


# Project root = parent of backend/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
frontend_path = PROJECT_ROOT / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

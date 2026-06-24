from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes.auth import router as auth_router
from app.routes.oauth import router as oauth_router
from app.routes.session import router as session_router
from app.routes.tools import router as tools_router
from app.services.auth_service import init_db

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="Inbound Receptionist Agent", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(oauth_router)
app.include_router(session_router)
app.include_router(tools_router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "timezone": settings.timezone,
        "booking_window_days": settings.booking_window_days,
    }


@app.get("/legacy")
def legacy_ui():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

"""FastAPI application factory and shared path constants."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

ROOT_DIR = Path(__file__).resolve().parent.parent
UI_ENTRY = ROOT_DIR / "soundlab_v2.html"
PARTIALS_DIR = ROOT_DIR / "partials"
CSS_DIR = ROOT_DIR / "css"
JS_DIR = ROOT_DIR / "js"
STATIC_DIR = ROOT_DIR / "static"


def init_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Soundlab Main Server", version="1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    return app

"""
Safety PPE Checker — FastAPI Application Entry Point

Run:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

API Docs:
    http://localhost:8000/docs      (Swagger UI)
    http://localhost:8000/redoc     (ReDoc)
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS, STATIC_DIR
from database import create_tables
from routers import check_ppe, inspections, stats

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-25s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ppe-checker")


# ── Lifespan (startup/shutdown) ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create DB tables. Shutdown: cleanup."""
    logger.info("=" * 50)
    logger.info("🦺 Safety PPE Checker — Starting up...")
    logger.info("=" * 50)

    # Create database tables
    create_tables()
    logger.info("✅ Database tables ready")

    # Ensure static directories exist
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    (STATIC_DIR / "results").mkdir(parents=True, exist_ok=True)
    (STATIC_DIR / "originals").mkdir(parents=True, exist_ok=True)
    logger.info("✅ Static directories ready")

    logger.info("🚀 Server ready! Docs at http://localhost:8000/docs")
    logger.info("=" * 50)

    yield  # App is running

    logger.info("Shutting down...")


# ── FastAPI App ──
app = FastAPI(
    title="Safety PPE Checker API",
    description=(
        "AI-powered PPE compliance checking for electrical workers. "
        "Upload a photo → get instant PASS/FAIL results for 5 PPE items."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static Files (serve annotated images) ──
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ── Routers ──
app.include_router(check_ppe.router)
app.include_router(inspections.router)
app.include_router(stats.router)


# ── Health Check ──
@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "Safety PPE Checker API",
        "status": "running",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

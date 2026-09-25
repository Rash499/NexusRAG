import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from .config import settings
from .routes.ingest import router as ingest_router
from .routes.query import router as query_router
from .routes.system import router as system_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting NexusRAG API service...")
    yield
    logger.info("Shutting down NexusRAG API service...")

app = FastAPI(
    title="NexusRAG API",
    version="2.0.0",
    description="High-performance DevOps-first Retrieval-Augmented Generation API with Modular Services",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        x.strip()
        for x in settings.cors_origins.split(",")
        if x.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics
app.mount("/metrics", make_asgi_app())

# Mount decomposed API routers
app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(system_router)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "NexusRAG API",
        "version": "2.0.0",
    }

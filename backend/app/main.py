"""
JobPulse — Personal Job Market Intelligence Dashboard
Main FastAPI application entry point.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.api import jobs, skills, analytics, profile

# Configure logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="JobPulse API",
        description="Personal Job Market Intelligence Dashboard API",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            settings.frontend_url,
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(jobs.router)
    app.include_router(skills.router)
    app.include_router(analytics.router)
    app.include_router(profile.router)

    @app.on_event("startup")
    async def startup():
        """Initialize database and taxonomy on startup."""
        logger.info("Starting JobPulse API...")
        init_db()
        # Seed canonical skills taxonomy
        from app.database import get_session_factory
        from app.services.job_service import ensure_skills_taxonomy
        session_factory = get_session_factory()
        with session_factory() as session:
            count = ensure_skills_taxonomy(session)
            if count > 0:
                logger.info(f"Seeded {count} canonical taxonomy skills.")
        logger.info("Database and taxonomy initialized.")

    @app.get("/")
    async def root():
        """Root endpoint with quick API reference and documentation links."""
        return {
            "name": "JobPulse API",
            "version": "0.1.0",
            "status": "online",
            "docs_url": "/api/docs",
            "health_url": "/api/health",
            "frontend_url": settings.frontend_url,
        }

    @app.get("/api/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": "0.1.0",
            "application": "JobPulse",
        }

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )

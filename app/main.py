"""
MalsiftCND - Main Application Entry Point
"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import structlog

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging
from app.api.v1.api import api_router
from app.core.middleware import SecurityHeadersMiddleware, RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    setup_logging()
    await init_db()
    logger = structlog.get_logger()
    logger.info("MalsiftCND application started", version=settings.VERSION)
    
    yield
    
    # Shutdown
    logger.info("MalsiftCND application shutting down")


# Create FastAPI application
app = FastAPI(
    title="MalsiftCND",
    description="Enterprise Attack Surface Discovery Tool",
    version=settings.VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Fixed: Use CORS_ORIGINS instead of ALLOWED_HOSTS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

# IMPORTANT: All API routes MUST be defined BEFORE mounting static files
# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.VERSION}


@app.get("/api/status")
async def status():
    """Detailed status endpoint"""
    return {
        "status": "operational",
        "version": settings.VERSION,
        "database": "connected",
        "redis": "connected",
        "scanners": "active"
    }

# Serve static files (if directory exists)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve frontend - MUST be LAST after all API routes  
if os.path.exists("frontend/dist"):
    # Mount static assets
    assets_path = os.path.join("frontend/dist", "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
    
    # Serve root
    @app.get("/", response_class=HTMLResponse)
    async def serve_root():
        index_path = os.path.join("frontend/dist", "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        raise HTTPException(status_code=404)
    
    # Catch-all route handler - serves index.html for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str, request: Request):
        path = request.url.path
        
        # Don't handle API routes or assets
        if path.startswith("/api/") or path.startswith("/assets/"):
            raise HTTPException(status_code=404)
        
        # Try to serve file if exists
        file_path = os.path.join("frontend/dist", full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Serve index.html for React Router
        index_path = os.path.join("frontend/dist", "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        
        raise HTTPException(status_code=404)
elif os.path.exists("static/index.html"):
    # Serve simple login page if no frontend but static directory exists
    @app.get("/", response_class=HTMLResponse)
    async def root_html():
        """Serve login page"""
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
else:
    # Fallback: return API info JSON
    @app.get("/")
    async def root():
        """Root endpoint - API information"""
        docs_url = "/api/docs" if settings.DEBUG else None
        return {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "status": "operational",
            "endpoints": {
                "health": "/health",
                "status": "/api/status",
                "api": "/api/v1",
                "docs": docs_url,
                "redoc": "/api/redoc" if settings.DEBUG else None
            },
            "available_api_routes": [
                "/api/v1/auth",
                "/api/v1/scans",
                "/api/v1/devices",
                "/api/v1/integrations",
                "/api/v1/exports",
                "/api/v1/scheduling",
                "/api/v1/tagging",
                "/api/v1/edr",
                "/api/v1/accuracy",
                "/api/v1/agents",
                "/api/v1/admin"
            ]
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        ssl_keyfile=settings.SSL_KEYFILE,
        ssl_certfile=settings.SSL_CERTFILE
    )

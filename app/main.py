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
from starlette.exceptions import HTTPException as StarletteHTTPException
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
    allow_origins=settings.ALLOWED_HOSTS,
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

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint (must be before frontend mount)
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

# Serve frontend (if directory exists)
if os.path.exists("frontend/dist"):
    # Mount static assets first
    assets_path = os.path.join("frontend/dist", "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
    
    # Serve root index.html
    @app.get("/", response_class=HTMLResponse)
    async def serve_root():
        """Serve React app root"""
        index_path = os.path.join("frontend/dist", "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        raise HTTPException(status_code=404, detail="Frontend not found")
    
    # Custom 404 handler for SPA routing
    @app.exception_handler(StarletteHTTPException)
    async def custom_404_handler(request: Request, exc: StarletteHTTPException):
        """Handle 404s by serving index.html for non-API routes"""
        if exc.status_code == 404:
            path = request.url.path
            
            # Don't serve index.html for API routes, assets, or static files
            if (path.startswith("/api/") or 
                path.startswith("/assets/") or 
                path.startswith("/static/") or
                path.startswith("/health")):
                return JSONResponse(status_code=404, content={"detail": "Not found"})
            
            # Serve index.html for all other 404s (SPA routing)
            index_path = os.path.join("frontend/dist", "index.html")
            if os.path.exists(index_path):
                with open(index_path, "r", encoding="utf-8") as f:
                    return HTMLResponse(content=f.read())
        
        # Re-raise other exceptions
        raise exc
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

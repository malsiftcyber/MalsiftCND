"""
Custom middleware for security and rate limiting
"""
import time
from typing import Dict
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with thread-safe implementation"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: Dict[str, list] = {}
        self.logger = logging.getLogger("middleware.rate_limit")
        # Use threading lock for thread safety
        import threading
        self._lock = threading.Lock()
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        
        # Clean old requests (thread-safe)
        current_time = time.time()
        with self._lock:
            if client_ip in self.clients:
                self.clients[client_ip] = [
                    req_time for req_time in self.clients[client_ip]
                    if current_time - req_time < self.period
                ]
            else:
                self.clients[client_ip] = []
            
            # Check rate limit
            if len(self.clients[client_ip]) >= self.calls:
                self.logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"}
                )
            
            # Add current request
            self.clients[client_ip].append(current_time)
        
        response = await call_next(request)
        return response

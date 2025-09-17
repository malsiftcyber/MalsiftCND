"""
Configuration management for MalsiftCND
"""
import os
from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "MalsiftCND"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str
    
    # Database
    DATABASE_URL: str = "postgresql://malsift:malsift@localhost:5432/malsift"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["*"]
    
    # SSL/TLS
    SSL_KEYFILE: Optional[str] = None
    SSL_CERTFILE: Optional[str] = None
    
    # Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # MFA
    MFA_ISSUER_NAME: str = "MalsiftCND"
    
    # Scanning
    DEFAULT_SCAN_TIMEOUT: int = 300
    MAX_CONCURRENT_SCANS: int = 10
    SCAN_THROTTLE_RATE: int = 100  # requests per second
    
    # AI/LLM APIs
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    # External Integrations
    RUNZERO_API_KEY: Optional[str] = None
    RUNZERO_BASE_URL: str = "https://api.runzero.com/v1.0"
    
    TANIUM_API_KEY: Optional[str] = None
    TANIUM_BASE_URL: Optional[str] = None
    
    ARMIS_API_KEY: Optional[str] = None
    ARMIS_BASE_URL: Optional[str] = None
    
    # Active Directory
    AD_SERVER: Optional[str] = None
    AD_DOMAIN: Optional[str] = None
    AD_USERNAME: Optional[str] = None
    AD_PASSWORD: Optional[str] = None
    
    # Azure AD
    AZURE_TENANT_ID: Optional[str] = None
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # File Storage
    DATA_DIR: str = "./data"
    LOGS_DIR: str = "./logs"
    CERTS_DIR: str = "./certs"
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("JWT_SECRET_KEY")
    def validate_jwt_secret_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

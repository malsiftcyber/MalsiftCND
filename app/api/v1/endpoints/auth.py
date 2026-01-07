"""
Authentication API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta

from app.auth.auth_service import AuthService
from app.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
auth_service = AuthService()


class LoginRequest(BaseModel):
    username: str
    password: str
    auth_type: str = "local"  # local, ad, azure


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_info: dict


class MFASetupResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: list


class MFATokenRequest(BaseModel):
    token: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return access token"""
    user = await auth_service.authenticate_user(
        request.username, 
        request.password, 
        request.auth_type
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user["username"], "user_id": user["id"]},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_info=user
    )


@router.post("/token", response_model=LoginResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 compatible token endpoint"""
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user["username"], "user_id": user["id"]},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_info=user
    )


@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user information"""
    payload = auth_service.verify_token(token)
    username: str = payload.get("sub")
    user_id: str = payload.get("user_id")
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"username": username, "user_id": user_id}


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(token: str = Depends(oauth2_scheme)):
    """Setup MFA for current user"""
    payload = auth_service.verify_token(token)
    username: str = payload.get("sub")
    
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    secret = auth_service.generate_mfa_secret()
    qr_code = auth_service.generate_mfa_qr_code(username, secret)
    backup_codes = auth_service.generate_backup_codes()
    
    # Store secret and backup codes in database
    # This should be implemented with proper database storage
    
    return MFASetupResponse(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )


@router.post("/mfa/verify")
async def verify_mfa(request: MFATokenRequest, token: str = Depends(oauth2_scheme)):
    """Verify MFA token"""
    payload = auth_service.verify_token(token)
    username: str = payload.get("sub")
    
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Get user's MFA secret from database
    from sqlalchemy import text
    from app.core.database import AsyncSessionLocal
    
    user_secret = None
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT mfa_secret FROM users WHERE username = :username"),
            {"username": username}
        )
        row = result.fetchone()
        if row and row.mfa_secret:
            user_secret = row.mfa_secret
    
    if not user_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not set up for this user"
        )
    
    if auth_service.verify_mfa_token(user_secret, request.token):
        return {"verified": True}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA token"
        )


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Logout user (invalidate token)"""
    # In a production system, you would maintain a blacklist of tokens
    # For now, we'll just return success
    return {"message": "Successfully logged out"}

"""
Authentication service supporting local users, AD, and Azure AD
"""
import secrets
import pyotp
import qrcode
from io import BytesIO
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
import logging
import bcrypt

from app.core.config import settings


class AuthService:
    """Authentication service"""
    
    def __init__(self):
        self.logger = logging.getLogger("auth.service")
        # Configure CryptContext - use simple configuration to avoid bug detection issues
        # We'll use bcrypt directly for hashing/verification, but keep passlib as fallback
        try:
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        except Exception as e:
            self.logger.error(f"Failed to initialize CryptContext: {e}")
            # Last resort: use default configuration
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        self.ad_client = None
        self.azure_client = None
        self._initialize_external_auth()
    
    def _initialize_external_auth(self):
        """Initialize external authentication clients"""
        # Active Directory
        if settings.AD_SERVER:
            try:
                from ldap3 import Server, Connection, ALL
                self.ad_server = Server(settings.AD_SERVER, get_info=ALL)
            except ImportError:
                self.logger.warning("ldap3 not available for AD authentication")
        
        # Azure AD
        if settings.AZURE_CLIENT_ID:
            try:
                import msal
                self.azure_client = msal.ConfidentialClientApplication(
                    settings.AZURE_CLIENT_ID,
                    authority=f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}",
                    client_credential=settings.AZURE_CLIENT_SECRET
                )
            except ImportError:
                self.logger.warning("msal not available for Azure AD authentication")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        if not plain_password or not hashed_password:
            self.logger.warning("Empty password or hash provided")
            return False
        
        # Bcrypt has a 72-byte limit - truncate if necessary for verification
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
            self.logger.debug("Password truncated to 72 bytes for verification")
        
        # Use bcrypt directly to avoid passlib bug detection issues
        try:
            # hashed_password should already be a string from the database
            # bcrypt.checkpw expects bytes for both arguments
            hash_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
            result = bcrypt.checkpw(password_bytes, hash_bytes)
            if not result:
                self.logger.debug(f"Password verification failed - hash: {hashed_password[:20]}...")
            return result
        except Exception as e:
            self.logger.error(f"Direct bcrypt verification failed: {e}", exc_info=True)
            # Fallback to passlib if bcrypt direct fails
            try:
                return self.pwd_context.verify(plain_password, hashed_password)
            except Exception as e2:
                self.logger.error(f"Passlib verification also failed: {e2}", exc_info=True)
                return False
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        # Bcrypt has a 72-byte limit - truncate if necessary
        # Encode to bytes to check length
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            # Truncate to 72 bytes
            password_bytes = password_bytes[:72]
        
        # Use bcrypt directly to avoid passlib bug detection issues
        try:
            # Generate salt and hash using bcrypt directly
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password_bytes, salt)
            return hashed.decode('utf-8')
        except Exception as e:
            # Fallback to passlib if bcrypt direct fails
            self.logger.warning(f"Direct bcrypt hashing failed, using passlib: {e}")
            password_str = password_bytes.decode('utf-8', errors='ignore')
            try:
                return self.pwd_context.hash(password_str)
            except ValueError as ve:
                if "password cannot be longer than 72 bytes" in str(ve):
                    # If still too long (shouldn't happen), truncate more aggressively
                    password_str = password_bytes[:72].decode('utf-8', errors='ignore')
                    return self.pwd_context.hash(password_str)
                else:
                    # Re-raise other ValueError exceptions
                    raise
            except Exception as ex:
                # Log and re-raise other exceptions
                self.logger.error(f"Password hashing failed: {ex}", exc_info=True)
                raise
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def authenticate_user(self, username: str, password: str, auth_type: str = "local") -> Optional[Dict[str, Any]]:
        """Authenticate user with specified method"""
        if auth_type == "local":
            return await self._authenticate_local_user(username, password)
        elif auth_type == "ad":
            return await self._authenticate_ad_user(username, password)
        elif auth_type == "azure":
            return await self._authenticate_azure_user(username, password)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid authentication type"
            )
    
    async def _authenticate_local_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate local user"""
        self.logger.info(f"Attempting to authenticate user: {username}")
        
        user = await self._get_local_user(username)
        if not user:
            self.logger.warning(f"User '{username}' not found in database")
            return None
        
        self.logger.info(f"User '{username}' found, checking password...")
        
        # Check if user is active
        if not user.get("is_active", True):
            self.logger.warning(f"User '{username}' is not active")
            return None
        
        password_valid = self.verify_password(password, user["hashed_password"])
        if not password_valid:
            self.logger.warning(f"Password verification failed for user '{username}'")
            return None
        
        self.logger.info(f"Authentication successful for user '{username}'")
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user.get("email"),
            "is_active": user.get("is_active", True),
            "is_admin": user.get("is_admin", False),
            "auth_type": "local"
        }
    
    async def _authenticate_ad_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate Active Directory user"""
        if not self.ad_server:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Active Directory authentication not configured"
            )
        
        try:
            from ldap3 import Connection, ALL_ATTRIBUTES
            
            # Try to bind with user credentials
            conn = Connection(
                self.ad_server,
                user=f"{username}@{settings.AD_DOMAIN}",
                password=password,
                auto_bind=True
            )
            
            # Search for user details
            conn.search(
                search_base=settings.AD_DOMAIN,
                search_filter=f"(sAMAccountName={username})",
                attributes=ALL_ATTRIBUTES
            )
            
            if conn.entries:
                user_entry = conn.entries[0]
                return {
                    "id": str(user_entry.sAMAccountName),
                    "username": str(user_entry.sAMAccountName),
                    "email": str(user_entry.mail) if hasattr(user_entry, 'mail') else None,
                    "display_name": str(user_entry.displayName) if hasattr(user_entry, 'displayName') else username,
                    "is_active": True,
                    "is_admin": self._check_ad_admin_group(user_entry),
                    "auth_type": "ad",
                    "groups": self._extract_ad_groups(user_entry)
                }
            
            conn.unbind()
            return None
            
        except Exception as e:
            self.logger.error(f"AD authentication failed: {e}")
            return None
    
    async def _authenticate_azure_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate Azure AD user"""
        if not self.azure_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Azure AD authentication not configured"
            )
        
        try:
            # This is a simplified example - in practice, you'd use OAuth2 flow
            # For username/password auth, you'd need to implement Resource Owner Password Credentials flow
            
            # Placeholder implementation
            return {
                "id": username,
                "username": username,
                "email": f"{username}@{settings.AZURE_TENANT_ID}",
                "is_active": True,
                "is_admin": False,
                "auth_type": "azure"
            }
            
        except Exception as e:
            self.logger.error(f"Azure AD authentication failed: {e}")
            return None
    
    def _check_ad_admin_group(self, user_entry) -> bool:
        """Check if user is in admin group"""
        # Check if user is member of admin groups
        admin_groups = ["Domain Admins", "Enterprise Admins", "Schema Admins"]
        
        if hasattr(user_entry, 'memberOf'):
            user_groups = [str(group) for group in user_entry.memberOf]
            return any(admin_group in str(user_groups) for admin_group in admin_groups)
        
        return False
    
    def _extract_ad_groups(self, user_entry) -> list:
        """Extract user groups from AD entry"""
        groups = []
        if hasattr(user_entry, 'memberOf'):
            for group in user_entry.memberOf:
                # Extract CN from DN
                cn_start = str(group).find("CN=") + 3
                cn_end = str(group).find(",", cn_start)
                if cn_end == -1:
                    cn_end = len(str(group))
                groups.append(str(group)[cn_start:cn_end])
        return groups
    
    async def _get_local_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get local user from database"""
        from sqlalchemy import select, text
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.core.database import AsyncSessionLocal
        
        try:
            async with AsyncSessionLocal() as session:
                # Use raw SQL to avoid relationship loading issues
                result = await session.execute(
                    text("""
                        SELECT id, username, email, hashed_password, is_active, is_admin, auth_type
                        FROM users
                        WHERE username = :username AND auth_type = 'local'
                    """),
                    {"username": username}
                )
                row = result.fetchone()
                
                if not row:
                    self.logger.debug(f"User '{username}' not found in database")
                    return None
                
                self.logger.debug(f"User '{username}' found: active={row.is_active}, admin={row.is_admin}")
                return {
                    "id": str(row.id),
                    "username": row.username,
                    "email": row.email,
                    "hashed_password": row.hashed_password,
                    "is_active": row.is_active,
                    "is_admin": row.is_admin,
                    "auth_type": row.auth_type or "local"
                }
        except Exception as e:
            self.logger.error(f"Failed to get user from database: {e}", exc_info=True)
            return None
    
    def generate_mfa_secret(self) -> str:
        """Generate MFA secret for user"""
        return pyotp.random_base32()
    
    def generate_mfa_qr_code(self, username: str, secret: str) -> str:
        """Generate QR code for MFA setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=username,
            issuer_name=settings.MFA_ISSUER_NAME
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 string
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        import base64
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_mfa_token(self, secret: str, token: str) -> bool:
        """Verify MFA token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self, count: int = 10) -> list:
        """Generate backup codes for MFA"""
        return [secrets.token_hex(4).upper() for _ in range(count)]

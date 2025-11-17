from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx
from typing import Optional
from config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# HTTP Bearer token scheme
security = HTTPBearer()

# Cache for Azure AD public keys
_jwks_cache: Optional[dict] = None

async def get_azure_public_keys():
    """
    Fetch Azure AD public keys (JWKS) for token validation.
    """
    global _jwks_cache
    
    if _jwks_cache is not None:
        return _jwks_cache
    
    # Try v2.0 endpoint first
    jwks_urls = [
        f"https://login.microsoftonline.com/{settings.azure_ad_tenant_id}/discovery/v2.0/keys",
        f"https://login.microsoftonline.com/{settings.azure_ad_tenant_id}/discovery/keys",  # v1.0 fallback
    ]
    
    async with httpx.AsyncClient() as client:
        for jwks_url in jwks_urls:
            try:
                response = await client.get(jwks_url, timeout=10.0)
                response.raise_for_status()
                _jwks_cache = response.json()
                logger.info(f"Successfully loaded JWKS from {jwks_url}")
                return _jwks_cache
            except Exception as e:
                logger.warning(f"Failed to load JWKS from {jwks_url}: {e}")
                continue
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Unable to fetch Azure AD public keys"
    )

def get_public_key_from_token(token: str, keys: dict):
    """
    Extract the correct public key based on token's kid (key ID).
    """
    try:
        # Decode header without verification to get kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        if not kid:
            raise ValueError("Token header missing 'kid'")
        
        # Find matching key
        for key in keys.get("keys", []):
            if key.get("kid") == kid:
                return key
        
        raise ValueError(f"No matching key found for kid: {kid}")
    except Exception as e:
        logger.error(f"Error extracting public key: {e}")
        raise

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify and decode JWT token from Azure AD.
    Supports both v1.0 and v2.0 tokens.
    """
    token = credentials.credentials
    
    try:
        # Get Azure public keys
        keys = await get_azure_public_keys()
        public_key = get_public_key_from_token(token, keys)
        
        # Decode token header to check version
        unverified_claims = jwt.get_unverified_claims(token)
        
        # Determine expected issuer (support both v1.0 and v2.0)
        iss = unverified_claims.get("iss", "")
        expected_issuers = [
            f"https://login.microsoftonline.com/{settings.azure_ad_tenant_id}/v2.0",  # v2.0
            f"https://sts.windows.net/{settings.azure_ad_tenant_id}/",  # v1.0
        ]
        
        if not any(iss == expected_iss for expected_iss in expected_issuers):
            raise ValueError(f"Invalid issuer: {iss}")
        
        # Verify and decode token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=f"api://{settings.azure_ad_client_id}",
            options={
                "verify_signature": True,
                "verify_aud": True,
                "verify_iat": True,
                "verify_exp": True,
                "verify_iss": False,  # We manually verified issuer above
            }
        )
        
        # Verify tenant
        if payload.get("tid") != settings.azure_ad_tenant_id:
            raise ValueError("Token from wrong tenant")
        
        # Verify scope
        scopes = payload.get("scp", "").split() or payload.get("roles", [])
        if "access_as_user" not in scopes and "access_as_user" not in str(scopes):
            logger.warning(f"Token scopes: {scopes}")
        
        return payload
        
    except JWTError as e:
        logger.error(f"JWT validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token_payload: dict = Depends(verify_token)) -> dict:
    """
    Extract user information from validated token.
    """
    user_info = {
        "user_id": token_payload.get("oid"),
        "email": token_payload.get("preferred_username") or token_payload.get("email") or token_payload.get("upn"),
        "name": token_payload.get("name"),
        "roles": token_payload.get("roles", []),
        "tenant_id": token_payload.get("tid"),
    }
    
    if not user_info["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )
    
    return user_info

# Optional: Role-based authorization
def require_role(required_role: str):
    async def role_checker(user: dict = Depends(get_current_user)):
        if required_role not in user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required role: {required_role}"
            )
        return user
    return role_checker

import httpx
from typing import Optional
import json
import time
import base64

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend

from app.app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)

# Cache JWKS with a simple dict and timestamp
_jwks_cache = {"data": None, "timestamp": 0, "ttl": 3600}  # 1 hour TTL


def _construct_ec_public_key_from_jwk(x: str, y: str):
    """
    Construct an EC public key from JWK x and y coordinates.
    """
    def b64_decode(data):
        padding = 4 - (len(data) % 4)
        return base64.urlsafe_b64decode(data + "=" * padding)
    
    try:
        x_bytes = b64_decode(x)
        y_bytes = b64_decode(y)
    except Exception as e:
        raise ValueError(f"Error decoding base64 coordinates: {str(e)}")
    
    # Construct the point on P-256 curve
    # Point format: 0x04 (uncompressed) + x (32 bytes) + y (32 bytes)
    point_bytes = b'\x04' + x_bytes + y_bytes
    
    # Create EC public key from the point
    try:
        public_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), point_bytes)
    except Exception as e:
        raise ValueError(f"Error creating EC public key: {str(e)}")
    
    # Serialize to PEM format
    from cryptography.hazmat.primitives import serialization
    pem_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem_key.decode("utf-8")


def _get_jwks():
    """
    Fetch the JWKS from Supabase and cache it with TTL.
    Falls back to SUPABASE_JWKS_JSON environment variable if fetch fails.
    """
    current_time = time.time()
    
    # Return cached data if still valid
    if _jwks_cache["data"] and (current_time - _jwks_cache["timestamp"]) < _jwks_cache["ttl"]:
        return _jwks_cache["data"]
    
    # First, check if JWKS is provided via environment variable
    if settings.supabase_jwks_json:
        try:
            print("Loading JWKS from SUPABASE_JWKS_JSON environment variable")
            data = json.loads(settings.supabase_jwks_json)
            _jwks_cache["data"] = data
            _jwks_cache["timestamp"] = current_time
            print(f"Successfully loaded JWKS with {len(data.get('keys', []))} keys from environment")
            return data
        except Exception as e:
            print(f"Error parsing SUPABASE_JWKS_JSON: {str(e)}")
    
    # Try to fetch from the endpoint
    try:
        # Construct JWKS URL from Supabase URL
        base_url = settings.supabase_url.rstrip('/')
        jwks_url = f"{base_url}/auth/v1/jwks"
        
        print(f"Fetching JWKS from: {jwks_url}")
        
        with httpx.Client() as client:
            response = client.get(jwks_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Cache the result
            _jwks_cache["data"] = data
            _jwks_cache["timestamp"] = current_time
            
            print(f"Successfully fetched JWKS with {len(data.get('keys', []))} keys")
            return data
    except Exception as e:
        print(f"Error fetching JWKS from endpoint: {str(e)}")
        
        # Return cached data if available, even if expired
        if _jwks_cache["data"]:
            print("Returning cached JWKS despite fetch error")
            return _jwks_cache["data"]
        
        # Return empty keys
        return {"keys": []}


def _get_key_from_jwks(token: str):
    """
    Extract the kid from the JWT header and find matching key in JWKS.
    Convert JWK to a key object that can be used by jose library.
    """
    try:
        # Get unverified header to extract kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        alg = unverified_header.get("alg")
        
        print(f"Token header - kid: {kid}, alg: {alg}")
        
        if not kid:
            print("Token missing kid (key id)")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing key id (kid)")
        
        # Fetch JWKS
        jwks = _get_jwks()
        print(f"JWKS has {len(jwks.get('keys', []))} keys")
        
        # Find the key with matching kid
        key_data = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                key_data = key
                break
        
        if not key_data:
            available_kids = [k.get("kid") for k in jwks.get("keys", [])]
            print(f"Key not found. Available kids: {available_kids}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Key not found in JWKS")
        
        print(f"Found key with kid: {kid}, kty: {key_data.get('kty')}")
        
        # Convert JWK to PEM format
        if key_data.get("kty") == "EC" and alg == "ES256":
            # For EC keys, reconstruct the public key from x and y coordinates
            x = key_data.get("x")
            y = key_data.get("y")
            
            if not x or not y:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid key data")
            
            try:
                pem_key = _construct_ec_public_key_from_jwk(x, y)
                print(f"Successfully created PEM key from JWK coordinates")
                return pem_key
            except ValueError as e:
                print(f"Error constructing EC public key: {str(e)}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid key format")
        
        elif key_data.get("kty") == "RSA":
            # For RSA keys, use the n and e
            from jose.utils import base64url_decode
            try:
                e = int.from_bytes(base64url_decode(key_data.get("e") + "=="), byteorder="big")
                n = int.from_bytes(base64url_decode(key_data.get("n") + "=="), byteorder="big")
                
                from cryptography.hazmat.primitives.asymmetric import rsa
                public_key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())
                
                from cryptography.hazmat.primitives import serialization
                pem_key = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                return pem_key.decode("utf-8")
            except Exception as e:
                print(f"Error constructing RSA public key: {str(e)}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid RSA key format")
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unsupported key type")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error extracting key from JWKS: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


class CurrentUser:
    def __init__(self, user_id: str, email: Optional[str] = None):
        self.user_id = user_id
        self.email = email


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> CurrentUser:
    if not credentials:
        print("No credentials provided")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing auth token")

    token = credentials.credentials
    try:
        print("Attempting to decode JWT token")
        # Get the key from JWKS
        key = _get_key_from_jwks(token)
        
        print(f"Got key, attempting to verify JWT")
        payload = jwt.decode(
            token,
            key,
            algorithms=["HS256", "HS384", "HS512", "ES256", "RS256"],
            options={
                "verify_aud": False,
                "verify_signature": True
            },
        )
        print(f"JWT decode successful, sub: {payload.get('sub')}")
    except HTTPException:
        raise
    except JWTError as exc:
        print(f"JWT Decode Error: {str(exc)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token") from exc

    sub = payload.get("sub")
    email = payload.get("email")
    if not sub:
        print("No 'sub' claim in token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token payload")

    print(f"User authenticated: {sub}")
    return CurrentUser(user_id=sub, email=email)


def require_user(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return user

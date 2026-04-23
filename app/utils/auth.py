from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from jose import JWTError, jwt
from fastapi import Header, HTTPException, status, Depends
from passlib.context import CryptContext
import os

load_dotenv()

# ─── Configuration ───────────────────────────────────────────────────────────────
SECRET_KEY: str = os.getenv("JWT_SECRET", "dev-only-secret") 
ALGORITHM:   str = os.getenv("JWT_ALGORITHM", "HS256")
TOKEN_TTL_MINUTES: int = int(os.getenv("ID_TOKEN_EXPIRE_MINUTES", 180))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




# ─── Password helpers ────────────────────────────────────────────────────────────
def hash_password(raw: str) -> str:
    return pwd_context.hash(raw)

def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)




# ─── JWT helpers ─────────────────────────────────────────────────────────────────
def create_id_token(data: dict,
                    expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=TOKEN_TTL_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_id_token(token: str) -> Optional[str]:
    """
    Returns the user identifier (sub) if token is valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
    
    
    

# ─── FastAPI dependency to protect routes ────────────────────────────────────────
async def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or improperly formatted",
        )

    token = authorization.split(" ")[1]
    user_email = verify_id_token(token)

    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return user_email
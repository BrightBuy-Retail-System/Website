import os
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from dotenv import load_dotenv

load_dotenv()

# Secret key to sign JWT tokens
raw_secret = os.getenv("SECRET_KEY", "bright-buy-super-secure-jwt-secret-key-32-chars-long")
if len(raw_secret) < 32:
    SECRET_KEY = raw_secret.ljust(32, "0")
else:
    SECRET_KEY = raw_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored bcrypt hash"""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(data: dict) -> str:
    """Generate a signed JWT token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    """Decode and validate a signed JWT token"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None

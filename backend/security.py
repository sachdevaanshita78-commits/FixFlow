
import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from database import get_db
from models import User, UserRole

# Load configuration from backend/.env
load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is missing. Add it to backend/.env"
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 30

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


# 1. Hash a password before saving it to the database
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# 2. Verify a login password against its stored hash
def verify_password(
    password: str,
    hashed_password: str
) -> bool:
    return password_hash.verify(password, hashed_password)


# 3. Create a signed JWT access token
def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user.id),
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
        "iat": now,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# 4. Verify the token and identify the current user
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = UUID(payload["sub"])

    except (
        jwt.InvalidTokenError,
        KeyError,
        ValueError,
        TypeError,
    ):
        raise unauthorized

    user = db.get(User, user_id)

    if user is None:
        raise unauthorized

    return user


# 5. Allow access only to administrators

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in (
        UserRole.admin,
        UserRole.platform_admin,
    ):
        raise HTTPException(
            status_code=403,
            detail="Administrator access required",
        )

    return current_user


# 6. Allow access only to the platform administrator
def require_platform_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.platform_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform administrator access required",
        )

    return current_user

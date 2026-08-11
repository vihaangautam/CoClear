from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import SessionLocal
from . import models

SECRET_KEY = "pgpal-super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme_operator = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/operator/login")
oauth2_scheme_tenant = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/tenant/login")


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_tokens(user_id: UUID, role: str) -> Token:
    access_token = create_access_token({"sub": str(user_id), "role": role})
    refresh_token = create_refresh_token({"sub": str(user_id), "role": role})
    return Token(access_token=access_token, refresh_token=refresh_token)


def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        token_type: str = payload.get("type")
        if user_id is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(sub=user_id, role=role)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_operator(
    token: str = Depends(oauth2_scheme_operator), db: Session = Depends(get_db)
) -> models.Operator:
    token_data = decode_token(token)
    if token_data.role != "operator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized as operator",
        )
    operator = db.query(models.Operator).filter(models.Operator.id == UUID(token_data.sub)).first()
    if operator is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Operator not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return operator


def get_current_tenant(
    token: str = Depends(oauth2_scheme_tenant), db: Session = Depends(get_db)
) -> models.Tenant:
    token_data = decode_token(token)
    if token_data.role != "tenant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized as tenant",
        )
    tenant = db.query(models.Tenant).filter(models.Tenant.id == UUID(token_data.sub)).first()
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return tenant


def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_operator), db: Session = Depends(get_db)
):
    if not token:
        return None
    try:
        return get_current_operator(token, db)
    except HTTPException:
        try:
            return get_current_tenant(token, db)
        except HTTPException:
            return None
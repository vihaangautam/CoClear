from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from pydantic import BaseModel

from ..database import SessionLocal
from .. import models, schemas
from ..auth import (
    verify_password,
    get_password_hash,
    create_tokens,
    get_current_operator,
    get_current_tenant,
    get_db,
    decode_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class OperatorRegister(BaseModel):
    name: str
    email: str
    phone: str
    password: str


class TenantRegister(BaseModel):
    name: str
    phone: str
    password: str
    email: Optional[str] = None
    aadhaar_last4: Optional[str] = None


class TenantLogin(BaseModel):
    phone: str
    password: str


@router.post("/operator/register", response_model=schemas.Token, status_code=201)
def register_operator(data: OperatorRegister, db: Session = Depends(get_db)):
    existing = db.query(models.Operator).filter(models.Operator.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    operator = models.Operator(
        name=data.name,
        email=data.email,
        phone=data.phone,
        password_hash=get_password_hash(data.password),
    )
    db.add(operator)
    db.commit()
    db.refresh(operator)
    return create_tokens(operator.id, "operator")


@router.post("/operator/login", response_model=schemas.Token)
def login_operator(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    operator = db.query(models.Operator).filter(models.Operator.email == form_data.username).first()
    if not operator or not operator.password_hash or not verify_password(form_data.password, operator.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_tokens(operator.id, "operator")


@router.post("/tenant/register", response_model=schemas.Token, status_code=201)
def register_tenant(data: TenantRegister, db: Session = Depends(get_db)):
    existing = db.query(models.Tenant).filter(models.Tenant.phone == data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    tenant = models.Tenant(
        name=data.name,
        phone=data.phone,
        email=data.email,
        aadhaar_last4=data.aadhaar_last4,
        password_hash=get_password_hash(data.password),
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return create_tokens(tenant.id, "tenant")


@router.post("/tenant/login", response_model=schemas.Token)
def login_tenant(data: TenantLogin, db: Session = Depends(get_db)):
    tenant = db.query(models.Tenant).filter(models.Tenant.phone == data.phone).first()
    if not tenant or not tenant.password_hash or not verify_password(data.password, tenant.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_tokens(tenant.id, "tenant")


@router.post("/refresh", response_model=schemas.Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    token_data = decode_token(refresh_token)
    if token_data.role == "operator":
        user = db.query(models.Operator).filter(models.Operator.id == UUID(token_data.sub)).first()
    else:
        user = db.query(models.Tenant).filter(models.Tenant.id == UUID(token_data.sub)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return create_tokens(user.id, token_data.role)


@router.get("/operator/me", response_model=schemas.OperatorOut)
def get_operator_me(current_operator: models.Operator = Depends(get_current_operator)):
    return current_operator


@router.get("/tenant/me", response_model=schemas.TenantOut)
def get_tenant_me(current_tenant: models.Tenant = Depends(get_current_tenant)):
    return current_tenant
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from .. import models, schemas
from ..auth import get_current_operator, get_db

router = APIRouter()


@router.get("/tenancies/{tenancy_id}/payments", response_model=list[schemas.PaymentOut])
def list_payments(
    tenancy_id: UUID,
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    tenancy = db.query(models.Tenancy).filter(
        models.Tenancy.id == tenancy_id,
        models.Tenancy.operator_id == current_operator.id,
    ).first()
    if not tenancy:
        raise HTTPException(status_code=404, detail="Tenancy not found")
    return (
        db.query(models.Payment)
        .filter(models.Payment.tenancy_id == tenancy_id)
        .order_by(models.Payment.payment_date.desc())
        .all()
    )


@router.post("/tenancies/{tenancy_id}/payments", response_model=schemas.PaymentOut, status_code=201)
def create_payment(
    tenancy_id: UUID,
    data: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    tenancy = db.query(models.Tenancy).filter(
        models.Tenancy.id == tenancy_id,
        models.Tenancy.operator_id == current_operator.id,
    ).first()
    if not tenancy:
        raise HTTPException(status_code=404, detail="Tenancy not found")

    payment = models.Payment(
        tenancy_id=tenancy_id,
        amount=data.amount,
        payment_date=data.payment_date,
        method=data.method,
        reference=data.reference,
        note=data.note,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
"""
Tenant-facing API endpoints.
Tenants look up their tenancy by phone number (MVP: no JWT auth).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from typing import List
from ..database import SessionLocal
from .. import models, schemas

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/tenant/lookup")
def tenant_lookup(phone: str, db: Session = Depends(get_db)):
    """Look up a tenant and their active tenancies by phone number."""
    tenant = db.query(models.Tenant).filter(models.Tenant.phone == phone).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="No tenant found with this phone number")

    tenancies = (
        db.query(models.Tenancy)
        .options(joinedload(models.Tenancy.tenant), joinedload(models.Tenancy.bed))
        .filter(models.Tenancy.tenant_id == tenant.id)
        .all()
    )

    return {
        "tenant": {
            "id": str(tenant.id),
            "name": tenant.name,
            "email": tenant.email,
            "phone": tenant.phone,
        },
        "tenancies": [
            {
                "id": str(t.id),
                "status": t.status.value if hasattr(t.status, 'value') else t.status,
                "rent_amount": str(t.rent_amount),
                "deposit_amount": str(t.deposit_amount),
                "move_in_date": str(t.move_in_date) if t.move_in_date else None,
                "bed_label": t.bed.label if t.bed else None,
            }
            for t in tenancies
        ],
    }


@router.get("/tenant/tenancies/{tenancy_id}/tickets", response_model=List[schemas.TicketOut])
def tenant_get_tickets(tenancy_id: UUID, db: Session = Depends(get_db)):
    """Tenant views their own tickets for a specific tenancy."""
    return (
        db.query(models.Ticket)
        .filter(models.Ticket.tenancy_id == tenancy_id)
        .order_by(models.Ticket.created_at.desc())
        .all()
    )

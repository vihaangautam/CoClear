"""
Tenant-facing API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from typing import List
from .. import models, schemas
from ..auth import get_current_tenant, get_db

router = APIRouter()


@router.get("/tenant/lookup")
def tenant_lookup(phone: str, db: Session = Depends(get_db)):
    """Look up a tenant and their active tenancies by phone number (for initial login)."""
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


@router.get("/tenant/me", response_model=schemas.TenantOut)
def get_tenant_me(current_tenant: models.Tenant = Depends(get_current_tenant)):
    """Get current authenticated tenant's profile."""
    return current_tenant


@router.get("/tenant/tenancies", response_model=List[schemas.TenancyOut])
def get_tenant_tenancies(
    db: Session = Depends(get_db),
    current_tenant: models.Tenant = Depends(get_current_tenant),
):
    """Get all tenancies for the authenticated tenant."""
    return (
        db.query(models.Tenancy)
        .options(joinedload(models.Tenancy.tenant), joinedload(models.Tenancy.bed))
        .filter(models.Tenancy.tenant_id == current_tenant.id)
        .all()
    )


@router.get("/tenant/tenancies/{tenancy_id}/tickets", response_model=List[schemas.TicketOut])
def tenant_get_tickets(
    tenancy_id: UUID,
    db: Session = Depends(get_db),
    current_tenant: models.Tenant = Depends(get_current_tenant),
):
    """Tenant views their own tickets for a specific tenancy."""
    tenancy = db.query(models.Tenancy).filter(
        models.Tenancy.id == tenancy_id,
        models.Tenancy.tenant_id == current_tenant.id,
    ).first()
    if not tenancy:
        raise HTTPException(status_code=404, detail="Tenancy not found")

    return (
        db.query(models.Ticket)
        .filter(models.Ticket.tenancy_id == tenancy_id)
        .order_by(models.Ticket.created_at.desc())
        .all()
    )


@router.post("/tenant/tenancies/{tenancy_id}/tickets", response_model=schemas.TicketOut, status_code=201)
def tenant_create_ticket(
    tenancy_id: UUID,
    body: schemas.TicketCreate,
    db: Session = Depends(get_db),
    current_tenant: models.Tenant = Depends(get_current_tenant),
):
    """Tenant creates a new ticket/complaint."""
    tenancy = db.query(models.Tenancy).filter(
        models.Tenancy.id == tenancy_id,
        models.Tenancy.tenant_id == current_tenant.id,
    ).first()
    if not tenancy:
        raise HTTPException(status_code=404, detail="Tenancy not found")

    ticket = models.Ticket(
        tenancy_id=tenancy_id,
        title=body.title,
        description=body.description,
        priority=body.priority or models.TicketPriority.medium,
        status=models.TicketStatus.open
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/tenant/tenancies/{tenancy_id}/condition-report/{report_type}", response_model=schemas.ConditionReportOut)
def tenant_get_condition_report(
    tenancy_id: UUID,
    report_type: str,
    db: Session = Depends(get_db),
    current_tenant: models.Tenant = Depends(get_current_tenant),
):
    """Tenant views their condition report."""
    tenancy = db.query(models.Tenancy).filter(
        models.Tenancy.id == tenancy_id,
        models.Tenancy.tenant_id == current_tenant.id,
    ).first()
    if not tenancy:
        raise HTTPException(status_code=404, detail="Tenancy not found")

    report = (
        db.query(models.ConditionReport)
        .options(joinedload(models.ConditionReport.items))
        .filter(
            models.ConditionReport.tenancy_id == tenancy_id,
            models.ConditionReport.report_type == report_type,
        )
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Condition report not found")
    return report


@router.post("/tenant/condition-reports/{report_id}/sign", response_model=schemas.ConditionReportOut)
def tenant_sign_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_tenant: models.Tenant = Depends(get_current_tenant),
):
    """Tenant signs a condition report."""
    report = (
        db.query(models.ConditionReport)
        .options(joinedload(models.ConditionReport.items))
        .join(models.Tenancy)
        .filter(
            models.ConditionReport.id == report_id,
            models.Tenancy.tenant_id == current_tenant.id,
        )
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.is_locked:
        raise HTTPException(status_code=400, detail="Report is already locked.")

    report.signed_by_tenant = True

    # Lock when both have signed
    if report.signed_by_operator and report.signed_by_tenant:
        report.is_locked = True
        from datetime import datetime, timezone
        report.signed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(report)
    return report


@router.get("/tenant/tenancies/{tenancy_id}/payments", response_model=List[schemas.PaymentOut])
def tenant_get_payments(
    tenancy_id: UUID,
    db: Session = Depends(get_db),
    current_tenant: models.Tenant = Depends(get_current_tenant),
):
    """Tenant views their payment history."""
    tenancy = db.query(models.Tenancy).filter(
        models.Tenancy.id == tenancy_id,
        models.Tenancy.tenant_id == current_tenant.id,
    ).first()
    if not tenancy:
        raise HTTPException(status_code=404, detail="Tenancy not found")

    return (
        db.query(models.Payment)
        .filter(models.Payment.tenancy_id == tenancy_id)
        .order_by(models.Payment.payment_date.desc())
        .all()
    )
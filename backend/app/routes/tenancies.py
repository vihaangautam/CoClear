from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from .. import models, schemas
from ..auth import get_current_operator, get_db

router = APIRouter()

# Valid state transitions per the PRD state machine
VALID_TRANSITIONS = {
    "inquiry": ["confirmed", "cancelled"],
    "confirmed": ["active", "cancelled"],
    "active": ["notice_period"],
    "notice_period": ["vacated"],
}


@router.get("/tenancies", response_model=list[schemas.TenancyOut])
def list_tenancies(
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    return (
        db.query(models.Tenancy)
        .options(joinedload(models.Tenancy.tenant), joinedload(models.Tenancy.bed))
        .filter(models.Tenancy.operator_id == current_operator.id)
        .all()
    )


@router.post("/tenancies", response_model=schemas.TenancyOut, status_code=201)
def create_tenancy(
    data: schemas.TenancyCreate,
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    # Verify bed belongs to operator's property
    bed = db.query(models.Bed).join(models.Room).join(models.Property).filter(
        models.Bed.id == data.bed_id,
        models.Property.operator_id == current_operator.id,
    ).first()
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")

    tenancy = models.Tenancy(
        bed_id=data.bed_id,
        tenant_id=data.tenant_id,
        operator_id=current_operator.id,
        status=models.TenancyStatus.inquiry,
        rent_amount=data.rent_amount,
        rent_due_day=data.rent_due_day,
        deposit_amount=data.deposit_amount,
        move_in_date=data.move_in_date,
    )
    db.add(tenancy)
    db.commit()
    db.refresh(tenancy)
    return tenancy


@router.get("/tenancies/{tenancy_id}", response_model=schemas.TenancyOut)
def get_tenancy(
    tenancy_id: UUID,
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    tenancy = (
        db.query(models.Tenancy)
        .options(joinedload(models.Tenancy.tenant), joinedload(models.Tenancy.bed))
        .filter(
            models.Tenancy.id == tenancy_id,
            models.Tenancy.operator_id == current_operator.id,
        )
        .first()
    )
    if not tenancy:
        raise HTTPException(status_code=404, detail="Tenancy not found")
    return tenancy


@router.patch("/tenancies/{tenancy_id}/transition", response_model=schemas.TenancyOut)
def transition_tenancy(
    tenancy_id: UUID,
    body: schemas.TenancyTransition,
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    tenancy = db.query(models.Tenancy).filter(
        models.Tenancy.id == tenancy_id,
        models.Tenancy.operator_id == current_operator.id,
    ).first()
    if not tenancy:
        raise HTTPException(status_code=404, detail="Tenancy not found")

    current = tenancy.status.value if hasattr(tenancy.status, 'value') else tenancy.status
    target = body.to.value

    # Validate transition
    allowed = VALID_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition: {current} → {target}. Allowed: {allowed}"
        )

    # Gate: confirmed → active requires signed check-in report
    if current == "confirmed" and target == "active":
        report = db.query(models.ConditionReport).filter(
            models.ConditionReport.tenancy_id == tenancy_id,
            models.ConditionReport.report_type == "check_in",
            models.ConditionReport.is_locked == True,
        ).first()
        if not report:
            raise HTTPException(
                status_code=400,
                detail="Cannot activate tenancy without a signed check-in condition report"
            )

    # Log the transition
    log = models.TenancyStatusLog(
        tenancy_id=tenancy_id,
        from_status=current,
        to_status=target,
    )
    db.add(log)

    tenancy.status = target
    db.commit()
    db.refresh(tenancy)
    return tenancy
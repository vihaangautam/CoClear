from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from datetime import datetime, timezone
from .. import models, schemas
from ..auth import get_current_operator, get_current_tenant, get_db

router = APIRouter()


@router.post("/tenancies/{tenancy_id}/condition-report", response_model=schemas.ConditionReportOut, status_code=201)
def create_condition_report(
    tenancy_id: UUID,
    body: schemas.ConditionReportCreate,
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    tenancy = db.query(models.Tenancy).filter(
        models.Tenancy.id == tenancy_id,
        models.Tenancy.operator_id == current_operator.id,
    ).first()
    if not tenancy:
        raise HTTPException(status_code=404, detail="Tenancy not found")

    # Check if report of this type already exists
    existing = db.query(models.ConditionReport).filter(
        models.ConditionReport.tenancy_id == tenancy_id,
        models.ConditionReport.report_type == body.report_type,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"{body.report_type} report already exists for this tenancy")

    report = models.ConditionReport(
        tenancy_id=tenancy_id,
        report_type=body.report_type,
    )
    db.add(report)
    db.commit()

    # Auto-populate the default checklist items
    default_items = [
        "Walls", "Floor", "Ceiling", "Bed Frame", "Mattress",
        "Wardrobe/Almirah", "Table & Chair", "AC", "Geyser",
        "Bathroom Fittings", "Window/Door",
    ]
    for item_name in default_items:
        item = models.ConditionItem(report_id=report.id, item_name=item_name)
        db.add(item)
    db.commit()
    db.refresh(report)
    return report


@router.get("/tenancies/{tenancy_id}/condition-report/{report_type}", response_model=schemas.ConditionReportOut)
def get_condition_report(
    tenancy_id: UUID,
    report_type: str,
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    tenancy = db.query(models.Tenancy).filter(
        models.Tenancy.id == tenancy_id,
        models.Tenancy.operator_id == current_operator.id,
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


@router.put("/condition-reports/{report_id}/items/{item_id}", response_model=schemas.ConditionItemOut)
def update_condition_item(
    report_id: UUID,
    item_id: UUID,
    body: schemas.ConditionItemCreate,
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    report = db.query(models.ConditionReport).join(models.Tenancy).filter(
        models.ConditionReport.id == report_id,
        models.Tenancy.operator_id == current_operator.id,
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.is_locked:
        raise HTTPException(status_code=400, detail="Report is locked. No edits permitted after signing.")

    item = db.query(models.ConditionItem).filter(
        models.ConditionItem.id == item_id,
        models.ConditionItem.report_id == report_id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.condition = body.condition
    item.notes = body.notes
    item.photo_url = body.photo_url
    item.deduction_amount = body.deduction_amount
    db.commit()
    db.refresh(item)
    return item


@router.post("/condition-reports/{report_id}/sign", response_model=schemas.ConditionReportOut)
def sign_report(
    report_id: UUID,
    role: str = "operator",
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    """Sign the report. role = 'operator' or 'tenant'. Locks when both sign."""
    report = (
        db.query(models.ConditionReport)
        .options(joinedload(models.ConditionReport.items))
        .join(models.Tenancy)
        .filter(
            models.ConditionReport.id == report_id,
            models.Tenancy.operator_id == current_operator.id,
        )
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.is_locked:
        raise HTTPException(status_code=400, detail="Report is already locked.")

    if role == "operator":
        report.signed_by_operator = True
    elif role == "tenant":
        report.signed_by_tenant = True
    else:
        raise HTTPException(status_code=400, detail="role must be 'operator' or 'tenant'")

    # Lock when both have signed
    if report.signed_by_operator and report.signed_by_tenant:
        report.is_locked = True
        report.signed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(report)
    return report


@router.get("/tenancies/{tenancy_id}/condition-report/diff")
def get_condition_diff(
    tenancy_id: UUID,
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    """Side-by-side diff of check-in vs check-out condition items."""
    tenancy = db.query(models.Tenancy).filter(
        models.Tenancy.id == tenancy_id,
        models.Tenancy.operator_id == current_operator.id,
    ).first()
    if not tenancy:
        raise HTTPException(status_code=404, detail="Tenancy not found")

    check_in = (
        db.query(models.ConditionReport)
        .options(joinedload(models.ConditionReport.items))
        .filter(
            models.ConditionReport.tenancy_id == tenancy_id,
            models.ConditionReport.report_type == "check_in",
        )
        .first()
    )
    check_out = (
        db.query(models.ConditionReport)
        .options(joinedload(models.ConditionReport.items))
        .filter(
            models.ConditionReport.tenancy_id == tenancy_id,
            models.ConditionReport.report_type == "check_out",
        )
        .first()
    )

    if not check_in or not check_out:
        raise HTTPException(status_code=404, detail="Both check-in and check-out reports are required for diff")

    # Build diff by item name
    in_items = {item.item_name: item for item in check_in.items}
    out_items = {item.item_name: item for item in check_out.items}

    diff = []
    for name in in_items:
        ci = in_items.get(name)
        co = out_items.get(name)
        diff.append({
            "item_name": name,
            "check_in_condition": ci.condition.value if ci and ci.condition else None,
            "check_in_photo": ci.photo_url if ci else None,
            "check_in_notes": ci.notes if ci else None,
            "check_out_condition": co.condition.value if co and co.condition else None,
            "check_out_photo": co.photo_url if co else None,
            "check_out_notes": co.notes if co else None,
            "changed": (ci.condition != co.condition) if ci and co and ci.condition and co.condition else False,
            "deduction_amount": str(co.deduction_amount) if co and co.deduction_amount else None,
        })

    return {"tenancy_id": str(tenancy_id), "diff": diff}
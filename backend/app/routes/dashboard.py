from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc
from decimal import Decimal
from datetime import date
from ..database import SessionLocal
from .. import models, schemas

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dashboard/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_properties = db.query(models.Property).count()
    total_beds = db.query(models.Bed).count()
    active_tenancies = db.query(models.Tenancy).filter(
        models.Tenancy.status == models.TenancyStatus.active
    ).count()
    occupancy = (active_tenancies / total_beds * 100) if total_beds > 0 else 0

    # Revenue this month
    today = date.today()
    first_of_month = today.replace(day=1)
    revenue = db.query(sqlfunc.coalesce(sqlfunc.sum(models.Payment.amount), 0)).filter(
        models.Payment.payment_date >= first_of_month
    ).scalar()

    notice_count = db.query(models.Tenancy).filter(
        models.Tenancy.status == models.TenancyStatus.notice_period
    ).count()

    return schemas.DashboardStats(
        total_properties=total_properties,
        total_beds=total_beds,
        active_tenancies=active_tenancies,
        occupancy_percent=round(occupancy, 1),
        total_revenue_mtd=Decimal(str(revenue)),
        tenancies_in_notice=notice_count,
    )


@router.get("/dashboard/occupancy", response_model=list[schemas.PropertyOccupancy])
def get_occupancy_grid(db: Session = Depends(get_db)):
    properties = db.query(models.Property).all()
    result = []

    for prop in properties:
        beds_data = []
        total = 0
        occupied = 0
        for room in prop.rooms:
            for bed in room.beds:
                total += 1
                # Find the current tenancy for this bed (not vacated/cancelled)
                tenancy = db.query(models.Tenancy).filter(
                    models.Tenancy.bed_id == bed.id,
                    models.Tenancy.status.notin_([
                        models.TenancyStatus.vacated,
                        models.TenancyStatus.cancelled,
                    ])
                ).first()
                status = tenancy.status if tenancy else None
                tenant_name = None
                if tenancy and tenancy.tenant:
                    tenant_name = tenancy.tenant.name
                    occupied += 1
                beds_data.append(schemas.OccupancyBed(
                    bed_id=bed.id,
                    label=bed.label,
                    room_number=room.room_number,
                    status=status,
                    tenant_name=tenant_name,
                ))

        occ_pct = (occupied / total * 100) if total > 0 else 0
        result.append(schemas.PropertyOccupancy(
            property_id=prop.id,
            property_name=prop.name,
            address=prop.address,
            occupancy_percent=round(occ_pct, 1),
            beds=beds_data,
        ))

    return result

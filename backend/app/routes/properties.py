from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from .. import models, schemas
from ..auth import get_current_operator, get_db

router = APIRouter()


# ─── Properties ──────────────────────────────────────────────────

@router.get("/properties", response_model=list[schemas.PropertyOut])
def list_properties(
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    return db.query(models.Property).filter(models.Property.operator_id == current_operator.id).all()


@router.post("/properties", response_model=schemas.PropertyOut, status_code=201)
def create_property(
    data: schemas.PropertyCreate,
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    prop = models.Property(
        operator_id=current_operator.id,
        name=data.name,
        address=data.address,
        type=data.type,
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


@router.get("/properties/{property_id}", response_model=schemas.PropertyOut)
def get_property(
    property_id: UUID,
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    prop = db.query(models.Property).filter(
        models.Property.id == property_id,
        models.Property.operator_id == current_operator.id,
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


# ─── Rooms ───────────────────────────────────────────────────────

@router.get("/properties/{property_id}/rooms", response_model=list[schemas.RoomOut])
def list_rooms(
    property_id: UUID,
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    prop = db.query(models.Property).filter(
        models.Property.id == property_id,
        models.Property.operator_id == current_operator.id,
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return db.query(models.Room).filter(models.Room.property_id == property_id).all()


@router.post("/properties/{property_id}/rooms", response_model=schemas.RoomOut, status_code=201)
def create_room(
    property_id: UUID,
    data: schemas.RoomCreate,
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    prop = db.query(models.Property).filter(
        models.Property.id == property_id,
        models.Property.operator_id == current_operator.id,
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    room = models.Room(
        property_id=property_id,
        room_number=data.room_number,
        floor=data.floor,
        total_beds=data.total_beds,
    )
    db.add(room)
    db.commit()
    db.refresh(room)

    # Auto-create beds
    for i in range(1, data.total_beds + 1):
        bed = models.Bed(room_id=room.id, label=f"{data.room_number}{chr(64 + i)}")
        db.add(bed)
    db.commit()
    db.refresh(room)
    return room


# ─── Beds ────────────────────────────────────────────────────────

@router.post("/rooms/{room_id}/beds", response_model=schemas.BedOut, status_code=201)
def create_bed(
    room_id: UUID,
    data: schemas.BedCreate,
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    room = db.query(models.Room).join(models.Property).filter(
        models.Room.id == room_id,
        models.Property.operator_id == current_operator.id,
    ).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    bed = models.Bed(room_id=room_id, label=data.label)
    db.add(bed)
    db.commit()
    db.refresh(bed)
    return bed


# ─── Tenants ─────────────────────────────────────────────────────

@router.get("/tenants", response_model=list[schemas.TenantOut])
def list_tenants(
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    return db.query(models.Tenant).join(models.Tenancy).filter(
        models.Tenancy.operator_id == current_operator.id
    ).distinct().all()


@router.post("/tenants", response_model=schemas.TenantOut, status_code=201)
def create_tenant(
    data: schemas.TenantCreate,
    db: Session = Depends(get_db),
    current_operator: models.Operator = Depends(get_current_operator),
):
    tenant = models.Tenant(
        name=data.name,
        email=data.email,
        phone=data.phone,
        aadhaar_last4=data.aadhaar_last4,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant
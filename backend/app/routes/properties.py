from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from ..database import SessionLocal
from .. import models, schemas

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── Properties ──────────────────────────────────────────────────

@router.get("/properties", response_model=list[schemas.PropertyOut])
def list_properties(db: Session = Depends(get_db)):
    return db.query(models.Property).all()


@router.post("/properties", response_model=schemas.PropertyOut, status_code=201)
def create_property(data: schemas.PropertyCreate, db: Session = Depends(get_db)):
    # For MVP, use first operator
    operator = db.query(models.Operator).first()
    if not operator:
        raise HTTPException(status_code=400, detail="No operator found. Seed the database first.")
    prop = models.Property(
        operator_id=operator.id,
        name=data.name,
        address=data.address,
        type=data.type,
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


@router.get("/properties/{property_id}", response_model=schemas.PropertyOut)
def get_property(property_id: UUID, db: Session = Depends(get_db)):
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


# ─── Rooms ───────────────────────────────────────────────────────

@router.get("/properties/{property_id}/rooms", response_model=list[schemas.RoomOut])
def list_rooms(property_id: UUID, db: Session = Depends(get_db)):
    return db.query(models.Room).filter(models.Room.property_id == property_id).all()


@router.post("/properties/{property_id}/rooms", response_model=schemas.RoomOut, status_code=201)
def create_room(property_id: UUID, data: schemas.RoomCreate, db: Session = Depends(get_db)):
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
def create_bed(room_id: UUID, data: schemas.BedCreate, db: Session = Depends(get_db)):
    bed = models.Bed(room_id=room_id, label=data.label)
    db.add(bed)
    db.commit()
    db.refresh(bed)
    return bed


# ─── Tenants ─────────────────────────────────────────────────────

@router.get("/tenants", response_model=list[schemas.TenantOut])
def list_tenants(db: Session = Depends(get_db)):
    return db.query(models.Tenant).all()


@router.post("/tenants", response_model=schemas.TenantOut, status_code=201)
def create_tenant(data: schemas.TenantCreate, db: Session = Depends(get_db)):
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

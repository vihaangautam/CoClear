from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from typing import List, Optional
from ..database import SessionLocal
from .. import models, schemas

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/tickets", response_model=List[schemas.TicketOut])
def get_tickets(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Ticket)
    if status:
        query = query.filter(models.Ticket.status == status)
    return query.order_by(models.Ticket.created_at.desc()).all()

@router.post("/tenancies/{tenancy_id}/tickets", response_model=schemas.TicketOut, status_code=201)
def create_ticket(tenancy_id: UUID, body: schemas.TicketCreate, db: Session = Depends(get_db)):
    tenancy = db.query(models.Tenancy).filter(models.Tenancy.id == tenancy_id).first()
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

@router.patch("/tickets/{ticket_id}", response_model=schemas.TicketOut)
def update_ticket(ticket_id: UUID, body: schemas.TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    if body.status is not None:
        ticket.status = body.status
    if body.priority is not None:
        ticket.priority = body.priority
        
    db.commit()
    db.refresh(ticket)
    return ticket

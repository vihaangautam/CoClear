import uuid
import enum
from sqlalchemy import Column, String, Integer, Numeric, Boolean, Date, DateTime, Text, ForeignKey, Enum as SQLEnum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class TenancyStatus(str, enum.Enum):
    inquiry = "inquiry"
    confirmed = "confirmed"
    active = "active"
    notice_period = "notice_period"
    vacated = "vacated"
    cancelled = "cancelled"


class PaymentMethod(str, enum.Enum):
    upi = "upi"
    cash = "cash"
    bank_transfer = "bank_transfer"
    other = "other"


class ConditionRating(str, enum.Enum):
    good = "good"
    fair = "fair"
    damaged = "damaged"
    missing = "missing"


class TicketStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"


class TicketPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


# ─── Core Entity Models ────────────────────────────────────────────

class Operator(Base):
    __tablename__ = "operators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    password_hash = Column(String, nullable=True)  # For auth (MVP: optional)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    properties = relationship("Property", back_populates="operator", cascade="all, delete-orphan")
    tenancies = relationship("Tenancy", back_populates="operator")


class Property(Base):
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operator_id = Column(UUID(as_uuid=True), ForeignKey("operators.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'men', 'women', 'mixed'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    operator = relationship("Operator", back_populates="properties")
    rooms = relationship("Room", back_populates="property", cascade="all, delete-orphan")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"))
    room_number = Column(String, nullable=False)
    floor = Column(Integer)
    total_beds = Column(Integer, nullable=False, default=1)

    property = relationship("Property", back_populates="rooms")
    beds = relationship("Bed", back_populates="room", cascade="all, delete-orphan")


class Bed(Base):
    __tablename__ = "beds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE"))
    label = Column(String, nullable=False, default="Bed 1")

    room = relationship("Room", back_populates="beds")
    tenancies = relationship("Tenancy", back_populates="bed")


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
    phone = Column(String, nullable=False)
    aadhaar_last4 = Column(String(4))
    password_hash = Column(String, nullable=True)  # For tenant portal auth
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenancies = relationship("Tenancy", back_populates="tenant")


# ─── Tenancy + State Machine ──────────────────────────────────────

class Tenancy(Base):
    __tablename__ = "tenancies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bed_id = Column(UUID(as_uuid=True), ForeignKey("beds.id"))
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    operator_id = Column(UUID(as_uuid=True), ForeignKey("operators.id"))
    status = Column(SQLEnum(TenancyStatus), nullable=False, default=TenancyStatus.inquiry)
    rent_amount = Column(Numeric(10, 2), nullable=False)
    rent_due_day = Column(Integer)
    deposit_amount = Column(Numeric(10, 2), nullable=False, default=0)
    deposit_refunded = Column(Numeric(10, 2))
    move_in_date = Column(Date)
    notice_given_date = Column(Date)
    vacating_date = Column(Date)
    vacated_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    bed = relationship("Bed", back_populates="tenancies")
    tenant = relationship("Tenant", back_populates="tenancies")
    operator = relationship("Operator", back_populates="tenancies")
    condition_reports = relationship("ConditionReport", back_populates="tenancy", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="tenancy", cascade="all, delete-orphan")


# ─── Condition Reports (Core Feature) ─────────────────────────────

class ConditionReport(Base):
    __tablename__ = "condition_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenancy_id = Column(UUID(as_uuid=True), ForeignKey("tenancies.id"))
    report_type = Column(String, nullable=False)  # 'check_in' or 'check_out'
    signed_by_operator = Column(Boolean, default=False)
    signed_by_tenant = Column(Boolean, default=False)
    signed_at = Column(DateTime(timezone=True))
    is_locked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenancy = relationship("Tenancy", back_populates="condition_reports")
    items = relationship("ConditionItem", back_populates="report", cascade="all, delete-orphan")


class ConditionItem(Base):
    __tablename__ = "condition_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("condition_reports.id"))
    item_name = Column(String, nullable=False)
    condition = Column(SQLEnum(ConditionRating), nullable=True)
    notes = Column(Text)
    photo_url = Column(String)
    deduction_amount = Column(Numeric(10, 2))
    disputed = Column(Boolean, default=False)

    report = relationship("ConditionReport", back_populates="items")


# ─── Payments ─────────────────────────────────────────────────────

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenancy_id = Column(UUID(as_uuid=True), ForeignKey("tenancies.id"))
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    method = Column(SQLEnum(PaymentMethod))
    reference = Column(String)
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenancy = relationship("Tenancy", back_populates="payments")


# ─── Audit Log ────────────────────────────────────────────────────

class TenancyStatusLog(Base):
    __tablename__ = "tenancy_status_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenancy_id = Column(UUID(as_uuid=True), ForeignKey("tenancies.id"))
    from_status = Column(SQLEnum(TenancyStatus))
    to_status = Column(SQLEnum(TenancyStatus), nullable=False)
    changed_by = Column(UUID(as_uuid=True))
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    note = Column(Text)


# ─── Tickets ──────────────────────────────────────────────────────

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenancy_id = Column(UUID(as_uuid=True), ForeignKey("tenancies.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(TicketStatus), nullable=False, default=TicketStatus.open)
    priority = Column(SQLEnum(TicketPriority), nullable=False, default=TicketPriority.medium)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tenancy = relationship("Tenancy")


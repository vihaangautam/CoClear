from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


# ─── Enums ────────────────────────────────────────────────────────

class TenancyStatusEnum(str, Enum):
    inquiry = "inquiry"
    confirmed = "confirmed"
    active = "active"
    notice_period = "notice_period"
    vacated = "vacated"
    cancelled = "cancelled"


class ConditionRatingEnum(str, Enum):
    good = "good"
    fair = "fair"
    damaged = "damaged"
    missing = "missing"


class PaymentMethodEnum(str, Enum):
    upi = "upi"
    cash = "cash"
    bank_transfer = "bank_transfer"
    other = "other"


# ─── Operator ────────────────────────────────────────────────────

class OperatorCreate(BaseModel):
    name: str
    email: str
    phone: str

class OperatorOut(BaseModel):
    id: UUID
    name: str
    email: str
    phone: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Property ────────────────────────────────────────────────────

class PropertyCreate(BaseModel):
    name: str
    address: str
    type: str  # 'men', 'women', 'mixed'

class PropertyOut(BaseModel):
    id: UUID
    operator_id: UUID
    name: str
    address: str
    type: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Room ────────────────────────────────────────────────────────

class RoomCreate(BaseModel):
    room_number: str
    floor: Optional[int] = None
    total_beds: int = 1

class BedOut(BaseModel):
    id: UUID
    label: str

    class Config:
        from_attributes = True

class RoomOut(BaseModel):
    id: UUID
    property_id: UUID
    room_number: str
    floor: Optional[int]
    total_beds: int
    beds: List[BedOut] = []

    class Config:
        from_attributes = True


# ─── Bed ─────────────────────────────────────────────────────────

class BedCreate(BaseModel):
    label: str = "Bed 1"


# ─── Tenant ──────────────────────────────────────────────────────

class TenantCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: str
    aadhaar_last4: Optional[str] = None

class TenantOut(BaseModel):
    id: UUID
    name: str
    email: Optional[str]
    phone: str
    aadhaar_last4: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Tenancy ─────────────────────────────────────────────────────

class TenancyCreate(BaseModel):
    bed_id: UUID
    tenant_id: UUID
    rent_amount: Decimal
    rent_due_day: Optional[int] = 1
    deposit_amount: Decimal = Decimal("0")
    move_in_date: Optional[date] = None

class TenancyTransition(BaseModel):
    to: TenancyStatusEnum

class TenancyOut(BaseModel):
    id: UUID
    bed_id: Optional[UUID]
    tenant_id: Optional[UUID]
    operator_id: Optional[UUID]
    status: TenancyStatusEnum
    rent_amount: Decimal
    rent_due_day: Optional[int]
    deposit_amount: Decimal
    deposit_refunded: Optional[Decimal]
    move_in_date: Optional[date]
    notice_given_date: Optional[date]
    vacating_date: Optional[date]
    vacated_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    tenant: Optional[TenantOut] = None
    bed: Optional[BedOut] = None

    class Config:
        from_attributes = True


# ─── Payment ─────────────────────────────────────────────────────

class PaymentCreate(BaseModel):
    amount: Decimal
    payment_date: date
    method: Optional[PaymentMethodEnum] = None
    reference: Optional[str] = None
    note: Optional[str] = None

class PaymentOut(BaseModel):
    id: UUID
    tenancy_id: UUID
    amount: Decimal
    payment_date: date
    method: Optional[PaymentMethodEnum]
    reference: Optional[str]
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Condition Report ────────────────────────────────────────────

class ConditionItemCreate(BaseModel):
    item_name: str
    condition: Optional[ConditionRatingEnum] = None
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    deduction_amount: Optional[Decimal] = None

class ConditionItemOut(BaseModel):
    id: UUID
    report_id: UUID
    item_name: str
    condition: Optional[ConditionRatingEnum]
    notes: Optional[str]
    photo_url: Optional[str]
    deduction_amount: Optional[Decimal]
    disputed: bool

    class Config:
        from_attributes = True

class ConditionReportCreate(BaseModel):
    report_type: str  # 'check_in' or 'check_out'

class ConditionReportOut(BaseModel):
    id: UUID
    tenancy_id: UUID
    report_type: str
    signed_by_operator: bool
    signed_by_tenant: bool
    signed_at: Optional[datetime]
    is_locked: bool
    created_at: datetime
    items: List[ConditionItemOut] = []

    class Config:
        from_attributes = True


# ─── Dashboard Stats ─────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_properties: int
    total_beds: int
    active_tenancies: int
    occupancy_percent: float
    total_revenue_mtd: Decimal
    tenancies_in_notice: int


class OccupancyBed(BaseModel):
    bed_id: UUID
    label: str
    room_number: str
    status: Optional[TenancyStatusEnum]
    tenant_name: Optional[str] = None

class PropertyOccupancy(BaseModel):
    property_id: UUID
    property_name: str
    address: str
    occupancy_percent: float
    beds: List[OccupancyBed]

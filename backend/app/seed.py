"""
Seed script — populates the database with realistic demo data for the PGPal MVP.
Run: python -m app.seed  (from the backend directory)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__) + "/..")

from datetime import date, timedelta
from decimal import Decimal
from app.database import SessionLocal, engine
from app.models import (
    Base, Operator, Property, Room, Bed, Tenant, Tenancy,
    TenancyStatus, Payment, PaymentMethod,
    ConditionReport, ConditionItem, ConditionRating,
)
from app.auth import get_password_hash

def seed():
    db = SessionLocal()

    # Check if already seeded
    if db.query(Operator).first():
        print("Database already seeded. Skipping.")
        db.close()
        return

    print("[SEED] Seeding database...")

    # ─── Operator ──────────────────────────────────────────────
    op = Operator(
        name="Ramesh Kumar",
        email="ramesh@pgpal.in",
        phone="+919876543210",
        password_hash=get_password_hash("password123"),
    )
    db.add(op)
    db.flush()

    # ─── Properties ────────────────────────────────────────────
    p1 = Property(operator_id=op.id, name="The Vertex", address="Sector 42, Koramangala", type="mixed")
    p2 = Property(operator_id=op.id, name="Lumina Coliving", address="HSR Layout, Sector 2", type="women")
    db.add_all([p1, p2])
    db.flush()

    # ─── Rooms + Beds for The Vertex (8 rooms, 2 beds each) ───
    rooms_p1 = []
    beds_p1 = []
    for i in range(1, 9):
        room = Room(property_id=p1.id, room_number=str(i), floor=(i - 1) // 4 + 1, total_beds=2)
        db.add(room)
        db.flush()
        rooms_p1.append(room)
        for letter in ["A", "B"]:
            bed = Bed(room_id=room.id, label=f"{i}{letter}")
            db.add(bed)
            db.flush()
            beds_p1.append(bed)

    # ─── Rooms + Beds for Lumina (4 rooms, 2 beds each) ───────
    rooms_p2 = []
    beds_p2 = []
    for i in range(1, 5):
        room = Room(property_id=p2.id, room_number=str(i), floor=1, total_beds=2)
        db.add(room)
        db.flush()
        rooms_p2.append(room)
        for letter in ["A", "B"]:
            bed = Bed(room_id=room.id, label=f"{i}{letter}")
            db.add(bed)
            db.flush()
            beds_p2.append(bed)

    # ─── Tenants ──────────────────────────────────────────────
    default_password = get_password_hash("password123")
    tenants = [
        Tenant(name="Priya Sharma", email="priya@example.com", phone="+919111111111", aadhaar_last4="1234", password_hash=default_password),
        Tenant(name="Amit Singh", email="amit@example.com", phone="+919222222222", aadhaar_last4="5678", password_hash=default_password),
        Tenant(name="Neha Gupta", email="neha@example.com", phone="+919333333333", aadhaar_last4="9012", password_hash=default_password),
        Tenant(name="Rahul Verma", email="rahul@example.com", phone="+919444444444", aadhaar_last4="3456", password_hash=default_password),
        Tenant(name="Ananya Reddy", email="ananya@example.com", phone="+919555555555", aadhaar_last4="7890", password_hash=default_password),
        Tenant(name="Vikram Patel", email="vikram@example.com", phone="+919666666666", aadhaar_last4="2345", password_hash=default_password),
        Tenant(name="Deepa Nair", email="deepa@example.com", phone="+919777777777", aadhaar_last4="6789", password_hash=default_password),
        Tenant(name="Arjun Mehta", email="arjun@example.com", phone="+919888888888", aadhaar_last4="0123", password_hash=default_password),
        Tenant(name="Kavita Joshi", email="kavita@example.com", phone="+919999999999", password_hash=default_password),
        Tenant(name="Ravi Shankar", email="ravi@example.com", phone="+919101010101", password_hash=default_password),
    ]
    db.add_all(tenants)
    db.flush()

    today = date.today()

    # ─── Tenancies for The Vertex ─────────────────────────────
    # Active tenancies (beds 1A-4B = 8 beds)
    active_beds = beds_p1[:8]
    for i, bed in enumerate(active_beds):
        t = Tenancy(
            bed_id=bed.id,
            tenant_id=tenants[i].id if i < len(tenants) else tenants[0].id,
            operator_id=op.id,
            status=TenancyStatus.active,
            rent_amount=Decimal("12500"),
            rent_due_day=1,
            deposit_amount=Decimal("25000"),
            move_in_date=today - timedelta(days=90 + i * 10),
        )
        db.add(t)
        db.flush()

        # Add some payments for each active tenancy
        for month_offset in range(3):
            pay_date = today - timedelta(days=30 * month_offset)
            payment = Payment(
                tenancy_id=t.id,
                amount=Decimal("12500"),
                payment_date=pay_date,
                method=PaymentMethod.upi,
                reference=f"TXN-{bed.label}-{month_offset}",
                note=f"Rent for month -{month_offset}",
            )
            db.add(payment)

    # Notice period tenancy (bed 5A — Vertex)
    notice_tenancy = Tenancy(
        bed_id=beds_p1[8].id,  # 5A
        tenant_id=tenants[8].id,
        operator_id=op.id,
        status=TenancyStatus.notice_period,
        rent_amount=Decimal("12500"),
        rent_due_day=1,
        deposit_amount=Decimal("25000"),
        move_in_date=today - timedelta(days=180),
        notice_given_date=today - timedelta(days=5),
        vacating_date=today + timedelta(days=25),
    )
    db.add(notice_tenancy)
    db.flush()

    # Inquiry tenancy (bed 6A — Vertex)
    inquiry_tenancy = Tenancy(
        bed_id=beds_p1[10].id,  # 6A
        tenant_id=tenants[9].id,
        operator_id=op.id,
        status=TenancyStatus.inquiry,
        rent_amount=Decimal("12500"),
        rent_due_day=1,
        deposit_amount=Decimal("25000"),
    )
    db.add(inquiry_tenancy)

    # ─── Tenancies for Lumina ─────────────────────────────────
    # Active (beds 1A, 1B, 2A)
    for i in range(3):
        t = Tenancy(
            bed_id=beds_p2[i].id,
            tenant_id=tenants[i].id,
            operator_id=op.id,
            status=TenancyStatus.active,
            rent_amount=Decimal("10000"),
            rent_due_day=5,
            deposit_amount=Decimal("20000"),
            move_in_date=today - timedelta(days=60 + i * 15),
        )
        db.add(t)
        db.flush()

    # Notice (bed 2B)
    t_notice = Tenancy(
        bed_id=beds_p2[3].id,
        tenant_id=tenants[3].id,
        operator_id=op.id,
        status=TenancyStatus.notice_period,
        rent_amount=Decimal("10000"),
        rent_due_day=5,
        deposit_amount=Decimal("20000"),
        move_in_date=today - timedelta(days=200),
        notice_given_date=today - timedelta(days=3),
        vacating_date=today + timedelta(days=27),
    )
    db.add(t_notice)

    # Inquiry (bed 3A)
    t_inq = Tenancy(
        bed_id=beds_p2[4].id,
        tenant_id=tenants[4].id,
        operator_id=op.id,
        status=TenancyStatus.inquiry,
        rent_amount=Decimal("10000"),
        rent_due_day=5,
        deposit_amount=Decimal("20000"),
    )
    db.add(t_inq)

    db.commit()
    db.close()
    print("[OK] Database seeded successfully!")
    print(f"   • 1 Operator: Ramesh Kumar")
    print(f"   • 2 Properties: The Vertex (16 beds), Lumina Coliving (8 beds)")
    print(f"   • 10 Tenants")
    print(f"   • Multiple tenancies in various states (active, notice, inquiry)")
    print(f"   • Payment history for active tenancies")


if __name__ == "__main__":
    seed()

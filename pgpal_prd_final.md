# PGPal — Final PRD (Delta Version)
**Version:** 2.0 — Delta  
**Date:** May 2026  
**Status:** Build-ready. Scope locked.  
**Changes from v1.0:** Scope narrowed to validated core. Celery deferred. Tenant portal scoped to read-only. Market evidence section added. Build order resequenced.

---

## What Changed and Why

The original PRD (v1.0) was a comprehensive full-lifecycle PG management platform: rent tracking, Celery reminders, maintenance ticketing, full tenant portal, 3-role auth, GraphQL roadmap — the works.

The Lean PRD identified the real, validated pain point: **deposit disputes caused by missing evidence at move-in and move-out**.

This delta document resolves the tension between them. It keeps everything from v1.0 that builds toward the core value proposition, cuts everything that doesn't earn its scope in MVP, and adds real market evidence that didn't exist in either document.

**The rule applied to every feature:** Does this directly prevent a deposit dispute or make the evidence case stronger? If yes, keep. If no, defer.

---

## 1. The Validated Problem — Real Market Evidence

Before any feature discussion, here is the proof that this product should exist.

### 1.1 The Problem Is Mainstream, Not Niche

In April 2025, entrepreneur Varun Mayya posted on X: *"The biggest scam in Bangalore is when you are leaving an apartment and the owner sends you a fraction of the security deposit claiming 'damage' or something despite no evidence. I've lived in maybe 10 apartments and this illegal retention of deposit has happened every single time."* The post went viral — over a million views, hundreds of corroborating stories. Financial advisor AK Mandhan subsequently posted the same frustration independently, calling it "Bangalore's biggest scam." Two separate people with large audiences independently surfaced the same problem in the same city in the same quarter. *([Business Today, April 2025](https://www.businesstoday.in/personal-finance/real-estate/story/the-biggest-scam-in-bengaluru-investment-advisor-calls-out-citys-rental-deposit-trap-472022-2025-04-15))*

This is not a niche legal complaint. It is a lived urban experience with millions of impressions of validation.

### 1.2 The Root Cause Is Always the Same: No Evidence

The Business Today coverage identified the precise mechanism: *"Claims of 'damage' come with no evidence, no bills — just vague justifications."* The Karnataka Rent Control Act is clear — landlords must return deposits within 30 days and furnish itemised receipts for any deductions. The law is not the problem. The evidence vacuum is.

Tenants cannot prove the room was undamaged at check-in. Operators cannot prove it was damaged at checkout. Both sides are arguing from memory over WhatsApp. **PGPal's check-in/check-out condition report with timestamped photos and dual signatures is the direct, surgical solution to this exact mechanism.**

### 1.3 Consumer Complaints Are Documented and Recurring

On Voxya (India's consumer complaint platform), Colive Bangalore alone has dozens of documented deposit disputes — unnecessary deductions, non-return of deposits, one-sided deductions with no explanation. These are branded, tech-enabled co-living operators with apps and support teams. Independent PG operators, who have none of that infrastructure, produce disputes at a far higher rate with zero recourse infrastructure for either party.

A Bengaluru tenant in BTM Layout went viral on Reddit in October 2025 after his landlord vanished without returning a deposit — after proper notice, with a rental agreement in place. He had to appeal to Karnataka Police publicly. *([Deccan Herald, October 2025](https://www.deccanherald.com/india/karnataka/bengaluru/bengaluru-security-deposit-scam-landlord-vanishes-without-returning-deposit-to-tenant-3775530))*

### 1.4 The Regulatory Tailwind Is Real and Accelerating

As of May 2025, BBMP inspected 4,456 PGs in Bengaluru:
- 2,504 were authorised
- **1,799 were unauthorised** (running illegally)
- 533 were found violating rules
- 94 PGs were shut down in a single enforcement wave

*([The Hans India, May 2025](https://www.thehansindia.com/amp/bengaluru/bbmp-plans-to-regulate-unauthorised-pgs-in-bengaluru-968661))*

BBMP is now actively considering a licensing system. Operators who cannot produce tenant records, KYC documentation, and maintenance histories during inspections are exposed. PGPal's tenancy records and condition reports directly address this compliance need — not as a future feature, but as an immediate sales angle.

### 1.5 The Competitor Gap Is Confirmed

RentOk — the market leader with 15,000+ operators — covers rent collection, KYC, WhatsApp reminders, and payment tracking. Its own marketing lists features extensively. **Check-in/check-out condition reports with photos do not appear anywhere in RentOk's feature set.** The deposit dispute evidence gap is confirmed unoccupied in the leading product.

---

## 2. What This Product Is

**PGPal is deposit dispute prevention infrastructure for independent PG operators in Bengaluru.**

It is not a listing site. It is not a coliving brand. It is not trying to be the "operating system for all of PG management" in v1.

**Tagline:** "Protect deposits. Prevent disputes. Keep proof."

**Who pays:** PG operators (B2B SaaS, ₹499–1,499/month per property). Tenants use the evidence features for free.

**The core value exchange:** The operator gets legal-grade evidence that protects their deposit deductions. The tenant gets a signed check-in record that protects them from invented damage claims. Both parties benefit. Neither has incentive to avoid the tool.

---

## 3. User Personas

### Ramesh — PG Operator, Koramangala, 24 beds

Manages a 4-floor building with 24 beds alongside a day job. Uses WhatsApp, a notebook, and memory. Lost two deposit disputes last year — once paid back a full deposit because he had no proof of damage; once withheld a deposit and received a legal notice. He wants to run this like a business.

**Willingness to pay:** ₹500–1,500/month if the product saves him from one deposit dispute per year. At ₹20,000 average disputed deposit, the ROI is immediate.

**What he needs from MVP:** Condition reports with photos, signed by both parties. Dashboard to see which beds are occupied and which are in notice. Tenant records for BBMP compliance.

### Priya — Tenant, Software Engineer, HSR Layout

First year in Bengaluru. Paid ₹20,000 deposit. Pays rent via UPI with no receipt. Reported a broken AC three weeks ago over WhatsApp. Worried about getting her deposit back.

**What she needs from MVP:** A signed check-in record she can show if there's a dispute. A rent receipt she can download. These she gets for free because her operator uses PGPal.

---

## 4. MVP Scope — Final and Locked

### In Scope

| Feature | Justification |
|---|---|
| Property + room + bed CRUD | Required to model the property being protected |
| Tenant creation + onboarding | Required to associate tenancy with condition report |
| Tenancy state machine (inquiry → active → notice → vacated) | Required to know when check-in/checkout reports are needed |
| **Check-in condition report** | **Core product. Primary differentiator. Ships first.** |
| **Check-out condition report + diff vs check-in** | **Core product. The settlement evidence moment.** |
| **Photo uploads per condition item (Cloudflare R2)** | **Core product. Evidence without photos is useless.** |
| **Dual digital sign-off (operator + tenant)** | **Core product. Signature = legal weight.** |
| **Immutable report after signing (append-only trigger)** | **Core product. Tamper-proof = court-admissible.** |
| **PDF export of settlement report** | **Core product. The deliverable that ends the dispute.** |
| Deposit deduction tracking on checkout | Directly part of the settlement workflow |
| Basic operator dashboard (occupancy grid, tenancy status) | Required to navigate to condition reports |
| JWT auth (operator + tenant roles) | Required to attribute signatures to real users |
| Tenant read-only portal (view check-in report, view deposit status) | Required for tenant to access their evidence |
| Payment logging (manual, no gateway) | Basic ledger; receipt useful but not the differentiator |

### Deferred to Phase 2+

| Feature | Why Deferred |
|---|---|
| Celery rent reminders | Adds Redis + worker infrastructure; not core to dispute prevention |
| Maintenance ticketing | Valuable but not the sales hook; add after condition reports are sticky |
| Full tenant portal (complaints, full ledger, notifications) | Scope risk; tenant only needs read access to their check-in report in v1 |
| UPI/Razorpay payment integration | Compliance overhead; manual payment logging is sufficient in v1 |
| WhatsApp notifications | Nice-to-have; email works for v1 |
| GraphQL | Add on top of stable REST API in v2 |
| Mobile app (React Native) | PWA is sufficient for v1 |
| KYC API / DigiLocker | V2 compliance feature |
| Public listing / discovery | Needs operator critical mass first |

**Scope decision rule:** If a feature does not directly make the check-in/checkout evidence stronger, more signed, or more defensible in a dispute — it is Phase 2.

---

## 5. Core Feature: Condition Reports

This is the product. Everything else is scaffolding.

### 5.1 Check-in Report (Move-In)

1. Operator creates tenant entry and initiates check-in report
2. Pre-defined checklist appears: Walls, Floor, Ceiling, Bed frame, Mattress, Wardrobe/Almirah, Table & Chair, AC (if applicable), Geyser, Bathroom fittings, Window/Door, Other
3. For each item: condition rating (Good / Fair / Damaged / Missing) + optional photo upload
4. Free-text notes per item
5. Both operator and tenant tap "Sign & Confirm" — generates a cryptographic timestamp + user ID signature
6. Report becomes **immutable** — Postgres trigger prevents any edits after signing
7. Tenancy transitions from `confirmed` to `active` only after check-in report is signed by both parties

### 5.2 Check-out Report (Move-Out)

1. Operator initiates checkout inspection
2. Same checklist, same photo upload workflow
3. System renders a **side-by-side diff**: every item's check-in condition vs check-out condition
4. Operator marks disputed items, proposes deduction amounts with reasons
5. Tenant reviews the diff, can accept or flag line items
6. Final settlement calculated: `deposit_amount - total_deductions = refund_amount`
7. **PDF settlement report generated**: includes check-in photos, check-out photos, diff view, deduction table, both parties' signatures, server timestamps

### 5.3 Why Immutability Matters

The report's legal defensibility depends on it being tamper-proof. A photo that can be edited after the fact is worthless in a consumer court filing. The Postgres trigger ensures:
- No UPDATE on condition_items after `is_locked = true`
- No DELETE on condition_reports ever
- Every signature is stored with server timestamp, not client-provided timestamp

This is the detail that separates PGPal from "just take photos on WhatsApp."

### 5.4 The Sales Pitch in One Sentence

"The next time a tenant threatens you over their deposit, you open the app, show them the signed check-in photo of the room's exact condition — taken together, signed by both of you, timestamped by the server. The conversation ends."

---

## 6. Tenancy State Machine

The state machine gates the condition report workflow. It is not optional architecture — it is what ensures the check-in report is completed before a tenancy goes active, and the checkout report is completed before a tenancy closes.

```
INQUIRY ──► CONFIRMED ──► ACTIVE ──► NOTICE_PERIOD ──► VACATED
                │                          │
                └──────────────────────────┴──► CANCELLED
```

| State | Meaning | Trigger |
|---|---|---|
| `inquiry` | Prospective tenant shown interest | Operator creates |
| `confirmed` | Deposit paid, move-in date set | Operator confirms |
| `active` | Check-in report signed by both parties | Auto on dual sign |
| `notice_period` | 30-day notice given; vacating date locked | Tenant or operator |
| `vacated` | Checkout done, deposit settled | Operator closes |
| `cancelled` | Pre-move-in abandonment | Operator cancels |

**Critical gate:** `confirmed → active` requires a signed check-in report. The app will not allow this transition without it. This is how operators are nudged to complete the most important step — not through messaging, but through workflow.

---

## 7. Data Model

```sql
-- Tenancy state machine
CREATE TYPE tenancy_status AS ENUM (
  'inquiry', 'confirmed', 'active', 'notice_period', 'vacated', 'cancelled'
);

CREATE TABLE operators (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          TEXT NOT NULL,
  email         TEXT UNIQUE NOT NULL,
  phone         TEXT NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE properties (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id   UUID REFERENCES operators(id) ON DELETE CASCADE,
  name          TEXT NOT NULL,
  address       TEXT NOT NULL,
  type          TEXT CHECK (type IN ('men', 'women', 'mixed')) NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE rooms (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id   UUID REFERENCES properties(id) ON DELETE CASCADE,
  room_number   TEXT NOT NULL,
  floor         INT,
  total_beds    INT NOT NULL DEFAULT 1,
  UNIQUE(property_id, room_number)
);

CREATE TABLE beds (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  room_id       UUID REFERENCES rooms(id) ON DELETE CASCADE,
  label         TEXT NOT NULL DEFAULT 'Bed 1'
);

CREATE TABLE tenants (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          TEXT NOT NULL,
  email         TEXT UNIQUE,
  phone         TEXT NOT NULL,
  aadhaar_last4 TEXT,
  created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE tenancies (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bed_id              UUID REFERENCES beds(id),
  tenant_id           UUID REFERENCES tenants(id),
  operator_id         UUID REFERENCES operators(id),
  status              tenancy_status NOT NULL DEFAULT 'inquiry',
  rent_amount         NUMERIC(10,2) NOT NULL,
  rent_due_day        INT CHECK (rent_due_day BETWEEN 1 AND 28),
  deposit_amount      NUMERIC(10,2) NOT NULL DEFAULT 0,
  deposit_refunded    NUMERIC(10,2),
  move_in_date        DATE,
  notice_given_date   DATE,
  vacating_date       DATE,
  vacated_date        DATE,
  created_at          TIMESTAMPTZ DEFAULT now(),
  updated_at          TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE payments (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenancy_id    UUID REFERENCES tenancies(id),
  amount        NUMERIC(10,2) NOT NULL,
  payment_date  DATE NOT NULL,
  method        TEXT CHECK (method IN ('upi', 'cash', 'bank_transfer', 'other')),
  reference     TEXT,
  note          TEXT,
  created_at    TIMESTAMPTZ DEFAULT now()
);

-- THE CORE TABLES
CREATE TABLE condition_reports (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenancy_id          UUID REFERENCES tenancies(id),
  report_type         TEXT CHECK (report_type IN ('check_in', 'check_out')) NOT NULL,
  signed_by_operator  BOOLEAN DEFAULT false,
  signed_by_tenant    BOOLEAN DEFAULT false,
  signed_at           TIMESTAMPTZ,
  is_locked           BOOLEAN DEFAULT false,
  created_at          TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE condition_items (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_id        UUID REFERENCES condition_reports(id),
  item_name        TEXT NOT NULL,
  condition        TEXT CHECK (condition IN ('good','fair','damaged','missing')),
  notes            TEXT,
  photo_url        TEXT,
  deduction_amount NUMERIC(10,2),
  disputed         BOOLEAN DEFAULT false
);

-- Immutability trigger
CREATE OR REPLACE FUNCTION enforce_report_lock()
RETURNS TRIGGER AS $$
BEGIN
  IF (SELECT is_locked FROM condition_reports WHERE id = OLD.report_id) THEN
    RAISE EXCEPTION 'Condition report is locked after signing. No edits permitted.';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER condition_item_lock_check
  BEFORE UPDATE OR DELETE ON condition_items
  FOR EACH ROW EXECUTE FUNCTION enforce_report_lock();

-- Tenancy transition trigger
CREATE OR REPLACE FUNCTION validate_tenancy_transition()
RETURNS TRIGGER AS $$
BEGIN
  IF OLD.status IN ('vacated', 'cancelled') THEN
    RAISE EXCEPTION 'Cannot transition from terminal state %', OLD.status;
  END IF;
  IF NOT (
    (OLD.status = 'inquiry'       AND NEW.status IN ('confirmed', 'cancelled')) OR
    (OLD.status = 'confirmed'     AND NEW.status IN ('active', 'cancelled')) OR
    (OLD.status = 'active'        AND NEW.status = 'notice_period') OR
    (OLD.status = 'notice_period' AND NEW.status = 'vacated')
  ) THEN
    RAISE EXCEPTION 'Invalid transition: % → %', OLD.status, NEW.status;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tenancy_transition_check
  BEFORE UPDATE OF status ON tenancies
  FOR EACH ROW EXECUTE FUNCTION validate_tenancy_transition();

-- Status audit log (append-only — never delete)
CREATE TABLE tenancy_status_log (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenancy_id  UUID REFERENCES tenancies(id),
  from_status tenancy_status,
  to_status   tenancy_status NOT NULL,
  changed_by  UUID,
  changed_at  TIMESTAMPTZ DEFAULT now(),
  note        TEXT
);
```

### Relationship Summary

```
operator
  └── properties
        └── rooms
              └── beds
                    └── tenancies
                          ├── payments
                          └── condition_reports (check_in + check_out)
                                └── condition_items (with photo_url)
```

---

## 8. API Surface (MVP)

Base URL: `https://api.pgpal.in/v1`  
All endpoints require `Authorization: Bearer <JWT>` except auth.

### Auth
| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/login` | Email + password → JWT |
| `POST` | `/auth/refresh` | Refresh JWT |
| `POST` | `/auth/invite/accept` | Tenant accepts invite, sets password |

### Properties, Rooms, Beds
| Method | Path | Description |
|---|---|---|
| `GET` | `/properties` | List with occupancy summary |
| `POST` | `/properties` | Create property |
| `GET` | `/properties/{id}/rooms` | Rooms + beds + tenancy status |
| `POST` | `/properties/{id}/rooms` | Add room |
| `POST` | `/rooms/{id}/beds` | Add bed |

### Tenancy Lifecycle
| Method | Path | Description |
|---|---|---|
| `POST` | `/tenancies` | Create (inquiry state) |
| `GET` | `/tenancies/{id}` | Full tenancy record |
| `PATCH` | `/tenancies/{id}/transition` | `{ "to": "confirmed" }` — validated |
| `POST` | `/tenancies/{id}/notice` | Record notice; auto-sets vacating_date |

### Condition Reports (Core)
| Method | Path | Description |
|---|---|---|
| `POST` | `/tenancies/{id}/condition-report` | Create check-in or check-out report |
| `GET` | `/tenancies/{id}/condition-report/{type}` | Get report (check_in or check_out) |
| `POST` | `/condition-reports/{id}/items` | Add item with condition + photo |
| `POST` | `/condition-reports/{id}/sign` | Operator or tenant signs; locks when both sign |
| `GET` | `/tenancies/{id}/condition-report/diff` | Side-by-side check-in vs check-out |
| `GET` | `/tenancies/{id}/settlement-pdf` | Generate PDF settlement report |

### File Upload
| Method | Path | Description |
|---|---|---|
| `POST` | `/upload/presigned` | Get presigned R2 URL; client uploads directly |

### Payments (Basic)
| Method | Path | Description |
|---|---|---|
| `GET` | `/tenancies/{id}/payments` | Payment ledger |
| `POST` | `/tenancies/{id}/payments` | Log payment |
| `GET` | `/tenancies/{id}/payments/{pid}/receipt` | PDF receipt |

### Tenant Portal (Read-Only in MVP)
| Method | Path | Description |
|---|---|---|
| `GET` | `/tenant/me` | Profile + active tenancy |
| `GET` | `/tenant/payments` | Ledger view |
| `GET` | `/tenant/condition-report` | Check-in report for current tenancy |

---

## 9. Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| Frontend | React 18 + Vite 5 | |
| State | TanStack Query v5 | Server state, caching |
| Routing | React Router v6 | Role-based protected routes |
| UI | Shadcn/ui + Tailwind | |
| Backend | FastAPI 0.111+ | Async, Pydantic, auto OpenAPI |
| ORM | SQLAlchemy 2.0 async | |
| Migrations | Alembic | Every schema change versioned |
| Database | PostgreSQL 16 | ENUMs, RLS, triggers |
| File storage | Cloudflare R2 | S3-compatible, zero egress fees |
| Auth | python-jose + passlib | JWT + bcrypt |
| PDF | WeasyPrint | Receipts + settlement reports |
| Containerisation | Docker Compose | 3 services in MVP: api, postgres, redis (deferred: worker) |
| Deployment | Railway | Managed Postgres + Redis |

**MVP Docker Compose (3 services — no Celery worker yet):**
```yaml
services:
  api:       # FastAPI
  postgres:  # PostgreSQL 16
  redis:     # Reserved for Phase 2 Celery
```

Celery + worker are deferred to Phase 2. Email reminders can be sent synchronously in the background via FastAPI's `BackgroundTasks` for MVP without a full Celery setup.

---

## 10. Non-Functional Requirements

**Security**
- JWT: 15-minute access token + 7-day refresh token
- Passwords: bcrypt cost factor 12
- Condition report photos: private R2 bucket, presigned URLs expire in 1 hour
- Signed reports: append-only at DB level (trigger prevents UPDATE/DELETE after lock)
- RLS: operator data isolation — one operator cannot read another's data even on application bug

**Performance**
- Dashboard load: < 800ms p95
- Pagination on all list endpoints (page size: 20)
- Indexes: `tenancies(bed_id, status)`, `tenancies(operator_id)`, `payments(tenancy_id)`, `condition_reports(tenancy_id)`

**Compliance**
- Condition reports timestamped and user-attributed — suitable as evidence in consumer court
- No Aadhaar number storage; last 4 digits only
- Tenant data never exposed to other tenants

---

## 11. Build Order

Build in this sequence. Each milestone gates the next. **Do not skip ahead.**

### Milestone 1 — Schema & State Machine (Week 1–2)
**Goal:** Working Postgres schema with migrations, state machine trigger, immutability trigger, RLS.

Deliverables:
- All tables via Alembic migration
- Tenancy transition trigger (with invalid transition rejection)
- Condition report immutability trigger (tested: attempt edit after lock → exception)
- RLS policies for operator isolation
- Seed script: 1 operator, 1 property, 2 rooms, 4 beds, 2 tenancies in different states

**Learning:** Alembic, Postgres ENUMs, triggers, RLS. Most conceptually dense week.

---

### Milestone 2 — FastAPI Core + Auth (Week 3–4)
**Goal:** Auth working. CRUD for all entities. State transition endpoint validated.

Deliverables:
- JWT auth (login, refresh, invite accept)
- CRUD: properties, rooms, beds, tenants
- Tenancy CRUD + `/transition` with state machine validation
- Payment logging + PDF receipt endpoint
- Pytest: at least 10 state machine transition tests (valid and invalid)

---

### Milestone 3 — Condition Reports + R2 (Week 5–6)
**Goal:** The core feature working end-to-end. This is the milestone that matters.

Deliverables:
- Condition report API (create, add items, sign)
- Presigned R2 URL endpoint (client uploads directly; only URL stored)
- Report locking on dual sign (trigger tested)
- Diff endpoint: check-in vs check-out comparison
- PDF settlement report generation (WeasyPrint: photos + diff table + both signatures)
- Pytest: sign flow, lock enforcement, diff accuracy

**This milestone = the demo you show operators.**

---

### Milestone 4 — React Frontend (Week 7–10)
**Goal:** Operator dashboard + condition report UI working end-to-end.

Deliverables:
- Operator dashboard: property/room/bed grid with color-coded status (Green/Amber/Red/Grey/Blue)
- Tenancy creation flow + state transition buttons
- **Condition report form: checklist + photo upload + signature UI** (most important screen)
- **Side-by-side diff view + deposit deduction entry**
- **Settlement PDF download**
- Tenant portal: check-in report read-only view + ledger
- Role-based routing (operator vs tenant)

---

### Milestone 5 — Deploy + First Operator (Week 11–12)
**Goal:** Live on Railway. First real Koramangala operator onboarded.

Deliverables:
- Docker Compose deploy to Railway
- Environment variable management
- Walk Koramangala 5th Block or 6th Block with the demo on your phone
- First operator running a real check-in report

---

## 12. Go-to-Market

### Target Areas (Bengaluru, Phase 1)
Walk these streets in order of PG density:
1. Koramangala 5th and 6th Block
2. HSR Layout Sector 1–2
3. Indiranagar 100ft Road
4. Marathahalli (near tech parks)

**Identifying prospects:** Buildings with hand-painted "PG Available" boards, NoBroker listings with a personal mobile number (not a brand name). These are independent operators — not Stanza, Zolo, or Colive, who are too large and have their own systems.

### The 5-Minute Sales Conversation

**Opening:** "How do you currently handle it when a tenant claims you're inventing damage to keep their deposit?"

If they describe WhatsApp arguments, paying money back without proof, or receiving legal notices — you have qualified them.

**Second question:** "When a tenant gives notice, how far in advance do you know the room is actually vacating?"

**The demo:** Show the condition report on your phone. The checklist. The photo upload. The side-by-side diff. The signed PDF. That's 3 minutes. Most operators will ask "how much does it cost" before you finish the demo.

### Pricing (MVP)

| Tier | Price | Beds |
|---|---|---|
| Starter | ₹499/month | Up to 20 beds |
| Growth | ₹999/month | 21–50 beds |
| Multi-property | ₹1,499/month | 50+ beds or multiple properties |

First 30 days free, no credit card. Goal in year 1 is adoption, not revenue maximisation. One avoided deposit dispute covers 6–18 months of subscription fees.

### The Regulatory Angle

BBMP recently shut down 94 PGs in a single enforcement wave. The secondary pitch: "If a BBMP inspector shows up, you can pull up every tenancy record, every KYC document, every condition report — on your phone, in 30 seconds."

---

## 13. Success Metrics

### MVP Success (90 Days Post-Launch)

| Metric | Target |
|---|---|
| Operators onboarded | 10+ in Koramangala/HSR |
| Active tenancies in system | 80+ beds |
| Check-in reports completed | >70% of active tenancies |
| Check-out settlement PDFs generated | >3 |

### The Single Best Signal

An operator shows you a resolved deposit dispute where the check-in photo from PGPal was the deciding evidence. That is the moment the product is real.

### Leading Indicators of Product-Market Fit

- Operators send the check-in report link to tenants before you remind them to
- A tenant screenshots their check-in report and shares it in a dispute
- An operator refers another operator before you've asked

---

## 14. What Is Not Being Built and Why

| Not Building | Reason |
|---|---|
| Celery rent reminders | Adds Redis worker infrastructure; reminders are a convenience, not the core value. Use FastAPI BackgroundTasks for now. |
| Full maintenance ticketing | Valuable but not the demo feature. Adds scope without strengthening the deposit evidence case. |
| Full tenant portal (complaints, notifications) | Tenant only needs check-in report access in MVP. Full portal is Phase 2. |
| UPI/Razorpay payment integration | Adds payment compliance overhead. Manual payment logging works for v1. |
| WhatsApp notifications | Email is sufficient for v1. WhatsApp requires approved business API — not worth the friction for 10 operators. |
| GraphQL | Add on top of stable REST in v2. |
| Mobile app | PWA is sufficient. Camera access works via browser on mobile. |
| KYC API / DigiLocker | V2 compliance feature. |
| Public listing / discovery | Needs operator critical mass. Premature. |
| Complex occupancy dashboards | Color-coded bed grid is enough. Charts and analytics are not the product. |

---

## 15. Reference Links

**Market Evidence**
- Deposit dispute viral thread: [businesstoday.in — April 2025](https://www.businesstoday.in/personal-finance/real-estate/story/the-biggest-scam-in-bengaluru-investment-advisor-calls-out-citys-rental-deposit-trap-472022-2025-04-15)
- Landlord vanishes without returning deposit (Reddit → Deccan Herald): [deccanherald.com — October 2025](https://www.deccanherald.com/india/karnataka/bengaluru/bengaluru-security-deposit-scam-landlord-vanishes-without-returning-deposit-to-tenant-3775530)
- BBMP PG crackdown, 94 PGs shut: [thehansindia.com — May 2025](https://www.thehansindia.com/amp/bengaluru/bbmp-plans-to-regulate-unauthorised-pgs-in-bengaluru-968661)
- Karnataka deposit law: [kots.world](https://www.kots.world/blog/security-deposit-rules-in-karnataka-legal-remedies-for-tenants-when-landlords-withhold-deposits-in-bangalore)
- Deposit legal framework (India): [sudhirrao.com](https://sudhirrao.com/pg-owner-not-refunding-your-security-deposit-heres-what-indian-law-says/)

**Competitor Research**
- RentOk (market leader, 15k+ operators): [rentok.com](https://rentok.com) — no condition reports confirmed
- SpaceBasic (institutional, not indie PGs): [spacebasic.com](https://spacebasic.com)
- HostelOS (legacy, no deposit protection): [hostelos.softweirdo.com](https://hostelos.softweirdo.com)

**Tech Documentation**
- FastAPI: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- SQLAlchemy 2.0 async: [docs.sqlalchemy.org](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- Alembic: [alembic.sqlalchemy.org](https://alembic.sqlalchemy.org)
- TanStack Query: [tanstack.com/query](https://tanstack.com/query/latest)
- Cloudflare R2: [developers.cloudflare.com/r2](https://developers.cloudflare.com/r2/)
- Railway deployment: [railway.app](https://railway.app)

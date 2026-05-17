# PGPal — Final Product Requirements Document
**Version:** 4.0 — Unified Final  
**Date:** May 2026  
**Status:** Build-ready  
**Consolidates:** v1.0 (initial), v2.0 (lean delta), v3.0 (AI enhancements), import spec, notification layer update

---

## 1. Executive Summary

PGPal is a workflow and trust infrastructure platform for independent PG (Paying Guest) operators in India — starting in Bengaluru.

It digitises the full lifecycle of a tenancy — from a prospective tenant's first inquiry to their final deposit refund — replacing WhatsApp groups, paper registers, and verbal agreements with a structured, evidence-based system.

**Who pays:** PG operators (B2B SaaS, ₹499–1,499/month per property). Tenants use the platform for free.

**The single clearest value proposition:** The next time a tenant threatens to take you to consumer court over their deposit, you open the app, show them the check-in photo of the room — taken together, signed by both parties, timestamped by the server. The conversation ends.

**What makes it defensible:** AI damage analysis between check-in and check-out photos, automated Leave & Licence agreement generation, AI-powered Excel import for instant onboarding, and an in-app notification centre for tenants.

---

## 2. Problem Statement — Real Market Evidence

### 2.1 The Scale of the Market
India's residential rental market is estimated between ₹1.5–1.65 lakh crore ($18–20 billion), with the student accommodation segment alone at approximately $10 billion. Bengaluru is the epicentre — a city where the technology workforce grows faster than formal housing can keep up, making PGs the default first housing choice.

### 2.2 The Root Cause Is Always the Same: No Evidence
Claims of 'damage' come with no evidence, no bills — just vague justifications. The Karnataka Rent Control Act is clear — landlords must return deposits within 30 days and furnish itemised receipts for any deductions. The law is not the problem. The evidence vacuum is.

PGPal's check-in/check-out condition report with timestamped photos, dual signatures, and **AI-powered damage comparison** is the direct, surgical solution to this exact mechanism.

### 2.3 Regulatory Compliance
BBMP is actively inspecting and shutting down unauthorized PGs. Operators who cannot produce tenant records, KYC documentation, and maintenance histories are exposed. PGPal directly addresses this compliance need.

---

## 3. Product Scope & Features

### 3.1 Core Workflow (MVP Foundation)
- **Property/Room/Bed Management**: Full CRUD to model the properties.
- **Tenancy State Machine**: Tracks tenants from Inquiry → Active → Notice Period → Vacated.
- **Condition Reports (Check-in/Check-out)**: 
  - Itemized checklist with photos for walls, floor, AC, bed, etc.
  - Immutable once signed by both parties via cryptographic timestamp.
  - Checkout diff comparison (Check-in vs Check-out).
  - Settlement PDF export.

### 3.2 AI Integrations & Advanced Features (Version 4.0 Additions)
Since AI is part of the final vision, these features integrate directly into the core workflow:

1. **AI Damage Analysis**:
   - When generating the check-out report, an integrated local Vision model (e.g., Qwen-VL or similar) compares the check-in and check-out photos.
   - The AI automatically highlights potential damages (scratches, stains, breakages) and suggests a confidence score, reducing manual inspection time.
   
2. **AI-Powered Excel Import**:
   - Operators can upload their existing unstructured Excel/CSV sheets.
   - A local LLM (e.g., Qwen2.5 / Gemma via E2B/Ollama) parses the arbitrary column names, extracts tenant details, rent amounts, deposit amounts, and room numbers, and maps them to the structured PGPal database automatically.

3. **Automated Leave & Licence Agreement Generation**:
   - Generates legal-grade rental agreements automatically based on the tenant's profile, rent, deposit, and the condition report data.

4. **In-App Notification Centre**:
   - A centralized hub for tenants and operators to view automated reminders for rent, notice periods, and document signings (replacing the need for Celery/Redis in MVP by using FastAPI BackgroundTasks).

---

## 4. Tenancy State Machine

```
INQUIRY ──► CONFIRMED ──► ACTIVE ──► NOTICE_PERIOD ──► VACATED
                │                          │
                └──────────────────────────┴──► CANCELLED
```

**Critical gate:** `confirmed → active` requires a signed check-in report. The app will not allow this transition without it.

---

## 5. Architecture & Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18 + Vite 5, Tailwind CSS, Shadcn/UI, TanStack Query |
| **Backend** | FastAPI 0.111+ (Async), Python |
| **Database** | PostgreSQL 16 (RLS, Triggers, ENUMs) |
| **ORM / Migrations**| SQLAlchemy 2.0 (Async) / Alembic |
| **AI Integration** | Local execution via Ollama/E2B (Qwen2.5 / Gemma / Vision models) |
| **File Storage** | Cloudflare R2 (for Condition Report photos) |
| **Containerisation**| Docker Compose (Postgres, pgAdmin, Backend, Frontend) |

---

## 6. Build Order & Milestones

### Milestone 1 — Database Foundation
- Scaffold FastAPI, SQLAlchemy, and Alembic.
- Build Postgres schema (Operators, Properties, Rooms, Beds, Tenants, Tenancies, Condition Reports).
- Implement database triggers for state machine rules and report immutability.

### Milestone 2 — Backend API Core & AI Skeleton
- JWT Auth (Operator + Tenant roles).
- Core CRUD APIs.
- Create `ai_services.py` layer connected to local Ollama endpoints for future use.

### Milestone 3 — Condition Reports & Frontend Scaffold
- Implement R2 Presigned URL uploads.
- Build Condition Report APIs and Diff calculation.
- Set up Vite + React frontend with Shadcn UI and routing.

### Milestone 4 — AI Excel Import & Advanced Features
- Build the AI Excel upload endpoint: Pass CSV/Excel data to Qwen2.5 for schema mapping.
- Implement the Tenant Notification centre.

### Milestone 5 — Check-out & AI Damage Analysis
- Integrate local Vision models into the check-out flow to analyze diffs between check-in and check-out photos.
- Generate the final PDF settlement report with WeasyPrint.

---

## 7. Success Metrics
- **Adoption:** 10+ operators onboarded in target areas (Koramangala/HSR).
- **Usage:** >70% of active tenancies have a fully signed check-in report.
- **AI Utility:** >80% accuracy in AI Excel imports without operator correction.
- **Dispute Resolution:** Operators explicitly cite PGPal timestamped photos as the reason a deposit dispute was successfully mediated.

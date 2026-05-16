# PGPal — Final Product Requirements Document
**Version:** 4.0 — Final  
**Date:** May 2026  
**Status:** Build-ready  
**Consolidates:** v1.0 (initial), v2.0 (lean delta), v3.0 (AI enhancements), import spec, notification layer update

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement — Research & Evidence](#2-problem-statement--research--evidence)
3. [Market & Competitor Landscape](#3-market--competitor-landscape)
4. [Product Vision & Positioning](#4-product-vision--positioning)
5. [User Personas](#5-user-personas)
6. [Feature Scope — All Phases](#6-feature-scope--all-phases)
7. [Feature Specifications — MVP](#7-feature-specifications--mvp)
8. [Feature Specifications — Phase 2](#8-feature-specifications--phase-2)
9. [Feature Specifications — Phase 3](#9-feature-specifications--phase-3)
10. [Tenancy State Machine](#10-tenancy-state-machine)
11. [Notification System](#11-notification-system)
12. [Data Model — Full Schema](#12-data-model--full-schema)
13. [API Surface](#13-api-surface)
14. [Tech Stack](#14-tech-stack)
15. [Non-Functional Requirements](#15-non-functional-requirements)
16. [Build Order & Milestones](#16-build-order--milestones)
17. [Go-to-Market](#17-go-to-market)
18. [Success Metrics](#18-success-metrics)
19. [Out of Scope & Why](#19-out-of-scope--why)
20. [Reference Links](#20-reference-links)

---

## 1. Executive Summary

PGPal is a workflow and trust infrastructure platform for independent PG (Paying Guest) operators in India — starting in Bengaluru.

It digitises the full lifecycle of a tenancy — from a prospective tenant's first inquiry to their final deposit refund — replacing WhatsApp groups, paper registers, and verbal agreements with a structured, evidence-based system.

**Who pays:** PG operators (B2B SaaS, ₹499–1,499/month per property). Tenants use the platform for free.

**The single clearest value proposition:** The next time a tenant threatens to take you to consumer court over their deposit, you open the app, show them the check-in photo of the room — taken together, signed by both parties, timestamped by the server. The conversation ends.

**What makes it defensible:** AI damage analysis between check-in and check-out photos, automated Leave & Licence agreement generation, AI-powered Excel import for instant onboarding, and an in-app notification centre for tenants — none of which any existing Indian PG software does.

---

## 2. Problem Statement — Research & Evidence

### 2.1 The Scale of the Market

India's residential rental market is estimated between ₹1.5–1.65 lakh crore ($18–20 billion), with the student accommodation segment alone at approximately $10 billion. Bengaluru is the epicentre — a city where the technology workforce grows faster than formal housing can keep up, making PGs the default first housing choice for every fresher and young professional who arrives.

### 2.2 The Deposit Dispute Problem Is Mainstream

In April 2025, entrepreneur Varun Mayya posted on X: the deposit dispute at checkout is Bangalore's biggest scam — deposit withheld with invented damage claims, no evidence on either side. The post crossed a million views. Financial advisor AK Mandhan posted the same independently in the same quarter
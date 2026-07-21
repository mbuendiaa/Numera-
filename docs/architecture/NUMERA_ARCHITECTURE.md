# Numera Architecture

Version: 1.0

---

# Vision

Numera is an AI-first accounting platform built around business capabilities
rather than technical components.

The system follows:

- Domain-Driven Design (DDD)
- Clean Architecture
- Event-Driven Architecture
- Rich Domain Models
- CQRS (future)
- Event Sourcing friendly

The domain is the center of the application.

---

# High Level Architecture

```
                API
                 │
        Application Layer
                 │
         Domain (Business)
                 │
 Infrastructure (DB, OCR, AI)
```

Dependencies always point inwards.

The Domain never depends on FastAPI, SQLAlchemy or external services.

---

# Bounded Contexts

Core

- Identity
- Company
- Master Data
- Business Events

Business

- Purchase
- Sales
- Banking
- Assets
- Payroll
- Tax

Financial

- Accounting
- Ledger
- Reporting

Platform

- OCR
- AI
- Document Engine
- Storage

---

# Domain Principles

Every business capability owns:

- Aggregate Root
- Entities
- Value Objects
- Domain Events
- Repository Interface

Example:

Purchase

├── Aggregate
├── PurchaseInvoice
├── Payment
├── Money
├── SupplierReference
└── PurchaseCreated

---

# Layer Responsibilities

API

- HTTP
- Authentication
- DTOs

Application

- Use Cases
- Transactions
- Publish Domain Events

Domain

- Business Rules
- Aggregates
- Policies
- Value Objects

Infrastructure

- SQLAlchemy
- OCR
- AI
- Storage
- Repository implementations

---

# Event Flow

Example:

DocumentUploaded

↓

SupplierResolved

↓

InvoiceCreated

↓

PurchaseCreated

↓

JournalEntryProposed

↓

LedgerUpdated

↓

Reports

---

# Aggregate Rules

Aggregates are responsible for consistency.

Only Aggregates can change their internal state.

Never expose public setters.

Example:

purchase.approve()

instead of

purchase.status = APPROVED

---

# Repository Rule

Repositories belong to the Domain as interfaces.

Implementations belong to Infrastructure.

Domain

PurchaseRepository

Infrastructure

SQLAlchemyPurchaseRepository

---

# Domain Events

Aggregates emit Domain Events.

Example:

PurchaseApproved

PaymentRegistered

PurchasePaid

Aggregates never publish events.

Application Services publish events after persistence.

---

# Business Events

Business Events are persisted.

Purposes:

- Audit
- Timeline
- AI reasoning
- Debugging
- Replay

---

# Coding Rules

Never use floats for money.

Use Value Objects.

Avoid primitive obsession.

Prefer explicit business concepts over strings.

Example:

Money

SupplierReference

InvoiceReference

JournalReference

---

# Long Term Roadmap

Purchase

Sales

Banking

Assets

Payroll

Tax

General Ledger

Financial Statements

AI Copilot

Forecasting

Cash Flow

Budgeting

Consolidation

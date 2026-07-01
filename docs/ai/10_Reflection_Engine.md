# NUMERA

# AI-09 Agent Model

---

**Document ID:** AI-09

**Version:** 0.1

**Status:** Draft

**Created:** 2026-06-29

**Owner:** Founding Team

---

# Purpose

This document defines how specialised agents operate inside Numera.

Numera is not a single AI assistant.

Numera is a coordinated system of specialised financial agents working under the supervision of the Numera Brain.

Each agent has a clear responsibility, a limited scope and defined interaction rules.

---

# Philosophy

A single agent cannot safely understand every financial process.

Specialisation creates reliability.

Coordination creates intelligence.

Numera agents must behave like a professional finance team:

* each agent owns a domain;
* agents collaborate when needed;
* no agent acts outside its authority;
* high-risk actions require approval;
* the Brain coordinates the whole system.

---

# Core Principle

Agents do not own the company truth.

The Enterprise Knowledge Universe owns the truth.

Agents query, interpret and update knowledge under governance.

---

# Agent Hierarchy

```text
Numera Brain
     ↓
AI Orchestrator
     ↓
Specialised Agents
     ↓
Tools / Engines / Integrations
```

Agents never bypass the Brain for critical actions.

---

# Initial Agent Types

## Document Agent

Responsible for understanding incoming documents.

Tasks:

* classify documents;
* extract relevant fields;
* identify missing information;
* detect document quality issues;
* route documents to the correct agent.

---

## Invoice Agent

Responsible for invoice-specific interpretation.

Tasks:

* identify supplier/customer;
* validate invoice number;
* detect duplicates;
* identify bases and taxes;
* analyse invoice lines;
* determine invoice type.

---

## Accounting Agent

Responsible for accounting interpretation.

Tasks:

* propose journal entries;
* select accounts;
* validate account structure;
* check balancing;
* explain accounting treatment.

---

## Tax Agent

Responsible for tax reasoning.

Tasks:

* validate VAT;
* identify withholding;
* detect reverse charge;
* identify intracommunity transactions;
* flag tax risks.

---

## Treasury Agent

Responsible for liquidity and payment reasoning.

Tasks:

* analyse due dates;
* evaluate cash impact;
* detect upcoming payments;
* support payment planning.

---

## Reconciliation Agent

Responsible for matching financial movements.

Tasks:

* match bank transactions with invoices;
* detect unmatched payments;
* identify partial payments;
* flag reconciliation exceptions.

---

## Memory Agent

Responsible for memory governance.

Tasks:

* create candidate memories;
* retrieve relevant memories;
* detect obsolete memories;
* identify memory conflicts;
* update memory confidence.

---

## Audit Agent

Responsible for traceability and control.

Tasks:

* verify decision logs;
* detect missing approvals;
* review high-risk actions;
* generate audit explanations.

---

## Planning Agent

Responsible for execution plans.

Tasks:

* decompose actions;
* define dependencies;
* request approvals;
* prepare rollback steps;
* coordinate execution order.

---

## Conversation Agent

Responsible for natural language interaction.

Tasks:

* interpret user questions;
* retrieve company knowledge;
* explain decisions;
* guide users through workflows.

---

# Agent Responsibilities

Every agent must define:

* domain;
* inputs;
* outputs;
* tools allowed;
* memory access;
* rules access;
* confidence requirements;
* escalation triggers.

Undefined responsibility is not allowed.

---

# Agent Boundaries

Agents may recommend.

Agents may analyse.

Agents may prepare.

Agents may not independently execute high-risk actions.

Examples:

The Tax Agent may flag a VAT risk.

It may not submit tax information without approval.

The Treasury Agent may prepare a payment recommendation.

It may not execute bank transfers without authorisation.

---

# Collaboration Model

Agents collaborate through structured messages.

Example:

Document Agent

↓

Invoice Agent

↓

Accounting Agent

↓

Tax Agent

↓

Confidence Engine

↓

Planning Agent

↓

Audit Agent

Each agent contributes a specialised interpretation.

---

# Agent Communication

Agent communication must be structured.

Each message includes:

* sender;
* recipient;
* task;
* input data;
* conclusion;
* confidence;
* evidence;
* open questions;
* recommended next step.

Free-form hidden conversations are not acceptable for critical workflows.

---

# Agent Memory Access

Agents access memory according to scope.

Example:

Invoice Agent may access supplier invoice memory.

Tax Agent may access fiscal memory.

Conversation Agent may access explanatory memory but not sensitive internal controls unless authorised.

Access must respect permissions.

---

# Agent Tool Access

Agents only use tools explicitly assigned to them.

Example:

Document Agent may use OCR tools.

Accounting Agent may use chart-of-accounts tools.

Treasury Agent may use banking data tools.

Tool access is part of security.

---

# Escalation

Agents escalate when:

* confidence is low;
* rules conflict;
* risk is high;
* data is missing;
* another agent must contribute;
* human approval is required.

Escalation prevents silent failure.

---

# Agent Evaluation

Every agent is evaluated using:

* accuracy;
* confidence calibration;
* correction rate;
* escalation quality;
* explanation quality;
* processing time;
* user trust.

---

# Failure Modes

Possible failures:

* agent acts outside scope;
* agent ignores rules;
* agent overuses memory;
* agent produces unexplained conclusions;
* agent fails to escalate uncertainty.

These failures must be monitored.

---

# Human-in-the-loop

Agents support human professionals.

They do not remove professional accountability.

The system should make it easy for users to understand which agent produced a recommendation and why.

---

# Future Evolution

Future agents may include:

* Payroll Agent;
* Procurement Agent;
* Budget Agent;
* Forecasting Agent;
* Investor Reporting Agent;
* Compliance Agent;
* ERP Integration Agent;
* Pricing Intelligence Agent.

Agents should be added only when a specialised domain requires ownership.

---

# Success Criteria

The Agent Model succeeds when:

* responsibilities remain clear;
* workflows are easier to explain;
* errors are easier to isolate;
* new domains can be added safely;
* agent behaviour remains auditable.

---

# Closing Statement

Numera is not a single AI system.

Numera is a coordinated intelligence organisation.

The Brain coordinates.

Agents specialise.

Engines govern.

Humans supervise.

This model allows Numera to grow without becoming chaotic.

# NUMERA

# AI-07 Rule Engine

---

**Document ID:** AI-07

**Version:** 0.1

**Status:** Draft

**Created:** 2026-06-29

**Owner:** Founding Team

---

# Purpose

The Rule Engine is responsible for evaluating deterministic business rules independently from Artificial Intelligence.

Its mission is to ensure that every recommendation produced by Numera complies with accounting principles, company policies, legal constraints and operational requirements.

The Rule Engine defines what is allowed.

The Reasoning Engine decides what is most appropriate.

---

# Philosophy

Rules represent certainty.

AI represents interpretation.

Rules must always have priority whenever legislation, accounting standards or company policies define a deterministic outcome.

Numera must never ignore a valid rule because an AI model suggested something different.

---

# Objectives

The Rule Engine must:

* validate business constraints;
* prevent invalid operations;
* enforce company policies;
* support explainable reasoning;
* remain fully versioned;
* remain independently testable.

---

# Categories of Rules

## Accounting Rules

Examples:

* Journal entries must balance.
* VAT codes must exist.
* Accounts must belong to the Chart of Accounts.
* Closed accounting periods cannot be modified.

---

## Fiscal Rules

Examples:

* VAT validation.
* Reverse charge.
* Intracommunity transactions.
* Tax withholding.
* Local fiscal legislation.

---

## Company Rules

Examples:

* Purchases above €5,000 require approval.
* Fuel invoices use cost centre 120.
* Foreign invoices require manual review.
* Payroll entries cannot be automated.

---

## User Rules

Examples:

* Junior accountants cannot approve payments.
* Controllers review month-end adjustments.
* Treasury users cannot modify accounting rules.

---

## Workflow Rules

Examples:

* An invoice must be approved before posting.
* Payment cannot occur before posting.
* Documents cannot be archived before reconciliation.

---

## Security Rules

Examples:

* User permissions.
* Multi-factor authentication.
* Sensitive document access.
* Segregation of duties.

---

# Rule Structure

Every rule contains:

* Rule ID
* Name
* Category
* Description
* Trigger
* Condition
* Action
* Priority
* Severity
* Company Scope
* Version
* Effective Date
* Expiration Date
* Owner
* Status

---

# Rule Lifecycle

Every rule follows:

Draft

↓

Review

↓

Approved

↓

Active

↓

Deprecated

↓

Archived

Historical versions remain available for auditing.

---

# Rule Evaluation

Rules are evaluated before any execution.

Example:

Receive invoice

↓

Validate mandatory fields

↓

Validate supplier

↓

Validate VAT

↓

Validate approval policy

↓

Pass to Reasoning Engine

Only compliant inputs reach the cognitive layer.

---

# Rule Priorities

Critical

System cannot continue.

Example:

Accounting period closed.

---

High

Execution blocked until corrected.

Example:

Missing VAT number.

---

Medium

Recommendation generated.

Human review suggested.

---

Low

Warning only.

No execution blocked.

---

# Rule Versioning

Every rule is versioned.

Changes include:

* previous version;
* new version;
* author;
* approval date;
* reason for change.

Historical decisions remain linked to the rule version used at the time.

---

# Rule Explainability

Whenever a rule affects a decision, Numera explains it.

Example:

"Posting blocked because company policy requires Finance Director approval for invoices above €5,000."

---

# Rule Conflicts

Conflicts may occur.

Example:

Company Rule

↓

Auto-post invoices under €3,000.

Fiscal Rule

↓

Manual review required for foreign suppliers.

Fiscal rule overrides company rule.

Conflict resolution must be explicit.

---

# Rule Hierarchy

Default priority:

1. Legal requirements
2. Accounting standards
3. Security policies
4. Company policies
5. User preferences
6. AI recommendations

AI never overrides mandatory rules.

---

# Rule Repository

Rules are stored centrally.

Every company has its own rule repository.

Shared rule libraries may exist for:

* IFRS
* Local GAAP
* VAT legislation
* Industry templates

---

# Testing

Every rule must be testable.

Rule changes require automated regression tests.

A modified rule must never create unexpected behaviour elsewhere.

---

# Integration with the Cognitive System

The Rule Engine collaborates with:

* Understanding Engine
* Memory Engine
* Context Engine
* Reasoning Engine
* Confidence Engine
* Planning Engine

Rules constrain reasoning.

They do not replace it.

---

# Future Evolution

Future versions may include:

* visual rule editor;
* rule simulation;
* dependency graphs;
* rule impact analysis;
* natural language rule generation with human approval.

---

# Success Criteria

The Rule Engine succeeds when:

* company policies are consistently enforced;
* legal compliance is maintained;
* explanations remain transparent;
* rule maintenance becomes simple;
* AI recommendations remain governed.

---

# Closing Statement

Rules are the foundation of trust.

Artificial Intelligence provides flexibility.

Rules provide certainty.

Numera combines both to deliver intelligent, explainable and compliant financial decisions.

# NUMERA

# AI-04 Context Engine

---

**Document ID:** AI-04

**Version:** 0.1

**Status:** Draft

**Created:** 2026-06-29

**Owner:** Founding Team

---

# Purpose

The Context Engine determines the current business situation in which Numera must reason and act.

Information without context is ambiguous.

The same document may require different decisions depending on when, where and why it is processed.

The Context Engine provides the situational awareness required by the Numera Brain.

---

# Philosophy

Knowledge answers:

"What is generally true?"

Memory answers:

"What happened before?"

Context answers:

"What is happening right now?"

Correct decisions require all three.

---

# Objectives

The Context Engine must:

* understand the current business situation;
* provide relevant information to the Reasoning Engine;
* reduce ambiguity;
* adapt recommendations dynamically;
* detect exceptional situations.

---

# Context Categories

## Temporal Context

Examples:

* Current date
* Accounting period
* Fiscal year
* Month-end closing
* Quarter-end
* Year-end
* VAT submission period

Time influences every financial decision.

---

## Organisational Context

Examples:

* Active company
* Department
* Cost centre
* Business unit
* Country
* Currency

Different organisations may follow different accounting policies.

---

## User Context

Examples:

* User role
* Permissions
* Previous actions
* Experience level
* Approval authority

A Finance Director and an Accountant may receive different recommendations.

---

## Workflow Context

Examples:

* Invoice received
* Pending approval
* Posted
* Paid
* Archived

The same invoice has different meanings throughout its lifecycle.

---

## Operational Context

Examples:

* Supplier onboarding
* Month-end closing
* Internal audit
* External audit
* Budget preparation
* Treasury review

Operational activities influence priorities.

---

## Financial Context

Examples:

* Cash position
* Outstanding liabilities
* Payment due dates
* Budget utilisation
* Credit exposure

Financial conditions influence recommendations.

---

## Regulatory Context

Examples:

* VAT regime
* Country-specific legislation
* IFRS
* Local GAAP
* Reporting obligations

Regulatory context constrains valid actions.

---

# Context Resolution

The Context Engine combines multiple sources.

Context is never determined by a single variable.

Example:

Invoice

↓

Supplier

↓

Current Month

↓

User

↓

Company

↓

Fiscal Calendar

↓

Active Workflow

↓

Context

---

# Dynamic Context

Context changes continuously.

Examples:

Today:

Normal processing.

Tomorrow:

Month-end closing.

Same invoice.

Different context.

Different recommendation.

---

# Context Priority

When multiple contexts conflict, Numera resolves them using priority rules.

Typical priority:

1. Legal constraints
2. Security
3. Company policy
4. Workflow state
5. User preferences

---

# Context Expiration

Some contexts are permanent.

Examples:

Country.

Currency.

Company.

Others are temporary.

Examples:

Month-end closing.

Annual audit.

Urgent payment campaign.

Temporary contexts expire automatically.

---

# Context and Memory

Memory never replaces context.

Memory says:

"This supplier usually invoices monthly."

Context says:

"Today is the last day before VAT submission."

Both are required.

---

# Context and Reasoning

The Reasoning Engine receives context as structured information.

Reasoning without context is incomplete.

Context narrows the solution space.

---

# Explainability

Whenever context influences a recommendation, Numera explains why.

Example:

"This invoice requires manual approval because month-end closing is currently active."

---

# Future Evolution

Future versions may incorporate:

* macroeconomic context;
* banking market conditions;
* seasonal business patterns;
* AI-generated operational context;
* predictive context.

---

# Success Criteria

The Context Engine succeeds when:

* recommendations adapt naturally to changing situations;
* unnecessary user questions decrease;
* incorrect automations caused by missing context are reduced;
* explanations become more relevant.

---

# Closing Statement

The Context Engine provides situational awareness.

Knowledge explains the business.

Memory explains the past.

Context explains the present.

Together they allow Numera to make decisions that are accurate, timely and relevant.

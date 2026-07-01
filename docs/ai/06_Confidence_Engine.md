# NUMERA

# AI-06 Confidence Engine

---

**Document ID:** AI-06

**Version:** 0.1

**Status:** Draft

**Created:** 2026-06-29

**Owner:** Founding Team

---

# Purpose

The Confidence Engine estimates how reliable every recommendation produced by Numera is.

Confidence is not a probability.

Confidence is an explanation of how much evidence supports a decision.

Its purpose is to determine whether Numera can safely automate, recommend or request human intervention.

---

# Philosophy

Confidence is earned.

Not assumed.

Every recommendation must justify its confidence through observable evidence.

The objective is not to maximise confidence.

The objective is to estimate it honestly.

---

# Core Objectives

The Confidence Engine must:

* estimate decision reliability;
* explain confidence composition;
* detect uncertainty;
* trigger human review when required;
* improve through continuous feedback.

---

# Confidence Components

Confidence is calculated using multiple dimensions.

## Data Quality

Measures the quality of incoming information.

Examples:

* OCR quality
* Missing fields
* Image resolution
* XML validation
* Document completeness

---

## Knowledge Confidence

Measures how well Numera understands the entities involved.

Examples:

* Known supplier
* Known customer
* Existing products
* Historical accounting behaviour

---

## Memory Confidence

Measures how strong company memories are.

Examples:

* Previous approvals
* Historical corrections
* Stable accounting patterns

---

## Rule Confidence

Evaluates deterministic validation.

Examples:

* VAT validation
* Fiscal rules
* Company policies
* Approval thresholds

Rules either pass or fail.

Failures reduce confidence significantly.

---

## Context Confidence

Measures whether current business context supports the recommendation.

Examples:

* Month-end closing
* Audit period
* New supplier
* Exceptional workflow

---

## Reasoning Confidence

Measures agreement between competing hypotheses.

Example:

H1 Office Supplies → 91%

H2 Subscription → 12%

High separation produces higher confidence.

Small differences indicate ambiguity.

---

## Historical Accuracy

Confidence increases when similar decisions have repeatedly been accepted.

Repeated corrections reduce confidence.

Learning influences future confidence.

---

# Confidence Calculation

Confidence is not a single formula.

It is a weighted aggregation of evidence.

Illustrative example:

Data Quality: 98

Knowledge: 96

Memory: 92

Rules: 100

Context: 94

Reasoning: 89

Historical Accuracy: 95

Overall Confidence: 95%

The calculation method must remain configurable.

---

# Confidence Levels

## Level A (95–100%)

Safe automation.

Automatic execution permitted if company policy allows.

---

## Level B (85–94%)

Recommendation presented.

Automation allowed depending on workflow.

---

## Level C (70–84%)

User confirmation recommended.

Additional explanation displayed.

---

## Level D (50–69%)

Manual review required.

System highlights uncertainty.

---

## Level E (<50%)

No recommendation.

Numera requests more information.

---

# Explainability

Every confidence score must include its composition.

Example:

Recommendation confidence: 93%

Built from:

✔ OCR Quality: 99%

✔ Supplier History: 98%

✔ Accounting Pattern: 94%

✔ VAT Validation: 100%

⚠ New Cost Centre: 63%

This allows users to understand uncertainty.

---

# Confidence Decay

Confidence changes over time.

Reasons include:

* supplier behaviour changes;
* new accounting policy;
* legal updates;
* repeated corrections;
* obsolete memories.

Confidence must evolve.

---

# Confidence Recovery

Confidence can increase again.

Examples:

* repeated successful approvals;
* consistent behaviour;
* new validated memories;
* updated accounting rules.

The engine should reward stability.

---

# Human Feedback

Every user action affects confidence.

Accepted recommendation

↓

Confidence increases.

Corrected recommendation

↓

Confidence decreases.

Rejected recommendation

↓

Confidence decreases significantly.

Feedback closes the learning loop.

---

# Confidence Thresholds

Every company may configure:

* automatic posting threshold;
* payment threshold;
* approval threshold;
* tax threshold;
* banking threshold.

Confidence policy is company-specific.

---

# Confidence Dashboard

Administrators should be able to analyse:

* average confidence;
* confidence trends;
* low-confidence areas;
* supplier confidence;
* document confidence;
* user corrections.

This enables continuous improvement.

---

# Safety Rules

Confidence never overrides business rules.

High confidence cannot bypass:

* fiscal restrictions;
* approval policies;
* security permissions;
* legal obligations.

Confidence supports decisions.

It does not replace governance.

---

# Future Evolution

Future versions may include:

* Bayesian confidence updates;
* confidence calibration models;
* confidence benchmarking;
* adaptive confidence thresholds;
* predictive uncertainty estimation.

---

# Success Criteria

The Confidence Engine succeeds when:

* users trust recommendations;
* unnecessary confirmations decrease;
* unsafe automation becomes rare;
* confidence reflects real-world accuracy.

---

# Closing Statement

Confidence is the bridge between reasoning and trust.

Numera should never say:

"I am 95% confident."

It should say:

"I recommend this decision because these pieces of evidence support it, and here is why I believe it is safe."

Trust grows from transparency.

Confidence is how Numera communicates uncertainty.

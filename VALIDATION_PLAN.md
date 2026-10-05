# Vireo Audio — Analytics & Model Validation Plan

**Document Status:** Approved Operational Test Specification (Stage 3)  
**Scope:** Data Integrity, Pipeline Normalization, Metric Calculations, NLP/AI Component  
**Dataset:** 11,750 Helpdesk Tickets (1 Jan 2025 – 30 Jun 2026)  
**Author:** Antigravity AI  

---

## 1. Overview & Verification Objectives

This document establishes the formal validation protocol to verify that all analytical pipelines, metric engines, financial ledgers, and NLP/AI components built for Vireo Audio are mathematically correct, reproducible, and compliant with `support-policy.pdf` and `email-thread.txt`.

The validation plan consists of two core tiers:
1. **Automated Deterministic Verification Suite:** 10 quantitative invariants tested against raw database exports.
2. **Qualitative NLP & Telephony Sampling Protocol:** A structured 50-ticket stratified audit plan to validate text extraction, category classification, and junk IVR handling.

---

## 2. Deterministic Verification Checks

Every data build or dashboard pipeline execution must pass the following deterministic assertions without exception:

```
+-----------------------------------------------------------------------------------------------------------------------+
| TABLE 1: DETERMINISTIC SYSTEM INTEGRITY CHECKLIST                                                                     |
+----+--------------------------------+--------------------------------------+---------------------+--------------------+
| #  | Verification Domain            | Assertion / Formula                  | Expected Value      | Severity if Failed |
+----+--------------------------------+--------------------------------------+---------------------+--------------------+
| 1  | Ticket Row-Count Integrity     | count(tickets.csv)                   | Exactly 11,750      | CRITICAL (Halt)    |
| 2  | Orders Row-Count Integrity     | count(orders.csv)                    | Exactly 15,500      | CRITICAL (Halt)    |
| 3  | Customers Row-Count Integrity  | count(customers.csv)                 | Exactly 9,500       | CRITICAL (Halt)    |
| 4  | Agents Row-Count Integrity     | count(agents.csv)                    | Exactly 44          | CRITICAL (Halt)    |
| 5  | Products Row-Count Integrity   | count(products.csv)                  | Exactly 14          | CRITICAL (Halt)    |
+----+--------------------------------+--------------------------------------+---------------------+--------------------+
| 6  | Foreign Key Referencing Audit  | count(unmatched customer/agent/sku)  | Exactly 0 orphans   | CRITICAL (Halt)    |
+----+--------------------------------+--------------------------------------+---------------------+--------------------+
| 7  | Legacy Timestamp Normalization | count(legacy_fd handle_time < 0)     | Exactly 0 residual  | HIGH (Pipeline)    |
+----+--------------------------------+--------------------------------------+---------------------+--------------------+
| 8  | First-Response SLA Breaches    | count(response_time > target)        | Exactly 1,064       | HIGH (Calculations)|
+----+--------------------------------+--------------------------------------+---------------------+--------------------+
| 9  | SLA Credit P&L Liability       | sum(is_breached * ₹350)              | Exactly ₹372,400.00 | HIGH (Financial)   |
+----+--------------------------------+--------------------------------------+---------------------+--------------------+
| 10 | Completed Attendance CSAT Mean | mean(csat | status in [res, cls])    | 3.3259 (~3.33)      | HIGH (Calculations)|
+----+--------------------------------+--------------------------------------+---------------------+--------------------+
| 11 | Agent Display Name Disambig.   | join on agent_id (A3006 vs A3029)    | Unique agents = 44  | CRITICAL (Legal)   |
+----+--------------------------------+--------------------------------------+---------------------+--------------------+
| 12 | Direct Refund Financial Sum    | sum(tickets.refund_amount_inr)       | Exactly ₹5,350,871  | HIGH (Financial)   |
+----+--------------------------------+--------------------------------------+---------------------+--------------------+
| 13 | Policy Replacement Spend Sum   | sum(repl_issued * (cost + 340))      | Exactly ₹3,415,990  | HIGH (Financial)   |
+----+--------------------------------+--------------------------------------+---------------------+--------------------+
| 14 | Internal Transfer Cost Sum     | sum(transfers * ₹305)                | Exactly ₹370,575.00 | HIGH (Financial)   |
+----+--------------------------------+--------------------------------------+---------------------+--------------------+
```

---

### Detailed Test Specifications:

### 2.1. Ingestion & Relational Join Integrity
- **Test 1: Primary Key Uniqueness:**
  $$\text{assert } \text{tickets['ticket\_id'].nunique()} == 11750$$
  $$\text{assert } \text{agents['agent\_id'].nunique()} == 44$$
- **Test 2: Agent Disambiguation Check:**
  - Verify that query filtering for `name == 'Kavya Pandey'` returns **2 distinct agent records**:
    - `A3006` (Site: Indore, Team: Chat Frontline, Tier: 1)
    - `A3029` (Site: Bengaluru, Team: Voice Frontline, Tier: 1)
  - Assert that all ticket joins merge strictly on `agent_id`. Any merge on `name` must trigger an immediate build failure.
- **Test 3: Foreign Key Referential Integrity:**
  - `tickets.customer_id` $\subset$ `customers.customer_id` (0 orphans).
  - `tickets.agent_id` $\subset$ `agents.agent_id` (0 orphans).
  - `tickets.product_sku` $\subset$ `products.sku` (0 orphans).
  - For non-null `tickets.order_id`: `order_id` $\subset$ `orders.order_id` (0 orphans).

---

### 2.2. Timestamp Normalization Verification
- **Test 4: Legacy Handle Time Verification:**
  - For `legacy_fd` tickets, raw resolution timestamps reconstructed from event logs were recorded in UTC.
  - Normalization rule:
    $$\text{resolved\_at}_{\text{norm}} = \text{resolved\_at} + 5.5\text{ hours} \quad \forall \text{ legacy\_fd}$$
  - Assert that before normalization, exactly **2,309 tickets** have raw negative handle times.
  - Assert that post-normalization, **0 tickets** have negative handle times.
- **Test 5: Handle Time Exclusion for Unresolved Tickets:**
  - Assert that handle time is evaluated as `NaN` (null) for all 567 `open` and `pending` tickets.
  - Assert that unresolved tickets are never assigned 0 handle time.

---

### 2.3. CSAT & Metric Verification
- **Test 6: Blank CSAT Handling:**
  - Assert that tickets with null `csat_score` total exactly **6,554 rows**.
  - Assert that blank scores are excluded from all agent and company averages.
  - Verify that global CSAT is reported as **3.33** (never 1.47).
- **Test 7: Attendance CSAT Filtering:**
  - Assert that agent scorecard CSAT includes only completed tickets (`status` $\in$ `['resolved', 'closed']`).
  - Verify that the 249 CSAT responses on `open` and `pending` tickets are segregated from attendance performance.

---

### 2.4. Financial Ledger Reconciliation
- **Test 8: SLA Credit Liability Audit:**
  - Chat SLA breaches (target > 15m): 401 breaches.
  - Email SLA breaches (target > 480m): 445 breaches.
  - Voice SLA breaches (target > 120m): 117 breaches.
  - Social SLA breaches (target > 240m): 101 breaches.
  - Total Breaches = 1,064. Total Liability = $1,064 \times ₹350 = \mathbf{₹372,400.00}$.
- **Test 9: Cost Formula Compliance:**
  - Replacement cost must evaluate using Policy §5 formula (`unit_cost` + ₹340).
  - Assert total company replacement cost = **₹3,415,990.00**.
  - Verify that Arjun Mehta's flat ₹2,500 estimate (₹4,740,000.00) is flagged as an unapproved budgeting benchmark with a documented ₹1,324,010.00 (+38.7%) variance.

---

## 3. Qualitative Validation: NLP / Text Analysis & Telephony Protocol

If automated text mining, issue extraction, or sentiment analysis is deployed (running locally with ₹0 per-ticket API costs), it must be verified via the following protocol:

### 3.1. Junk IVR / Telephony System Error Quarantine
- **System Failure Baseline:** ~40 tickets contain corrupt phone system recordings rather than genuine customer feedback (as flagged by Sameer Qureshi).
- **Validation Rule:**
  - Any customer message matching:
    1. Bracketed telephony artifacts: `[line dropped]`, `[inaudible]`, `[crosstalk]`
    2. Single punctuation / placeholder text: `-`, `.`, `...`, `??`, `test`
    3. Truncated audio string lengths $\le 5$ characters
  - **Must be classified as:** `Telephony Ingestion Error (Junk IVR)`.
  - **Behavioral Constraint:** These tickets must be quarantined from voice agent behavioral scorecards and not attributed to agent conduct.

---

### 3.2. Stratified 50-Ticket Manual Gold-Standard Sample Plan
To validate automated category tagging, issue detection, and sentiment analysis against real ground truth:

1. **Sampling Methodology:**
   Draw a reproducible pseudo-random sample of 50 tickets stratified across channels and categories:
   - **Chat:** 20 tickets
   - **Email:** 15 tickets
   - **Voice:** 10 tickets (including at least 3 known IVR dropped calls)
   - **Social:** 5 tickets
   - *Sampling Seed:* `random_state = 42`.

2. **Evaluation Protocol:**
   A human reviewer will independently audit the 50 tickets and record:
   - True Primary Issue (e.g., Battery Drain, Case Charging, Pairing, Delivery Delay, Duplicate Payment)
   - True Root Cause (Hardware / Firmware / Logistics / Billing / User Education)
   - Customer Distress Level (High / Medium / Low)

3. **Acceptance Thresholds:**
   ```
   +------------------------------------+--------------------+-----------------------+
   | NLP / Automated Tagging Metric     | Minimum Threshold  | Rejection Criterion   |
   +------------------------------------+--------------------+-----------------------+
   | Primary Category Accuracy          | >= 90.0% (45 / 50) | Tagging model refit   |
   | Hardware Defect Identification     | >= 94.0% (47 / 50) | RMA rule overhaul     |
   | Telephony Junk Recall              | 100.0% (All IVRs)  | Regex filter failure  |
   +------------------------------------+--------------------+-----------------------+
   ```

4. **Zero Per-Ticket Cost Enforcement:**
   - Verify that all classification scripts execute on-device using local Python, regex, and lightweight scikit-learn models.
   - Assert zero external API calls to avoid violating Arjun Mehta's budget directive.

---

## 4. Test Execution Sign-Off Procedure

Before presenting the final dashboard to stakeholders:
1. Run automated test suite: `python validate_pipeline.py`.
2. Inspect test log output; verify 100% assertions return `PASS`.
3. Check manual sample review sheet; verify $\ge 90\%$ accuracy.
4. Record validation timestamp and software version in release notes.

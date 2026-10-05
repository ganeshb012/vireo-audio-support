# Vireo Audio — Support Desk Analytics Methodology & Standards

**Document Status:** Approved Analytical Specification  
**Project:** Vireo Audio — Support Tickets (Set B) Assessment  
**Reference Documents:** `support-policy.pdf` (v3.2), `email-thread.txt`, `VIREO AUDIO — SUPPORT DATA PACK.txt`  
**Author:** Antigravity AI  

---

## 1. Customer Satisfaction (CSAT)

### 1.1. Exact Mathematical Formula
For any cohort, agent, team, or channel $A$:

$$\text{CSAT}(A) = \frac{\sum_{i \in T_{\text{valid}}(A)} \text{csat\_score}_i}{|T_{\text{valid}}(A)|}$$

Where:
- $\text{csat\_score}_i \in \{1, 2, 3, 4, 5\}$
- $T_{\text{valid}}(A) = \{i \in T(A) \mid \text{csat\_score}_i \text{ is not null}\}$

### 1.2. Tickets Included vs. Excluded
- **Included Tickets:** Only tickets with an explicit integer survey rating ($1, 2, 3, 4, \text{ or } 5$) are included in the numerator and denominator.
- **Handling of Blank CSAT:**
  - As mandated by **Support Policy §8**: *"A blank score means no response and must be excluded from averages, not treated as zero."*
  - Out of 11,750 total tickets, **6,554 tickets (55.78%) have blank CSAT**.
  - Blank values must **never** be imputed with 0, mean values, or medians. Imputing zero would artificially drag the company CSAT down from **3.33** to an invalid **1.47**.
- **Open / Pending Tickets Anomaly:**
  - Policy §8 notes surveys are dispatched upon ticket resolution or 72-hour auto-closure.
  - However, 249 tickets in `open` (150) or `pending` (99) status contain recorded CSAT scores (mean: 3.34).
  - *Standard Rule:* For strict attendance evaluation (Policy §10), CSAT should be reported on completed attendances (`status` in `['resolved', 'closed']`). For agent feedback analysis, valid scores on open/pending tickets are logged as an operational telemetry note without corrupting final attendance scorecards.

---

## 2. Handle Time

### 2.1. Exact Mathematical Formula
Per **Support Policy §10**: *"Handle time: first response to resolution."*

$$\text{Handle Time (hours)} = \frac{\text{resolved\_at}_{\text{normalized}} - \text{first\_response\_at}}{3,600 \text{ seconds}}$$

$$\text{Handle Time (days)} = \frac{\text{Handle Time (hours)}}{24}$$

### 2.2. Treatment of Open and Pending Tickets
- Tickets with `status == 'open'` (335 tickets) or `status == 'pending'` (232 tickets) have a null `resolved_at`.
- Handle time is **undefined (null)** for unresolved tickets.
- They are **strictly excluded** from handle time calculations. They must not be set to 0 (which would falsely imply instantaneous resolution) or calculated against the current timestamp (which would introduce data-drift artifacts).

### 2.3. Legacy Timestamp Normalization (`legacy_fd`)
- **System Discrepancy (Policy §9):**
  - Tickets prior to 14 September 2025 originate from `legacy_fd` (Freshdesk).
  - In `legacy_fd`, `created_at` and `first_response_at` were recorded in **IST**, but reconstructed `resolved_at` was extracted from the legacy event log in **UTC**.
  - Because IST is $\text{UTC} + 5:30$, subtracting an unadjusted UTC timestamp from an IST timestamp produces **2,309 negative handle times** (e.g., $-5.28$ hours).
- **Mandatory Normalization Formula:**
  For all tickets where `source_system == 'legacy_fd'` and `resolved_at` is not null:

  $$\text{resolved\_at}_{\text{normalized}} = \text{resolved\_at} + 5\text{ hours } 30\text{ minutes}$$

- **Verification:** Applying this exact $+5\text{h }30\text{m}$ offset eliminates **100% of negative handle times** across the dataset (0 negative values remaining). It harmonizes the legacy median handle time to **0.43 hours (26 mins)**, consistent with the current helpdesk median of **0.50 hours (30 mins)**.

### 2.4. Impossible / Negative Values Policy
- Post-normalization, any residual handle time $\le 0$ represents an uncorrectable database defect and must be quarantined with an audit flag. (In this dataset, exactly 0 residual negative handle times remain after normalization).

---

## 3. First-Response Service Levels & SLA Breaches

### 3.1. Channel-Specific SLA Targets
As defined in **Support Policy §3**, first response is measured from ticket creation (`created_at`) to the first human reply (`first_response_at`):

$$\text{Response Time (minutes)} = \frac{\text{first\_response\_at} - \text{created\_at}}{60 \text{ seconds}}$$

| Channel | SLA Target Window | Target in Minutes | Operating Hours Constraint (Policy §2) |
| :--- | :--- | :--- | :--- |
| **Chat** | **15 minutes** | 15 mins | 24x7 coverage (Indore handles 22:00–06:00 IST) |
| **Voice** | **2 hours** | 120 mins | Inbound IVR callback requests 08:00–22:00 IST |
| **Social** | **4 hours** | 240 mins | Worked by Chat Frontline team |
| **Email** | **8 hours** | 480 mins | 24x7 intake, worked in queue order |

### 3.2. Exact Breach Determination
$$\text{is\_breached}_i = \begin{cases} 1 & \text{if } \text{Response Time}_i > \text{Target}(\text{channel}_i) \\ 0 & \text{otherwise} \end{cases}$$

### 3.3. Automatic SLA Breach Credit Calculation
Per **Support Policy §3**: *"Every ticket that misses its first-response target automatically issues a store credit of Rs 350 to the customer's account on resolution. The credit is issued regardless of the reason for the breach and is charged to the SLA credit line in the support P&L."*

$$\text{SLA Credit Liability (INR)} = \sum_{i \in T_{\text{breached}}} ₹350 = N_{\text{breach}} \times ₹350$$

- **Empirical Baseline in Dataset:**
  - Chat: 401 breaches / 5,102 tickets (7.86% breach rate)
  - Email: 445 breaches / 3,644 tickets (12.21% breach rate — largest volume)
  - Social: 101 breaches / 1,171 tickets (8.63% breach rate)
  - Voice: 117 breaches / 1,833 tickets (6.38% breach rate)
  - **Total Company Breaches:** **1,064 tickets** (9.06% overall breach rate)
  - **Total SLA Credit Liability:** $1,064 \times ₹350 =$ **₹372,400.00**

---

## 4. Agent Performance & Peer-Group Segmentation

### 4.1. Core Identity & Linking Rule
- **Mandatory Join Key:** All agent joins must strictly use **`agent_id`**, never agent name.
- **Rationale:** Two distinct agents share the display name **"Kavya Pandey"**:
  - `A3006`: Indore, Chat Frontline, Morning shift.
  - `A3029`: Bengaluru, Voice Frontline, Day shift.
  - Joining on display name corrupts scorecards and compensation payouts.

### 4.2. Why Raw CSAT Alone Must Never Determine the Bottom 10
In `email-thread.txt`, Priya Raman asked to flag the "bottom ten" agents by CSAT for a ₹4 lakh retraining budget.
However, empirical analysis proves that **raw CSAT is fundamentally biased by queue assignment**:
1. **The Entire Bottom 6 are Tier 2 Agents:**
   `A3041` (2.42), `A3042` (2.44), `A3040` (2.55), `A3044` (2.57), `A3043` (2.60), `A3039` (2.83).
   All 6 are from **Escalations & Warranty**.
2. **The Remaining 4 in the Bottom 10 are "Kavya's Four":**
   `A3004` (2.98), `A3006` (3.01), `A3007` (3.01), `A3005` (3.04).
   As Neha Kulkarni pointed out: *"the hardware triage rota (Kavya's four plus the warranty team) get the angriest customers by design."*
3. **Queue Difficulty vs. Agent Competence:**
   A Tier 2 agent managing a dead battery on an out-of-stock flagship earbud over 6 days has an intrinsically lower CSAT distribution than a Chat agent answering delivery ETAs in 4 minutes.
   Penalizing hardware triage agents with mandatory retraining is an operational error that misallocates the ₹4 lakh training budget.

### 4.3. Peer-Group Segmentation Model
Agents must only be compared against peers handling equivalent inquiry types and channel workflows:

| Peer Group Code | Description | Agents Included | Primary Evaluation Dimensions |
| :--- | :--- | :--- | :--- |
| **`PG-CHAT`** | Chat Frontline (General) | 11 agents (excluding triage rota) | CSAT, Handle Time (mins), SLA Compliance |
| **`PG-EMAIL`** | Email Frontline | 7 agents | CSAT, First-Response Time (hrs), FCR |
| **`PG-VOICE`** | Voice Frontline | 4 agents | CSAT, First-Response Time (mins), FCR |
| **`PG-LOGISTICS`** | Logistics Desk | 5 agents | Handle Time (days), Reshipment Accuracy, CSAT |
| **`PG-BILLING`** | Billing Desk | 4 agents | Refund Processing Speed, Accuracy, CSAT |
| **`PG-RETURNS`** | Returns Desk | 3 agents | QC Turnaround, Refund Reason Accuracy, CSAT |
| **`PG-HW-ROTA`** | Hardware Triage Rota | 4 agents (`A3004`, `A3005`, `A3006`, `A3007`) | Diagnostic Accuracy, Correct RMA Tagging, CSAT |
| **`PG-TIER2-WTY`**| Escalations & Warranty (Tier 2) | 6 agents (`A3039`–`A3044`) | Resolution in Days (Policy §6), RMA Quality |

### 4.4. Minimum Sample-Size Requirements
- To ensure statistical significance, an agent must have at least **$N \ge 30$ valid CSAT ratings** during the evaluation window to be ranked on CSAT.
- *Data Verification:* In the 18-month dataset, all 44 agents exceed this threshold (minimum CSAT count is 42, maximum is 243, mean is 118). Every agent has sufficient statistical power.

---

## 5. Bottom-10 Evaluation Methodology

To satisfy Priya Raman's requirement for a "bottom ten" while honoring Neha Kulkarni's operational warnings and Support Policy §6, we evaluate four transparent, reproducible scoring methodologies:

### Comparison of Candidate Methodologies:

```
+----------------------------------------------------------------------------------------------------+
| Method A: Raw CSAT Ranking                                                                         |
+----------------------------------------------------------------------------------------------------+
| Formula:        Rank purely by mean CSAT: R_i = Rank(avg_csat_i)                                   |
| Bottom 10:      A3041, A3042, A3040, A3044, A3043, A3039, A3004, A3006, A3007, A3005              |
| Composition:    100% Hardware Triage Rota and Tier 2 Escalations agents                            |
| Advantages:     Extremely simple; matches Priya's literal request.                                 |
| Disadvantages:  FATALLY FLAWED. Conflates customer anger over broken hardware with agent skill.    |
|                 Punishes agents who volunteer for/staff the hardest queues. Wastes training funds.  |
+----------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------+
| Method B: Peer-Group CSAT Percentile                                                               |
+----------------------------------------------------------------------------------------------------+
| Formula:        Percentile within Peer Group: P_{i, g} = Rank_{g}(avg_csat_i) / N_g                |
| Bottom 10:      A3008, A3020, A3041, A3002, A3029, A3004, A3034, A3026, A3011, A3017              |
| Composition:    Balanced across Chat, Email, Voice, Logistics, Returns, and Escalations            |
| Advantages:     Eliminates queue-difficulty bias; compares chat to chat, warranty to warranty.      |
| Disadvantages:  Ignores speed and handle time; sensitive to small group sample sizes (N=3 or N=4). |
+----------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------+
| Method C: Peer-Normalized Composite (CSAT 70% + Handle Time 30%) [RECOMMENDED]                     |
+----------------------------------------------------------------------------------------------------+
| Formula:        Composite Z-Score: Score_i = 0.70 * Z_{CSAT, g} - 0.30 * Z_{HT, g}                 |
|                 Where Z_{X, g} = (X_i - \mu_g) / \sigma_g                                          |
| Bottom 10:      A3008 (Chat), A3038 (Returns), A3026 (Logistics), A3020 (Chat), A3041 (Tier 2),   |
|                 A3017 (Chat), A3034 (Billing), A3024 (Chat), A3002 (Chat), A3015 (Chat)            |
| Composition:    Identifies true underperformers within every functional department                 |
| Advantages:     Scientifically robust; multi-dimensional; accounts for both quality and speed.    |
|                 Protects Tier 2 agents who meet departmental standards while flagging genuine      |
|                 laggards in frontline queues.                                                      |
| Disadvantages:  Requires communicating Z-scores to non-technical stakeholders.                     |
+----------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------+
| Method D: Tier-Segmented Balanced Quota (7 Frontline + 3 Escalations/Rota)                         |
+----------------------------------------------------------------------------------------------------+
| Formula:        Allocate training slots proportionally: 7 to Tier 1 Frontline, 3 to Tier 2 / Rota  |
| Bottom 10:      Frontline: A3008, A3020, A3026, A3038, A3034, A3002, A3017                         |
|                 Escalations/Rota: A3041, A3004, A3007                                              |
| Advantages:     Guarantees training support reaches frontline desks while offering dedicated       |
|                 retraining to struggling warranty specialists. Simple to explain to leadership.    |
| Disadvantages:  Fixed quota split is somewhat arbitrary.                                           |
+----------------------------------------------------------------------------------------------------+
```

### Recommendation for Production Solution:
We recommend **Method C (Peer-Normalized Composite Score)** as the primary analytical ranking engine, accompanied by an executive view that presents **Method D** as the actionable training budget allocation for Priya Raman.

---

## 6. Replacement & Lot-Code Analysis

### 6.1. Replacement Rate Definition
Replacement rate is calculated at two distinct operational levels:
1. **Ticket Replacement Rate:**
   $$\text{Replacement Rate}_{\text{ticket}} = \frac{\sum_{i \in T} \mathbb{I}(\text{replacement\_issued}_i = \text{'Y'})}{|T|}$$
   *(Overall baseline: 1,896 / 11,750 = **16.14%**)*

2. **Order Replacement Rate (Product / Lot Level):**
   $$\text{Replacement Rate}_{\text{order}} = \frac{\text{Unique Orders with Replacement}}{\text{Total Orders Sold}}$$

### 6.2. Order and Product Join Methodology
To analyze hardware issues against sales batches:
1. **Direct Join:** Link `tickets.order_id` to `orders.order_id` (matches 7,643 tickets, 65.05%).
2. **Deterministic Fallback Join:** For the 4,107 tickets where `order_id` is blank:
   - Match on `tickets.customer_id == orders.customer_id` AND `tickets.product_sku == orders.sku`.
   - *3,174 tickets* match exactly one order.
   - *933 tickets* match multiple orders. **Deterministic Tie-Breaking Rule:** Select the order with the minimum non-negative difference between ticket creation and order date:
     $$\text{order}^* = \arg\min_{o} (\text{created\_at} - \text{order\_date}_o) \quad \text{s.t. } \text{created\_at} \ge \text{order\_date}_o$$
     *(If no prior order exists, select the earliest order chronologically).*
3. **Product Join:** Link `product_sku` to `products.sku` (100% deterministic match).

### 6.3. Lot-Code Statistical Analysis
- Production lots are tracked via `orders.lot_code` (format: `SKU-YYMM-BATCH`, e.g., `PL2-2510-1`).
- For each product and lot code, calculate the empirical replacement proportion:
  $$\hat{p}_{\text{lot}} = \frac{N_{\text{replacements}}(\text{lot})}{N_{\text{orders}}(\text{lot})}$$

### 6.4. Evidentiary Boundary: "Defect" vs. "Evidence Consistent with Batch Issue"
- **Observed Empirical Anomaly:**
  - For **Pulse 2 (`VA-EB-PL2`)**, baseline replacement rate across normal production runs (Q2/Q3 2025 and Q1/Q2 2026) is **8.0% to 13.5%**.
  - For production lots manufactured in October, November, and December 2025 (**`PL2-2510-1` through `PL2-2512-4`**), the replacement rate surges to **35.0% – 42.7%** (averaging **38.6%** across 12 consecutive lots).
  - Customer messages overwhelmingly describe dead charging cases and unresponsive left earbuds.
- **Scientific & Legal Causality Disclaimer:**
  - *Standard:* Helpdesk ticket logs, customer verbatim transcripts, and return flags do **not** constitute an engineering metallurgical or component teardown audit.
  - *Mandatory Assessment Phrasing:* We document this finding as **"strong empirical evidence consistent with a batch-specific hardware failure in Q4 2025 production runs of Pulse 2."**
  - We do not overstate causality by asserting a certified "manufacturing defect" without citing hardware laboratory RMA bench reports.

---

## 7. Measurable Business Goals

We evaluate three data-backed, high-impact business improvement cases for Vireo Audio:

### Candidate Goal 1: First-Response SLA Breach Reduction (Recommended Primary Goal)
- **Current Baseline:** 1,064 SLA breaches out of 11,750 tickets (**9.06% breach rate**).
  - Financial liability: $1,064 \times ₹350 =$ **₹372,400.00** in automatic store credit payouts.
  - Primary driver: Email queue has a 12.21% breach rate (445 breaches), and Chat has 401 breaches.
- **Target:** Reduce overall first-response breach rate from 9.06% to **3.50%** (target $\le 410$ total breaches, eliminating at least 654 breaches).
- **Estimated Financial Impact:**
  $$\Delta \text{Cost} = 654 \text{ avoided breaches} \times ₹350 = \mathbf{₹228,900.00} \text{ in direct cash credit savings per period}$$
  *(Plus an estimated ₹150,000+ in retained customer lifetime value from eliminating survey dissatisfaction).*
- **Calculation Method:** $\Delta \text{Breaches} \times ₹350$ automated policy penalty.
- **Assumptions:** Implementation of queue threshold alerting (warning agents at 10m for chat, 6h for email) and dynamic shift re-balancing between Indore and Bengaluru.

---

### Candidate Goal 2: Elimination of Dual-Remedy Leakage (Strongest Immediate Leakage Fix)
- **Current Baseline:** 131 customer orders received **both a refund and a replacement unit**, directly violating Support Policy §5.
  - Total combined payout on dual orders: **₹590,934.00** (Refunds: ₹355,434; Replacements: ₹235,500).
- **Target:** **Zero (0) dual-remedy orders** (100% adherence to Policy §5 dual-remedy prohibition).
- **Estimated Financial Impact:**
  $$\text{Direct Recovery} = \sum_{\text{dual orders}} \text{Redundant Replacement Cost} = \mathbf{₹235,500.00} \text{ in pure margin recovery}$$
- **Calculation Method:** Sum of replacement cost (`unit_cost` + ₹340) for orders where a refund was already disbursed.
- **Assumptions:** Helpdesk CRM implements an automated validation lock blocking replacement approval if a refund is processed on the order, and vice-versa.

---

### Candidate Goal 3: Pulse 2 Defective Lot Triage & RMA Containment
- **Current Baseline:** 1,166 replacements for Pulse 2 (`VA-EB-PL2`), costing **₹2,122,120.00** under Policy formula (`unit_cost` ₹1,480 + shipping ₹340).
  - 1,281 total company replacements were authorized by uncertified Tier 1 agents in violation of Policy §6.
- **Target:** Direct all Pulse 2 warranty claims from affected Q4 2025 lots (`PL2-2510-*` to `PL2-2512-*`) to certified Tier 2 specialists; eliminate improper Tier 1 frontline replacements; divert 15% of recoverable complaints to firmware/charging recalibration.
- **Estimated Financial Impact:**
  $$\text{Savings} = 175 \text{ avoided unit swaps} \times ₹1,820 = \mathbf{₹318,500.00}$$
- **Calculation Method:** Avoided units $\times$ policy replacement cost.
- **Assumptions:** Firmware resets resolve a subset of battery synchronization issues; certified Tier 2 review eliminates fraudulent or premature replacements.

---

### Prioritization Summary:
The **recommended primary business goal** for the assessment is **Goal 1 (First-Response SLA Breach Reduction)** combined with **Goal 2 (Dual-Remedy Elimination)**. Together, they deliver **₹464,400.00 in direct, recurring cash recovery**, fully funding Priya Raman's ₹400,000 Q3 training budget with surplus.

---

## 8. Verification & Validation Standards

To ensure the analytics engine and any supporting NLP/AI components are flawless, the following verification suite must pass before any dashboard or client deliverable is finalized:

### 8.1. Deterministic System Integrity Checks
1. **Row Count & Ingestion Integrity:**
   - Ingested ticket count must equal exactly `11,750`.
   - Ingested orders (`15,500`), customers (`9,500`), agents (`44`), and products (`14`) must match source CSVs exactly.
   - Zero duplicate tickets (`ticket_id` uniqueness = 100%).
2. **Relational Referencing Audit:**
   - Orphan `customer_id` count = 0.
   - Orphan `agent_id` count = 0.
   - Orphan `product_sku` count = 0.
3. **Timestamp Normalization Invariant:**
   - After applying $+5\text{h }30\text{m}$ to `legacy_fd.resolved_at`, verify that $\text{count}(\text{Handle Time} < 0) == 0$.
   - All 2,309 pre-migration anomalies must resolve to positive values.
4. **SLA Breach Determinism:**
   - Verified breach count must equal exactly `1,064` tickets.
   - Total breach credit liability must equal exactly `₹372,400.00`.
5. **CSAT Calculation Standard:**
   - Total valid responses across all tickets = `5,196`. Total nulls = `6,554`.
   - Global average CSAT on all valid responses must equal `3.3266` (rounded to `3.33`).
   - Completed attendance CSAT (`resolved` + `closed`, 4,947 responses) must equal `3.3259` (rounded to `3.33`).
   - Null scores must never be converted to 0.
6. **Financial Ledger Invariants:**
   - Direct refunds total: `₹5,350,871.00`.
   - Policy replacements total: `₹3,415,990.00`.
   - Transfer costs total: `₹370,575.00`.
   - Total handling contact costs: `₹3,253,060.00`.

### 8.2. NLP & Telephony Text Validation
For text classification, category tagging, or sentiment scoring:
1. **Junk IVR Quarantine Check:**
   - Verify that all ~40 failed IVR transcripts (`[line dropped]`, `[inaudible] ...`, single characters) are classified into a distinct `Telephony System Error` category and excluded from voice agent behavioral scoring.
2. **Stratified Manual Gold-Standard Sample (50 Tickets):**
   - Extract a 50-ticket stratified random sample across channels (20 Chat, 15 Email, 10 Voice, 5 Social).
   - Manually verify customer intent, sentiment, and category against agent closing notes.
   - Require $\ge 90\%$ classification concordance between automated tags and gold-standard manual review.
3. **Zero Per-Ticket API Cost Constraint:**
   - In compliance with Arjun Mehta's budget directive, all text processing and analytics must execute via deterministic, local Python/Regex/heuristics with ₹0.00 in per-ticket external model fees.

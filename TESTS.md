# Vireo Audio — Automated Test Suite & Validation Evidence

**Test Execution Status:** 13 / 13 Tests Passed (100% Deterministic Verification)  
**Execution Timestamp:** 6 October 2026, 00:01:02 IST  
**Execution Command:** `python test_pipeline.py`  
**Test Runner Engine:** `src/validation.py`  

---

## 1. Automated Test Results Summary

```
======================================================================
RUNNING VIREO AUDIO DETERMINISTIC PIPELINE & POLICY VALIDATION
======================================================================

[PASS] Test 01: Row Count Integrity: tickets (11,750), orders (15,500), customers (9,500), agents (44), products (14)
       Status: PASSED | Tickets: 11750, Orders: 15500, Customers: 9500, Agents: 44, Products: 14

[PASS] Test 02: SLA Channel Thresholds Correct (Chat 15m, Voice 120m, Social 240m, Email 480m)
       Status: PASSED | Evaluated 1,064 breaches matching policy channel thresholds

[PASS] Test 03: Rs 350 SLA Breach Store Credit Calculation (1,064 * Rs 350 = Rs 372,400)
       Status: PASSED | Total SLA credit calculated: Rs 372,400.00

[PASS] Test 04: Blank CSAT Excluded Across Dataset (6,554 nulls excluded; all-valid mean = 3.3266, not imputed to 0)
       Status: PASSED | Null CSAT count: 6554, All-valid non-null mean: 3.3266 (rounded: 3.33)

[PASS] Test 05: Completed Attendance CSAT Calculated Strictly on Resolved/Closed (4,947 responses, mean = 3.3259 -> 3.33)
       Status: PASSED | Attendance CSAT responses: 4,947, Completed attendance mean: 3.3259 (rounded: 3.33)

[PASS] Test 06: Legacy Timestamp Normalization (+05:30 eliminates all 2,309 negative handle times)
       Status: PASSED | Raw negative handle times: 2309 -> Normalized negative handle times: 0

[PASS] Test 07: Agent Joins Strictly Use agent_id (0 unmatched orphans; 2 distinct Kavya Pandeys mapped)
       Status: PASSED | Orphan agent keys: 0, Unique Kavya Pandey records: ['A3006', 'A3029']

[PASS] Test 08: Tier 2 Segmented into Dedicated Peer Group (8 distinct peer groups; no raw volume penalty)
       Status: PASSED | Distinct peer groups created: ['Frontline - Chat Frontline', 'Hardware Triage Rota', 'Frontline - Email Frontline', 'Frontline - Voice Frontline', 'Frontline - Logistics', 'Frontline - Billing', 'Frontline - Returns Desk', 'Tier 2 (Escalations & Warranty)']

[PASS] Test 09: Peer-Normalized Composite Score Formula: 0.70 * Z_CSAT - 0.30 * Z_HT
       Status: PASSED | Agent A3001: calculated -0.3075, expected -0.3075

[PASS] Test 10: Dual-Remedy Order Detection Works (131 orders received both refund and replacement)
       Status: PASSED | Dual-remedy orders identified: 131, Total repl spend: Rs 235,500.00

[PASS] Test 11: Goodwill Policy-Cap Overspend Detection Works (32 cap violations, Rs 99,732 overage)
       Status: PASSED | Violations: 32, Total overspend above cap: Rs 99,732.00

[PASS] Test 12: FCR Proxy Detects Same Customer + SKU Contacts within 30d (2,455 repeat contacts, Rs 680,740 spend)
       Status: PASSED | Repeat contacts detected: 2455, Cost: Rs 680,740.00

[PASS] Test 13: Replacement Cost Uses Policy Standard: unit_cost_inr + Rs 340 (Rs 3,415,990 total spend)
       Status: PASSED | Policy replacement spend: Rs 3,415,990.00

======================================================================
SUMMARY: 13 / 13 Tests Passed successfully.
======================================================================
```

---

## 2. Test Verification Details

### 2.1. Ingestion & Join Auditing (Tests 1, 7)
- Verifies zero records dropped during file ingestion.
- Ensures all 44 agents are mapped via `agent_id`, preventing any display-name merge conflicts between `A3006` (Indore) and `A3029` (Bengaluru).

### 2.2. SLA Breach & P&L Liability (Tests 2, 3)
- Validates that tickets missing channel targets incur the exact automated ₹350 store credit liability defined in Support Policy §3.
- Reconciles 1,064 breaches to ₹372,400.00.

### 2.3. CSAT & Attendance Standards (Tests 4, 5)
- Confirms 6,554 blank survey responses are strictly excluded from averages across all 11,750 tickets (mean of all 5,196 valid responses: **3.3266**, rounded to **3.33**).
- Confirms the 249 premature survey responses recorded on `open` and `pending` tickets are segregated from completed attendance scoring (mean of 4,947 attendance responses: **3.3259**, rounded to **3.33**).

### 2.4. Legacy System Normalization (Test 6)
- Verifies that applying the $+05:30$ UTC-to-IST correction to `legacy_fd.resolved_at` successfully eliminates all 2,309 negative handle times without modifying source CSVs.

### 2.5. Peer Normalization & Tier Protection (Tests 8, 9)
- Confirms agents are segmented into 8 functional cohorts.
- Verifies mathematical precision of composite Z-score weighting: $0.70 \times Z_{\text{CSAT}} - 0.30 \times Z_{\text{HT}}$.

### 2.6. Policy Violations & Operational Leakage (Tests 10, 11, 13)
- Verifies identification of 131 dual-remedy orders (Policy §5 breach).
- Verifies identification of 32 goodwill credits breaching the ₹500 cap (Policy §5 breach).
- Confirms replacement accounting adheres strictly to official policy (`unit_cost` + ₹340) rather than Arjun's flat ₹2,500 estimate.

### 2.7. FCR Proxy & Repeat Contact Financial Reconciliation (Test 12)
- Reconciles exactly 2,455 repeat contacts under the operational proxy (`same customer + same product SKU within 30 days of resolution`).
- Confirms **total observed repeat-contact handling spend: ₹680,740.00** across channels.
- Confirms **modeled avoidable savings: ₹102,111.00** when targeting a 15% reduction in repeat contacts ($₹680,740 \times 15\% = ₹102,111.00$).

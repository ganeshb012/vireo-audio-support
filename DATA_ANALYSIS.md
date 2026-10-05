# Vireo Audio — Support Tickets (Set B) Data & Requirements Analysis

**Document Status:** Complete Data & Requirements Analysis  
**Project:** Vireo Audio Support Desk Analysis & Optimization  
**Dataset Timeframe:** 1 January 2025 – 30 June 2026  
**Analysis Author:** Antigravity AI  

---

## 1. Row Count for Every CSV

The assessment workspace contains 5 core CSV files (and associated metadata documents). The exact row and column dimensions are as follows:

| Logical File | Actual File on Disk | Rows (Records) | Columns | File Size (Bytes) |
| :--- | :--- | :--- | :--- | :--- |
| **`tickets.csv`** | `ef56a2c7-7840-454e-ab7e-a0df87b90bc5-tickets.csv` | **11,750** | 21 | 4,411,878 |
| **`orders.csv`** | `6990ae61-2433-405d-a790-24fda9cb7743-orders.csv` | **15,500** | 8 | 1,016,709 |
| **`customers.csv`** | `1e2a735c-5a79-4c67-9fc0-e0006ea2b76a-customers.csv` | **9,500** | 6 | 445,206 |
| **`agents.csv`** | `8fb10115-c45d-42dc-9e04-95154d9c3e41-agents.csv` | **44** | 8 | 2,879 |
| **`products.csv`** | `c59ac66f-a215-4a8a-8dfe-39fc4db60f5c-products.csv` | **14** | 7 | 979 |

*Note: All original CSV files have been kept unmodified.*

---

## 2. Column Names and Meanings

### 2.1. `tickets.csv` (11,750 rows, 21 columns)
1. **`ticket_id`** *(string, primary key)*: Unique helpdesk ticket identifier (e.g., `TK-240001` to `TK-254719`).
2. **`created_at`** *(datetime string, IST)*: Timestamp when the customer ticket was logged in the intake flow.
3. **`first_response_at`** *(datetime string, IST)*: Timestamp of the first human agent reply.
4. **`resolved_at`** *(datetime string)*: Timestamp when the ticket reached resolution. Blank if open or pending. For `legacy_fd` tickets, reconstructed from legacy event logs in UTC.
5. **`status`** *(string)*: Ticket lifecycle state (`resolved`, `closed`, `open`, `pending`).
6. **`channel`** *(string)*: Contact channel (`chat`, `email`, `voice`, `social`).
7. **`customer_id`** *(string, foreign key)*: Customer reference into `customers.csv`.
8. **`order_id`** *(string, foreign key, nullable)*: E-commerce order reference into `orders.csv`. Blank if customer did not quote it.
9. **`product_sku`** *(string, foreign key)*: Product SKU into `products.csv`.
10. **`category`** *(string)*: Issue classification initially tagged by intake bot and optionally corrected by agent upon closure.
11. **`priority`** *(string)*: Ticket urgency (`Low`, `Normal`, `High`).
12. **`assigned_team`** *(string)*: Initial support team the ticket was routed to.
13. **`agent_id`** *(string, foreign key)*: Agent identifier who resolved the ticket. Must join into `agents.csv` via `agent_id`, never by agent name.
14. **`transfers`** *(integer)*: Count of internal hand-offs between teams.
15. **`csat_score`** *(float, nullable)*: 1 to 5 customer satisfaction rating. Blank indicates no response.
16. **`refund_amount_inr`** *(float, nullable)*: Monetary refund amount processed on the ticket in INR. Blank if no refund was issued.
17. **`refund_reason_code`** *(string, nullable)*: Standardized dropdown code selected by agent when raising a refund (per Policy §5).
18. **`replacement_issued`** *(string)*: Flag (`Y` / `N`) indicating if a replacement unit was dispatched.
19. **`customer_message`** *(string)*: Customer opening statement or IVR transcript (for voice).
20. **`agent_notes`** *(string)*: Agent closing notes, diagnostic log, or resolution summary.
21. **`source_system`** *(string)*: Originating system (`helpdesk` for current platform, `legacy_fd` for migrated Freshdesk records).

### 2.2. `agents.csv` (44 rows, 8 columns)
1. **`agent_id`** *(string, primary key)*: Unique agent identifier (`A3001` through `A3044`).
2. **`name`** *(string)*: Agent display name (note: non-unique; two distinct agents share the name "Kavya Pandey").
3. **`site`** *(string)*: Support center location (`Bengaluru`, `Indore`).
4. **`team`** *(string)*: Department/team assignment (`Chat Frontline`, `Email Frontline`, `Voice Frontline`, `Logistics`, `Billing`, `Returns Desk`, `Escalations & Warranty`).
5. **`shift`** *(string)*: Assigned working window (`Morning`, `Day`, `Night`).
6. **`tier`** *(integer)*: Agent skill tier (`1` for frontline, `2` for senior/certified escalation & warranty agents).
7. **`from_date`** *(date string)*: Effective start date of current assignment.
8. **`to_date`** *(date string, nullable)*: Effective end date (all rows currently null, indicating ongoing assignments).

### 2.3. `customers.csv` (9,500 rows, 6 columns)
1. **`customer_id`** *(string, primary key)*: Unique customer identifier (`C10001` to `C19500`).
2. **`name`** *(string)*: Customer full name.
3. **`city`** *(string)*: Customer city (across 33 major Indian cities).
4. **`state`** *(string)*: Customer state / union territory.
5. **`signup_date`** *(date string)*: Date customer registered account with Vireo.
6. **`care_plus`** *(string)*: Extended warranty / VIP loyalty program subscription (`Y` / `N`).

### 2.4. `orders.csv` (15,500 rows, 8 columns)
1. **`order_id`** *(string, primary key)*: Unique order number (`VR880001` to `VR910000`).
2. **`customer_id`** *(string, foreign key)*: Purchasing customer key into `customers.csv`.
3. **`sku`** *(string, foreign key)*: Purchased product SKU into `products.csv`.
4. **`order_date`** *(date string)*: Date order was placed.
5. **`channel`** *(string)*: Sales channel (`vireo.in`, `Amazon`, `Flipkart`, `QuickComm`).
6. **`qty`** *(integer)*: Quantity ordered (1 or 2 units).
7. **`order_value_inr`** *(integer)*: Total transaction value in INR.
8. **`lot_code`** *(string)*: Manufacturing batch / production lot code printed on the retail packaging.

### 2.5. `products.csv` (14 rows, 7 columns)
1. **`sku`** *(string, primary key)*: Stock Keeping Unit identifier (e.g., `VA-EB-PL2`).
2. **`product_name`** *(string)*: Marketing product name.
3. **`family`** *(string)*: Category group (`earbuds`, `headphones`, `watch`, `speaker`, `accessory`).
4. **`launch_date`** *(date string)*: Official market launch date.
5. **`unit_cost_inr`** *(integer)*: Landed manufacturing cost per unit in INR.
6. **`retail_price_inr`** *(integer)*: Official retail selling price (MRP/MOP) in INR.
7. **`warranty_months`** *(integer)*: Standard manufacturer warranty duration (6 or 12 months).

---

## 3. Missing-Value Analysis

Comprehensive null audit across all 5 tables:

| Dataset | Column Name | Total Rows | Null Count | Null % | Business Significance / Root Cause |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`tickets.csv`** | `ticket_id` | 11,750 | 0 | 0.00% | None (100% complete) |
| | `created_at` | 11,750 | 0 | 0.00% | None (100% complete) |
| | `first_response_at` | 11,750 | 0 | 0.00% | None (every ticket had an initial response) |
| | `resolved_at` | 11,750 | **567** | **4.83%** | Expected: corresponds exactly to unresolved tickets (335 `open` + 232 `pending`) |
| | `status` | 11,750 | 0 | 0.00% | None (100% complete) |
| | `channel` | 11,750 | 0 | 0.00% | None (100% complete) |
| | `customer_id` | 11,750 | 0 | 0.00% | None (100% complete) |
| | `order_id` | 11,750 | **4,107** | **34.95%** | Customer did not quote order number at intake. Requires fallback join (`customer_id` + `product_sku`) |
| | `product_sku` | 11,750 | 0 | 0.00% | None (100% complete) |
| | `category` | 11,750 | 0 | 0.00% | None (100% complete) |
| | `priority` | 11,750 | 0 | 0.00% | None (100% complete) |
| | `assigned_team` | 11,750 | 0 | 0.00% | None (100% complete) |
| | `agent_id` | 11,750 | 0 | 0.00% | None (100% complete) |
| | `transfers` | 11,750 | 0 | 0.00% | None (100% complete) |
| | `csat_score` | 11,750 | **6,554** | **55.78%** | Customer non-response. Must be excluded from CSAT score averages (Policy §8) |
| | `refund_amount_inr` | 11,750 | **9,881** | **84.09%** | Normal: only 1,869 tickets involved monetary refunds |
| | `refund_reason_code`| 11,750 | **9,881** | **84.09%** | Synchronized with `refund_amount_inr` |
| | `replacement_issued`| 11,750 | 0 | 0.00% | None (always `Y` or `N`) |
| | `customer_message` | 11,750 | 0 | 0.00% | None (100% complete) |
| | `agent_notes` | 11,750 | 0 | 0.00% | None (100% complete) |
| | `source_system` | 11,750 | 0 | 0.00% | None (`helpdesk`: 8,376, `legacy_fd`: 3,374) |
| **`agents.csv`** | `agent_id` to `from_date` | 44 | 0 | 0.00% | All roster metadata fields are 100% populated |
| | `to_date` | 44 | **44** | **100.00%** | Expected: all 44 agents are actively employed |
| **`customers.csv`**| All 6 columns | 9,500 | 0 | 0.00% | 100% complete; 0 missing values |
| **`orders.csv`** | All 8 columns | 15,500 | 0 | 0.00% | 100% complete; 0 missing values |
| **`products.csv`** | All 7 columns | 14 | 0 | 0.00% | 100% complete; 0 missing values |

---

## 4. Date Range

| Table | Date Field | Minimum Date / Timestamp | Maximum Date / Timestamp | Coverage Period |
| :--- | :--- | :--- | :--- | :--- |
| **`tickets.csv`** | `created_at` | `2025-01-01 08:22:00` IST | `2026-06-30 21:54:00` IST | Exactly 18 months (Q1 2025 – Q2 2026) |
| | `first_response_at` | `2025-01-01 08:22:00` IST | `2026-07-01 00:58:00` IST | Initial responses extend 3 hours past last ticket |
| | `resolved_at` | `2025-01-01 03:05:00` UTC* | `2026-07-10 21:35:00` IST | Final resolution spans to 10 July 2026 |
| **`orders.csv`** | `order_date` | `2024-06-15` | `2026-06-30` | 24.5 months (orders precede support data by ~6.5 mos) |
| **`customers.csv`**| `signup_date` | `2022-07-16` | `2025-01-01` | Customer signups up to ticket launch date |
| **`products.csv`** | `launch_date` | `2023-10-01` (Strata 2) | `2025-08-01` (Pulse Case) | Earliest release Oct 2023, newest Aug 2025 |
| **`agents.csv`** | `from_date` | `2020-11-24` | `2024-11-04` | Agent onboarding dates |

*\*Note on `resolved_at` minimum: Reconstructed legacy resolution timestamps are recorded in UTC, explaining timestamps appearing prior to IST ticket creation when unadjusted.*

---

## 5. Number of Agents

- **Total Roster Rows:** 44
- **Unique `agent_id`s:** 44 (`A3001` through `A3044`)
- **Unique Agent Display Names:** 43
- **Critical Agent Identity Warning:**
  Two distinct agent records share the display name **"Kavya Pandey"**:
  1. `agent_id`: **`A3006`** | Site: **Indore** | Team: **Chat Frontline** | Shift: **Morning** | Tier: **1** | Hired: 2023-02-11
  2. `agent_id`: **`A3029`** | Site: **Bengaluru** | Team: **Voice Frontline** | Shift: **Day** | Tier: **1** | Hired: 2023-04-25
  
  *Rule Verification:* Joining tickets on `name` instead of `agent_id` merges tickets from two different agents across two different cities, corrupting CSAT, handle time, and bonus calculations.

---

## 6. Teams

Support is organized across 7 distinct operational teams. Distribution across agents and tickets:

| Team Name | Roster Agent Count | Tier | Primary Responsibility (Policy §6) | Total Tickets Assigned | % of Total Tickets |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Chat Frontline** | 15 | Tier 1 | First contact for chat & social queries | 3,467 | 29.51% |
| **Logistics** | 5 | Tier 1 | Delivery, courier tracking, reshipments | 1,884 | 16.03% |
| **Email Frontline** | 7 | Tier 1 | First contact for asynchronous email tickets | 1,817 | 15.46% |
| **Billing** | 4 | Tier 1 | Payments, invoices, payment gateways | 1,471 | 12.52% |
| **Escalations & Warranty** | 6 | Tier 2 | Hardware escalations, RMA, warranty approval | 1,187 | 10.10% |
| **Returns Desk** | 3 | Tier 1 | Return pickups, QC, refund processing | 1,018 | 8.66% |
| **Voice Frontline** | 4 | Tier 1 | Inbound callback requests (08:00–22:00 IST) | 906 | 7.71% |
| **Total** | **44** | — | — | **11,750** | **100.00%** |

---

## 7. Tiers

Staffing and operational split by Tier:

| Tier | Agent Count | Agent IDs | Team(s) | Operational Focus |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | **38** (86.4%) | `A3001`–`A3038` | Chat, Email, Voice, Logistics, Billing, Returns Desk | First contact, general enquiries, order tracking, standard returns. High volume, measured on speed and attendance. |
| **Tier 2** | **6** (13.6%) | `A3039`–`A3044` | Escalations & Warranty | Certified senior agents (`Sameer Ghosh`, `Tarun Fernandes`, `Jaspreet Desai`, `Sneha Sethi`, `Kabir Varghese`, `Pranav Khanna`). Exclusive authorization for warranty replacements. Multi-touch cases measured in **days**, not tickets closed per week. |

---

## 8. Sites

Geographic distribution of support operations:

| Site | Agent Count | Teams Present | Shift Coverage | Key Operational Function |
| :--- | :--- | :--- | :--- | :--- |
| **Bengaluru** | **25** (56.8%) | Chat Frontline (8), Email Frontline (4), Escalations & Warranty (4), Logistics (3), Billing (2), Returns Desk (2), Voice Frontline (2) | Morning, Day | Headquarters site, primary contact handling and Escalations & Warranty hub. |
| **Indore** | **19** (43.2%) | Chat Frontline (7), Email Frontline (3), Escalations & Warranty (2), Logistics (2), Billing (2), Returns Desk (1), Voice Frontline (2) | Morning, Day, **Night** | Regional delivery center; provides **exclusive 24x7 night shift coverage** for chat and emergency queues. |

---

## 9. Shifts

Shifts are defined in Indian Standard Time (IST). Staffing allocation across the 44 agents:

| Shift Name | Working Hours (IST) | Agent Count | % of Roster | Site Distribution |
| :--- | :--- | :--- | :--- | :--- |
| **Morning** | 06:00 – 14:00 IST | **24** | 54.5% | Bengaluru (14), Indore (10) |
| **Day** | 14:00 – 22:00 IST | **15** | 34.1% | Bengaluru (11), Indore (4) |
| **Night** | 22:00 – 06:00 IST | **5** | 11.4% | **Indore (5)**, Bengaluru (0) |

*Policy §7 & §2:* 
- Overnight coverage is provided entirely by the Indore night shift (`A3020`, `A3021`, `A3022`, `A3023`, `A3024` — all on Chat Frontline).
- Queue coverage outside a team's staffed hours is picked up by the next shift in order of creation.

---

## 10. Channels

Operational volume, hours, and SLA rules by channel:

| Channel | Ticket Volume | % Volume | Operating Hours | First-Response Target | Cost Standard per Contact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Chat** | 5,102 | 43.42% | 24x7 (Night shift: Indore) | 15 minutes | Rs 210 |
| **Email** | 3,644 | 31.01% | 24x7 (Worked in queue order) | 8 hours (480 mins) | Rs 260 |
| **Voice** | 1,833 | 15.60% | 08:00 – 22:00 IST (Callbacks) | 2 hours (120 mins) | Rs 520 |
| **Social** | 1,171 | 9.97% | Worked by Chat Frontline | 4 hours (240 mins) | Rs 240 |
| **Total / Blended** | **11,750** | **100.00%** | — | — | **Rs 290 (Blended)** |

---

## 11. Ticket Statuses

Breakdown of ticket statuses across the 11,750 records:

| Status | Ticket Count | % of Total | CSAT Surveyed? | Reached Resolution (`resolved_at`)? | Definition per Policy §8 & §10 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`resolved`** | 10,138 | 86.28% | Yes | Yes (10,138 timestamps populated) | Ticket resolved by agent. Counts towards "Attendance". |
| **`closed`** | 1,045 | 8.89% | Yes | Yes (1,045 timestamps populated) | Auto-closed after 72h without customer response. Counts towards "Attendance". |
| **`open`** | 335 | 2.85% | Anomaly* | No (`resolved_at` is null) | Unresolved, currently awaiting agent action. |
| **`pending`** | 232 | 1.97% | Anomaly* | No (`resolved_at` is null) | Unresolved, currently awaiting customer or 3rd party info. |
| **Total** | **11,750** | **100.00%** | — | — | **Completed Attendance: 11,183 (95.17%)** |

*\*Data Anomaly Note: Despite Policy §8 stating surveys are sent only when a ticket is resolved or closed, 150 `open` and 99 `pending` tickets have recorded CSAT scores in the export.*

---

## 12. CSAT Response Rate

Customer satisfaction measurement details (Policy §8):

- **Total Survey Responses:** 5,196
- **Total Unanswered (Blank):** 6,554
- **Overall Response Rate:** **44.22%** (closely matching the ~45% policy expectation)
- **Response Rate on Attendance (Resolved + Closed):** 4,947 / 11,183 = **44.24%**
- **Average CSAT Score (excluding blanks):** **3.33 / 5.00**

### Score Distribution:
| Score | Responses | % of Valid Responses | Interpretation |
| :--- | :--- | :--- | :--- |
| **1 (Very Dissatisfied)** | 310 | 5.97% | Critical escalation / defect / failed delivery |
| **2 (Dissatisfied)** | 811 | 15.61% | Unresolved friction / long delays |
| **3 (Neutral)** | 1,695 | 32.62% | Acceptable resolution |
| **4 (Satisfied)** | 1,632 | 31.41% | Prompt, helpful interaction |
| **5 (Very Satisfied)** | 748 | 14.39% | Exceptional service |
| **Total Valid Scores** | **5,196** | **100.00%** | — |

*Strict Calculation Rule:* Blank scores represent non-responses and must **never** be imputed as 0. All agent CSAT averages must strictly exclude blank values.

---

## 13. Refund Information

Monetary compensation and refund metrics:

- **Total Tickets with Refund:** 1,869 (15.91% of tickets)
- **Total Monetary Value Refunded:** **Rs 5,350,871.00**
- **Average Refund Amount:** Rs 2,862.96 (Median: Rs 2,499.00; Min: Rs 38.00; Max: Rs 13,998.00)

### Breakdown by Refund Reason Code (Policy §5):
| Reason Code | Meaning | Tickets | Total Refund (INR) | Mean Refund (INR) | Compliance Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`RETURN-QC-OK`** | Return received and passed QC | 648 | Rs 2,056,582 | Rs 3,173.74 | Primary valid return channel |
| **`DUP-PAYMENT`** | Duplicate or failed payment | 513 | Rs 1,481,257 | Rs 2,887.44 | Billing gateway failures |
| **`CANCEL`** | Cancellation before dispatch | 326 | Rs 865,064 | Rs 2,653.57 | Pre-dispatch cancellations |
| **`DOA-REPL`** | Dead on arrival, refund chosen | 114 | Rs 333,086 | Rs 2,921.81 | Within 7 days of delivery |
| **`LOST-TRANSIT`** | Lost or undelivered in transit | 96 | Rs 260,704 | Rs 2,715.67 | Logistics failure |
| **`PRICE-ADJ`** | Price or coupon adjustment | 94 | Rs 100,565 | Rs 1,069.84 | Commercial adjustments |
| **`GW-OTHER`** | Goodwill / Other credit | 37 | Rs 117,333 | Rs 3,171.16 | **32 tickets breach Rs 500 cap!** |
| **`WTY-BUYBACK`** | Warranty buy-back | 41 | Rs 136,280 | Rs 3,323.90 | Certified warranty buybacks |
| **Total** | — | **1,869** | **Rs 5,350,871** | — | — |

### Policy Violations in Refunds:
1. **Goodwill Cap Breaches:** Policy §5 mandates: *"Goodwill credits are capped at Rs 500 per ticket and require Team Lead approval."* In reality, **32 out of 37 GW-OTHER refunds exceed Rs 500**, reaching as high as Rs 11,998 (Mean: Rs 3,171.16).
2. **Dual Remedy (Refund + Replacement):** Policy §5 strictly prohibits both refund and replacement for the same order.
   - **6 individual tickets** have both `refund_amount_inr > 0` AND `replacement_issued == 'Y'`.
   - **131 distinct customer orders** received both a refund and a replacement across multiple tickets.

---

## 14. Replacement Information

Hardware unit replacement metrics:

- **Total Replacements Issued:** **1,896** (16.14% of all tickets)
- **Total Replacement Cost (Policy Formula: Unit Cost + Rs 340):** **Rs 3,415,990.00**
- **Total Replacement Cost (Arjun Mehta's flat reckoning @ Rs 2,500):** **Rs 4,740,000.00**
- **Discrepancy:** Arjun's estimate overstates actual policy replacement costs by **Rs 1,324,010.00 (+38.7%)**.

### Product Replacement Concentration:
| SKU | Product Name | Family | Replacements | % of Total Replacements | Unit Cost | Policy Repl. Cost |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`VA-EB-PL2`** | **Pulse 2 True Wireless Earbuds** | earbuds | **1,166** | **61.50%** | Rs 1,480 | Rs 2,122,120 |
| `VA-EB-PL1` | Pulse True Wireless Earbuds | earbuds | 146 | 7.70% | Rs 1,120 | Rs 213,160 |
| `VA-EB-AIR` | AirLite Earbuds | earbuds | 111 | 5.85% | Rs 760 | Rs 122,100 |
| `VA-SW-NX2` | Nexa 2 Smartwatch | watch | 101 | 5.33% | Rs 2,450 | Rs 281,790 |
| `VA-HP-ST3` | Strata 3 Over-Ear Headphones | headphones | 70 | 3.69% | Rs 2,650 | Rs 209,300 |
| `VA-SP-MINI` | Orbit Mini Speaker | speaker | 63 | 3.32% | Rs 980 | Rs 83,160 |
| `VA-SW-FIT` | Nexa Fit Band | watch | 58 | 3.06% | Rs 850 | Rs 69,020 |
| `VA-NB-ARC` | Arc Neckband | earbuds | 43 | 2.27% | Rs 540 | Rs 37,840 |
| All Others (6 SKUs) | Strata 2, Nexa 1, Orbit, Spares | various | 138 | 7.28% | Various | Rs 277,500 |
| **Total** | — | — | **1,896** | **100.00%** | — | **Rs 3,415,990** |

### Policy Violations in Replacements:
- **Tier 1 Unauthorized Approvals:** Policy §6 strictly specifies: *"Tier 2 work is certified: only Tier 2 agents may approve warranty replacements."*
  - **Tier 2 agents approved:** **615 replacements** (32.4%)
  - **Tier 1 agents approved:** **1,281 replacements** (67.6%) across Chat Frontline (552), Logistics (332), Email Frontline (202), Returns Desk (111), Voice Frontline (75), and Billing (9).

---

## 15. Source Systems

The data is an aggregated export from two consecutive platforms:

| Metric / Dimension | `legacy_fd` (Freshdesk) | `helpdesk` (Current Platform) | Combined Total |
| :--- | :--- | :--- | :--- |
| **Active Date Range** | 1 Jan 2025 – 14 Sep 2025 (02:22 IST) | 14 Sep 2025 (07:30 IST) – 30 Jun 2026 | 1 Jan 2025 – 30 Jun 2026 |
| **Ticket Count** | 3,374 (28.71%) | 8,376 (71.29%) | 11,750 |
| **Resolved / Closed** | 3,189 | 7,994 | 11,183 |
| **Open / Pending** | 185 | 382 | 567 |
| **Timezone Representation** | `created_at` & `first_response_at` in **IST**; reconstructed `resolved_at` in **UTC** | All timestamps displayed and exported in **IST** | Timezone mismatch across systems |
| **Negative Handle Times** | **2,309 tickets (100% of negative cases)** | **0 tickets** | 2,309 tickets |
| **Handle Time Fix (+5:30)** | Adjusting `resolved_at` by +5h 30m resolves **100%** of negative cases | No adjustment required | Completely harmonized |
| **Transfers Field** | Present (Mean: 0.10, Max: 2) | Present (Mean: 0.10, Max: 2) | Stored as integer |
| **Monetary Units** | Stored in INR in `tickets.csv` | Stored in INR in `tickets.csv` | Consistent in export |

---

## 16. Important Data-Quality Issues

1. **Systemic Timezone Offset in Legacy Tickets (`legacy_fd`):**
   - In `legacy_fd` (3,374 tickets), `created_at` and `first_response_at` are in IST, while reconstructed `resolved_at` is in UTC.
   - Calculating raw handle time (`resolved_at - first_response_at`) results in **2,309 negative handle times** (e.g., -5.28 hours).
   - Adding 5 hours and 30 minutes to `resolved_at` for `legacy_fd` tickets completely eliminates all 2,309 negative values and aligns the legacy median handle time (0.43 hours) with current helpdesk performance (0.50 hours).

2. **Shared Agent Display Name:**
   - Two distinct Tier 1 agents share the name "Kavya Pandey": `A3006` in Indore (Chat Frontline) and `A3029` in Bengaluru (Voice Frontline).
   - Performing aggregations or joins by name rather than `agent_id` will corrupt agent performance tracking and Diwali bonus allocations.

3. **Junk IVR Transcripts / Phone System Failures:**
   - As flagged by Sameer Qureshi, approximately 40 tickets contain corrupt phone system transcripts rather than actual customer messages.
   - Exact breakdown: 14 bracketed audio failure strings (e.g., `[IVR transcript] [inaudible] ... charging ... [crosstalk] ... refund [inaudible]`, `[IVR transcript] [line dropped]`), 13 single-punctuation or test entries (`-`, `.`, `...`, `??`, `test`), and short garbled messages.
   - These are telephony ingestion failures and must not be treated as agent misconduct or customer negligence.

4. **Premature CSAT Scores on Unresolved Tickets:**
   - 150 `open` tickets and 99 `pending` tickets have recorded CSAT scores (Mean: ~3.34).
   - Per Policy §8, surveys are triggered upon ticket resolution or 72h auto-closure. These scores likely stem from re-opened tickets or premature survey triggers.

5. **Dual Compensation Violations (Both Refund AND Replacement):**
   - 6 individual tickets and 131 distinct customer orders received both a refund and a replacement unit, directly violating Policy §5.

6. **Unauthorized Replacements Issued by Tier 1:**
   - 1,281 replacements (67.6% of all replacements) were authorized by Tier 1 agents across 6 different teams, violating Policy §6 certification requirements.

7. **Goodwill Credit Policy Breaches:**
   - 32 out of 37 `GW-OTHER` refund reason code instances exceeded the strict Rs 500 goodwill limit (reaching up to Rs 11,998).

8. **Missing Order Numbers & Fallback Ambiguity:**
   - 4,107 tickets (34.95%) have a blank `order_id`.
   - While 3,174 tickets resolve to a single order via fallback `(customer_id + product_sku)`, **933 tickets match multiple prior orders** (757 have 2 orders, 157 have 3, 19 have 4), introducing ambiguity when calculating order-level warranty or financial impact.

---

## 17. Important Business Rules from `support-policy.pdf`

1. **First-Response Service Levels & Penalties (Policy §3):**
   - **Chat:** 15 minutes
   - **Voice Callback:** 2 hours (120 minutes)
   - **Social:** 4 hours (240 minutes)
   - **Email:** 8 hours (480 minutes)
   - *Automated Penalty:* Every ticket that misses its target automatically issues a **Rs 350 store credit** to the customer upon resolution, charged to the support P&L SLA credit line. Standard reports report breaches against the resolving agent.

2. **Cost Standards for Planning (Policy §4):**
   - Cost per contact: Chat Rs 210, Email Rs 260, Voice Callback Rs 520, Social Rs 240. Blended average: Rs 290.
   - Internal transfer between teams: **Rs 305 per transfer**.
   - Fully loaded agent cost for staffing decisions: **Rs 165 per agent-hour** (8-hour shift = Rs 1,320).

3. **Refund & Replacement Policy (Policy §5):**
   - *Dead on Arrival (DOA, within 7 days of delivery):* Customer choice of full refund or replacement.
   - *In-Warranty Fault:* Repair or replacement.
   - *Lost/Damaged in Transit:* Reshipment or refund.
   - *Dual Remedy Prohibition:* In no case may a customer receive both a refund and a replacement for the same order. Immediate escalation to Team Lead and Finance required.
   - *Replacement Planning Cost:* **`unit_cost_inr` (products.csv) + Rs 340** (reverse pickup and forward shipping). Refurbishment recovery cannot be assumed.
   - *Goodwill Cap:* Capped at **Rs 500 per ticket** with mandatory Team Lead approval.

4. **Tier Certification & Evaluation (Policy §6):**
   - Only certified Tier 2 agents may approve warranty replacements.
   - Tier 2 cases are multi-touch and must be measured on **resolution in days**, never on weekly ticket volume. Tier 2 agents must not be compared with Tier 1 on volume metrics.

5. **Reporting & Operational Definitions (Policy §8 & §10):**
   - *First-Contact Resolution (FCR):* A ticket is resolved at first contact if the customer does not contact again about the same issue within 30 days of resolution. Return contact within window is costed at the channel's contact cost.
   - *Handle Time:* `first_response_at` to `resolved_at`.
   - *Attendance:* Any ticket in status `resolved` or `closed`. Auto-closed tickets after 72h without customer reply are surveyed and count as completed attendance.
   - *CSAT:* Exclude blank scores from averages; do not impute as zero.

---

## 18. Important Context and Warnings from `email-thread.txt`

1. **Priya Raman (Head of Customer Experience):**
   - Stated objective: Wants agent CSAT, handle time, bottom 10 agents flagged for the Rs 4 lakh Q3 training budget, and top 5 agents for the Diwali bonus.
   - Pushes an aggressive stance: *"Dashboard first, causes later. Bottom ten, please."*
   - Noted the discrepancy in replacement cost: Policy says `unit cost + Rs 340`, whereas Arjun claimed a flat Rs 2,500.

2. **Neha Kulkarni (Support Operations Manager):**
   - **Crucial Warning:** The hardware triage rota (**"Kavya's four plus the warranty team"**) handles the angriest customers and hardest hardware defects by design.
   - Warns that flagging the bottom 10 agents without accounting for queue type will unfairly penalize agents assigned to hardware triage rather than addressing true agent performance.
   - *Data Validation:* The bottom 10 agents by CSAT in the company are **exactly** the 6 Tier 2 Escalations & Warranty agents (`A3039`–`A3044`) plus "Kavya's four" (`A3004`, `A3005`, `A3006`, `A3007`). This confirms Neha's warning of queue-level structural bias.

3. **Arjun Mehta (Finance Controller):**
   - Expressed alarm that replacement spend roughly doubled since December.
   - Notes Rohan in the warehouse believes festive volume caught up with support.
   - Estimates replacement costs at a flat Rs 2,500 all-in.
   - **Budget Mandate:** Demanded that whatever tool is built must be cheap to run: *"no per-ticket model calls at Rs 5 a pop across twelve thousand tickets."* (Eliminates paid per-ticket LLM batch calls).

4. **Sameer Qureshi (Helpdesk Administrator, IT):**
   - Explicitly warned about the duplicate display name for "Kavya Pandey" (join on `agent_id`, never name).
   - Noted orders export contains lot codes requested by Finance.
   - Explained that ~40 tickets have junk/failed IVR customer messages due to phone system issues.
   - Confirmed helpdesk display timestamps are in IST.

5. **Root Cause Analysis (Pulse 2 Defect vs Festive Volume):**
   - Analysis of `orders.csv` and `tickets.csv` reveals that Rohan's and Arjun's "festive volume" hypothesis is incomplete:
   - While overall volume grew by ~30%, replacement rates surged from ~10% up to **25.5%** between January and March 2026.
   - The spike is overwhelmingly driven by **Pulse 2 True Wireless Earbuds (`VA-EB-PL2`)**, accounting for 1,166 replacements (61.5% of total).
   - Specifically, manufacturing lots from October, November, and December 2025 (**`PL2-2510-*`**, **`PL2-2511-*`**, and **`PL2-2512-*`**) suffered failure/replacement rates of **35% to 43%**, compared to 8%–13% for earlier and later lots. This proves a systemic manufacturing defect in Q4 2025 Pulse 2 batches (case charging / earbud power failure).

---

## 19. Ambiguities in the Assessment

1. **Definition of "Same Issue" in First-Contact Resolution (FCR):**
   - Policy §10 defines FCR as no contact within 30 days "about the same issue".
   - In data terms, does "same issue" mean:
     - *Interpretation A:* Same category only (yields 347 repeat contacts).
     - *Interpretation B:* Same product SKU only (yields 2,455 repeat contacts).
     - *Interpretation C:* Same category AND same product SKU (yields 270 repeat contacts).
     - *Interpretation D:* Any subsequent contact by that customer within 30 days (yields 3,070 repeat contacts).

2. **Resolving Ambiguous Fallback Order Joins:**
   - 4,107 tickets have blank `order_id`. While 3,174 match exactly 1 order for `(customer_id, product_sku)`, **933 match multiple orders** (up to 4 orders).
   - The policy does not specify whether to tie to the closest preceding order by date, the highest-value order, or leave the order association unlinked.

3. **Treatment of CSAT on Unresolved Tickets:**
   - Policy states surveys are sent on resolution or 72h auto-closure, yet 249 open/pending tickets have scores.
   - Should these premature ratings be included in overall CSAT calculations, or filtered out until resolution?

4. **Handling of Telephony Junk Transcripts:**
   - Sameer noted ~40 failed IVR transcripts. Should these tickets remain in agent volume metrics, or should voice agents receive an exemption/adjustment for dropped calls and corrupted transcripts?

5. **Dual-Remedy Tickets / Orders:**
   - 6 tickets have both refund and replacement flags set, and 131 orders have both across multiple tickets. Should financial summaries sum both costs, or treat the secondary transaction as an accounting reconciliation error?

6. **Freshdesk Legacy Migration Timestamp Adjustment:**
   - While the +5:30 UTC-to-IST correction on `legacy_fd.resolved_at` resolves all 2,309 negative handle times, should the final application expose raw exported timestamps alongside normalized timestamps, or apply the normalization directly in the data pipeline?

---

## 20. Decisions We Will Need to Make Before Building the Final Solution

1. **Fair Agent Evaluation & Segmented Ranking:**
   - Avoid a naive "bottom 10" ranking that conflates Tier 1 and Tier 2 / hardware triage queues.
   - Establish separate leaderboards:
     - **Frontline General (Tier 1):** Chat, Email, Voice, Logistics, Billing, Returns Desk (evaluated on SLA compliance, handle time in hours, CSAT, volume).
     - **Escalations & Hardware Triage (Tier 2 & Rota):** Escalations & Warranty (`A3039`–`A3044`) and triage rota agents (`A3004`–`A3007`) evaluated on resolution rate in days, complex RMA resolution, and root-cause tagging rather than pure CSAT volume.
   - Ensure minimum response thresholds before calculating CSAT averages for bonuses/training flags.

2. **Legacy Timestamp Harmonization Pipeline:**
   - Implement an automated ETL normalization step that adds 5 hours and 30 minutes to `resolved_at` exclusively for `source_system == 'legacy_fd'`, ensuring handle times are positive and comparable across all 18 months.

3. **Fallback Order Join Deterministic Rule:**
   - When `order_id` is missing and multiple orders match `(customer_id, product_sku)`, join with the most recent order placed prior to `created_at`. If no prior order exists, join with the earliest subsequent order.

4. **FCR Baseline Rule Selection:**
   - Adopt `(customer_id + product_sku within 30 days)` as the primary operational FCR metric, as hardware support tickets are product-specific. Provide toggle or secondary view for category-level recurrence.

5. **Costing Standards Implementation:**
   - Use the official Policy §4 and §5 cost standards as the primary financial model:
     - Handling cost: Chat Rs 210, Email Rs 260, Voice Rs 520, Social Rs 240
     - Transfers: Rs 305 per transfer
     - SLA Breach: Rs 350 per breached ticket
     - Replacements: `unit_cost_inr` + Rs 340 logistics
   - Provide a comparison toggle against Arjun Mehta's flat Rs 2,500 replacement estimate to clearly show Finance why their arithmetic overstated replacement costs by Rs 1.32M.

6. **Architectural & Performance Constraint (Zero Per-Ticket API Cost):**
   - Comply strictly with Arjun Mehta's budget directive: eliminate external per-ticket LLM API calls.
   - Build all analytics, metrics, NLP/issue tagging, and visual reporting using deterministic, local, lightning-fast Python/JavaScript engines that run completely free of per-ticket operational fees.

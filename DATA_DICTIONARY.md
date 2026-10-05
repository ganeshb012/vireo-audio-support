# Vireo Audio — Support Desk Data Dictionary & Schema Specification

**Document Version:** 1.0  
**Scope:** Helpdesk, Orders, Roster, Customer, and Product Schemas  
**Effective Range:** 1 January 2025 – 30 June 2026  
**Author:** Antigravity AI  

---

## 1. Relational Entity Architecture

```
               +------------------+
               |  customers.csv   |
               +------------------+
               | PK: customer_id  |
               +--------+---------+
                        |
            +-----------+-----------+
            |                       |
            v                       v
+-----------------------+   +-----------------------+
|      orders.csv       |   |      tickets.csv      |
+-----------------------+   +-----------------------+
| PK: order_id          |   | PK: ticket_id         |
| FK: customer_id       |<--| FK: order_id (nullab) |
| FK: sku               |   | FK: customer_id       |
+-----------+-----------+   | FK: product_sku       |
            |               | FK: agent_id          |
            |               +-----------+-----------+
            |                           |
            v                           v
+-----------------------+   +-----------------------+
|     products.csv      |   |      agents.csv       |
+-----------------------+   +-----------------------+
| PK: sku               |   | PK: agent_id          |
+-----------------------+   +-----------------------+
```

---

## 2. Table Specifications

### 2.1. `tickets.csv` (11,750 rows, 21 columns)
Contains individual customer support interaction records.

| Field Name | Storage Type | Nullable? | Description & Business Rules |
| :--- | :--- | :--- | :--- |
| `ticket_id` | String (PK) | No | Helpdesk ticket reference (e.g., `TK-240001`). Unique across all rows. |
| `created_at` | Datetime | No | Ticket creation timestamp in Indian Standard Time (IST). |
| `first_response_at` | Datetime | No | Timestamp of first reply by human agent (IST). Measured from `created_at` for SLA. |
| `resolved_at` | Datetime | Yes | Resolution timestamp. Null for `open` (335) and `pending` (232) tickets. Reconstructed from legacy event logs in UTC for `legacy_fd` tickets. |
| `status` | Categorical | No | Ticket state: `resolved` (10,138), `closed` (1,045), `open` (335), `pending` (232). `resolved` + `closed` = completed attendance. |
| `channel` | Categorical | No | Intake channel: `chat` (5,102), `email` (3,644), `voice` (1,833), `social` (1,171). |
| `customer_id` | String (FK) | No | Reference to `customers.customer_id`. |
| `order_id` | String (FK) | Yes | Reference to `orders.order_id`. Null on 4,107 rows where customer did not quote order number. |
| `product_sku` | String (FK) | No | Reference to `products.sku`. |
| `category` | Categorical | No | Intake category tag (Charging & Battery, Delivery, Connectivity, Warranty, etc.). |
| `priority` | Categorical | No | Urgency tag: `Normal` (8,442), `High` (2,056), `Low` (1,252). |
| `assigned_team` | Categorical | No | Team first routed to: Chat Frontline, Logistics, Email Frontline, Billing, Escalations & Warranty, Returns Desk, Voice Frontline. |
| `agent_id` | String (FK) | No | Resolving agent key into `agents.agent_id`. **Must join strictly on ID, never name.** |
| `transfers` | Integer | No | Count of internal team hand-offs (0, 1, or 2). Each transfer incurs ₹305 re-handling cost. |
| `csat_score` | Float | Yes | Customer satisfaction survey rating (1.0 to 5.0). Blank (6,554 rows) indicates non-response; must be excluded from averages. |
| `refund_amount_inr` | Float | Yes | Direct refund processed on the ticket in INR. Populated on 1,869 rows. |
| `refund_reason_code`| Categorical | Yes | Dropdown code selected by agent (Policy §5): `RETURN-QC-OK`, `DUP-PAYMENT`, `CANCEL`, `DOA-REPL`, `LOST-TRANSIT`, `PRICE-ADJ`, `WTY-BUYBACK`, `GW-OTHER`. |
| `replacement_issued`| Categorical | No | Hardware unit replacement dispatch flag (`Y` on 1,896 rows, `N` on 9,854 rows). |
| `customer_message` | Text | No | Customer opening query or IVR speech transcript. Contains ~40 failed telephony strings. |
| `agent_notes` | Text | No | Closing diagnostic summary and actions logged by the resolving agent. |
| `source_system` | Categorical | No | Originating CRM: `helpdesk` (8,376 rows, live from Sep 14, 2025) or `legacy_fd` (3,374 rows). |

---

### 2.2. `agents.csv` (44 rows, 8 columns)
Support staff roster and assignment details.

| Field Name | Storage Type | Nullable? | Description & Business Rules |
| :--- | :--- | :--- | :--- |
| `agent_id` | String (PK) | No | Unique agent identifier (`A3001` to `A3044`). |
| `name` | String | No | Display name. **Non-unique:** Two agents share the name "Kavya Pandey" (`A3006` in Indore, `A3029` in Bengaluru). |
| `site` | Categorical | No | Location: `Bengaluru` (25) or `Indore` (19). Indore provides exclusive 24x7 night coverage. |
| `team` | Categorical | No | Department assignment: Chat, Email, Voice, Logistics, Billing, Returns Desk, Escalations & Warranty. |
| `shift` | Categorical | No | Shift window (IST): `Morning` (06:00–14:00), `Day` (14:00–22:00), `Night` (22:00–06:00). |
| `tier` | Integer | No | Support tier: `1` (Frontline generalist, 38 agents) or `2` (Certified warranty specialist, 6 agents). |
| `from_date` | Date | No | Start date of current assignment. |
| `to_date` | Date | Yes | End date (all rows currently null, indicating active tenure). |

---

### 2.3. `customers.csv` (9,500 rows, 6 columns)
Customer profile and loyalty tier records.

| Field Name | Storage Type | Nullable? | Description & Business Rules |
| :--- | :--- | :--- | :--- |
| `customer_id` | String (PK) | No | Unique customer identifier (`C10001` to `C19500`). |
| `name` | String | No | Customer full name. |
| `city` | String | No | Customer residential city (33 major Indian metro areas). |
| `state` | String | No | Customer state or Union Territory. |
| `signup_date` | Date | No | Registration date with Vireo Audio. |
| `care_plus` | Categorical | No | Extended warranty subscription status (`Y` = 2,889, `N` = 6,611). |

---

### 2.4. `orders.csv` (15,500 rows, 8 columns)
E-commerce retail sales transactions.

| Field Name | Storage Type | Nullable? | Description & Business Rules |
| :--- | :--- | :--- | :--- |
| `order_id` | String (PK) | No | Unique transaction reference (`VR880001` to `VR910000`). |
| `customer_id` | String (FK) | No | Purchasing customer key into `customers.csv`. |
| `sku` | String (FK) | No | Purchased product key into `products.csv`. |
| `order_date` | Date | No | Date order was placed (15 Jun 2024 to 30 Jun 2026). |
| `channel` | Categorical | No | Sales platform: `vireo.in`, `Amazon`, `Flipkart`, `QuickComm`. |
| `qty` | Integer | No | Quantity purchased (1 or 2 units). |
| `order_value_inr` | Integer | No | Total order value in INR. |
| `lot_code` | String | No | Manufacturing production batch printed on packaging (e.g., `PL2-2510-1`). |

---

### 2.5. `products.csv` (14 rows, 7 columns)
Hardware catalog and planning cost benchmarks.

| Field Name | Storage Type | Nullable? | Description & Business Rules |
| :--- | :--- | :--- | :--- |
| `sku` | String (PK) | No | Stock Keeping Unit (e.g., `VA-EB-PL2`). |
| `product_name` | String | No | Official marketing name. |
| `family` | Categorical | No | Product group: `earbuds`, `headphones`, `watch`, `speaker`, `accessory`. |
| `launch_date` | Date | No | Commercial release date. |
| `unit_cost_inr` | Integer | No | Landed bill-of-materials manufacturing cost in INR. |
| `retail_price_inr`| Integer | No | Retail selling price (MRP) in INR. |
| `warranty_months` | Integer | No | Manufacturer warranty duration (6 or 12 months). |

---

## 3. Relational Joins & Fallback Rules

### 3.1. Primary Joins
- `tickets.customer_id` $\rightarrow$ `customers.customer_id` (100% matched, 0 orphans).
- `tickets.agent_id` $\rightarrow$ `agents.agent_id` (100% matched, 0 orphans).
- `tickets.product_sku` $\rightarrow$ `products.sku` (100% matched, 0 orphans).

### 3.2. Order Fallback Join Algorithm
When `tickets.order_id` is populated (7,643 tickets), link directly to `orders.order_id`.
When `tickets.order_id` is null (4,107 tickets), execute the following deterministic fallback matching:
1. Candidate matching: Identify all orders where `orders.customer_id == tickets.customer_id` AND `orders.sku == tickets.product_sku`.
2. Unique Match: For 3,174 tickets, exactly 1 order matches. Link immediately.
3. Multiple Matches: For 933 tickets, multiple prior orders exist. **Deterministic Tie-Breaker:** Select the order placed prior to ticket creation with the minimum calendar distance:
   $$\text{order}^* = \arg\min_{o} (\text{created\_at} - \text{order\_date}_o) \quad \text{s.t. } \text{created\_at} \ge \text{order\_date}_o$$
   *(If no prior order exists, select the earliest chronologically).*

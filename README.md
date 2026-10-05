# Vireo Audio — Customer Support Desk Analytics & Operational Assessment Tool

An end-to-end analytics platform, operational audit pipeline, and interactive executive dashboard built for **Vireo Audio Pvt. Ltd.** to analyze 11,750 customer support tickets, eliminate operational policy leakage, optimize First-Response SLAs, and fairly allocate the ₹4 Lakh Q3 agent training budget.

---

## 1. Prerequisites

- **Python:** 3.10, 3.11, 3.12, or 3.13
- **Operating System:** Windows, macOS, or Linux
- **RAM:** Minimum 2 GB available RAM

---

## 2. Installation

1. Clone or download this project directory.
2. In your terminal, navigate to the project directory:
   ```bash
   cd Banao-assessment
   ```
3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

*Dependencies installed:* `streamlit>=1.30.0`, `pandas>=2.0.0`, `numpy>=1.24.0`, `plotly>=5.18.0`.

---

## 3. Data File Placement

The application automatically locates and ingests data files directly from the working directory. Files can be named either with their default names or with their supplied UUID prefixes:

- `tickets.csv` (or `*tickets.csv`) — 11,750 support ticket records
- `agents.csv` (or `*agents.csv`) — 44 agent roster assignments
- `customers.csv` (or `*customers.csv`) — 9,500 customer records
- `orders.csv` (or `*orders.csv`) — 15,500 e-commerce order records
- `products.csv` (or `*products.csv`) — 14 product catalog benchmarks
- `support-policy.pdf` — Support operating policy v3.2
- `email-thread.txt` — Stakeholder context from Priya, Neha, Sameer, and Arjun

*Note: Source CSV files are never modified, renamed, or overwritten by this tool.*

---

## 4. How to Run the Application

### A. Run Deterministic Validation & Test Suite
Verify that all 13 quantitative assertions, legacy timestamp corrections, and policy calculations pass:
```bash
python test_pipeline.py
```

### B. Launch the Interactive Dashboard
Launch the local Streamlit dashboard:
```bash
python -m streamlit run app.py
```
Once launched, the dashboard will automatically open in your default browser at:  
👉 **`http://localhost:8501`**

---

## 5. How Calculations Work

1. **CSAT Calculation:**
   - Strict average across non-null ratings ($1 \le \text{csat} \le 5$).
   - Excludes all 6,554 blank surveys (Policy §8).
   - Excludes the 249 premature ratings attached to `open` or `pending` tickets from completed attendance scorecards.
2. **Handle Time Normalization:**
   - Measured as $\text{resolved\_at} - \text{first\_response\_at}$.
   - Reconstructed timestamps for pre-migration `legacy_fd` tickets were stored in UTC. An automated $+05:30$ offset is applied to `legacy_fd.resolved_at` to convert UTC to IST, eliminating 100% of the 2,309 negative handle times. Unresolved tickets remain null.
3. **First-Response SLA & Penalties:**
   - Evaluated against channel targets: Chat (15m), Voice (120m), Social (240m), Email (480m).
   - Each breach incurs an automated ₹350 store credit liability per Policy §3 (1,064 breaches = ₹372,400).
4. **Peer-Normalized Composite Agent Scoring:**
   - Agents are grouped into 8 operational cohorts (Chat, Email, Voice, Logistics, Billing, Returns, Hardware Rota, Tier 2).
   - Evaluated via:
     $$\text{Composite Score} = 0.70 \times Z_{\text{CSAT, peer}} - 0.30 \times Z_{\text{HT, peer}}$$
   - Lowest composite scores identify candidates for the **Training Review List**.
5. **Replacement Cost Accounting:**
   - Evaluated strictly using the official Policy §5 standard:
     $$\text{Replacement Cost} = \text{unit\_cost\_inr} + ₹340 \text{ logistics}$$
   - Arjun Mehta's flat ₹2,500 estimate is documented as an unapproved budgeting benchmark overstating cost by ₹1.32M (+38.7%).
6. **Operational FCR Proxy:**
   - Tracks repeat contacts within 30 days of prior resolution for the same customer and same product SKU (proxy for "same issue" per Policy §10).

---

## 6. How Validation Works

Automated test runner `test_pipeline.py` executes 13 quantitative tests:
1. Row count integrity across all 5 tables (100% match).
2. Channel SLA threshold verification (1,064 breaches).
3. ₹350 breach credit calculation (₹372,400.00).
4. Blank CSAT non-imputation check (6,554 nulls excluded; 3.3266 mean across all valid ratings, 3.3259 on completed attendance).
5. Open/pending ticket exclusion from attendance CSAT.
6. Legacy timestamp normalization (+5:30 eliminates all negative handle times).
7. Agent joins strictly use `agent_id` (disambiguates the two Kavya Pandeys: `A3006` and `A3029`).
8. Tier 2 segmentation into dedicated peer groups.
9. Peer-normalized composite formula precision.
10. Dual-remedy order detection (131 orders).
11. Goodwill cap overspend detection (32 violations, ₹99,732 overage).
12. FCR proxy detection (2,455 repeat contacts, ₹680,740 cost).
13. Policy replacement cost formula compliance (₹3,415,990 spend).

---

## 7. AI Assistance Used

- **Development Pair Programming:** Google Deepmind's Antigravity CLI was used as an agentic pair-programming assistant to inspect files, draft test cases, structure modules, and build the Streamlit user interface.
- **Deterministic Pipeline Execution:** All analytical metrics, Z-score formulas, SQL-like joins, and financial calculations are 100% deterministic Python/pandas operations.
- **Local Execution:** No runtime AI calls are required for dashboard execution or testing.

---

## 8. Discarded Approaches & Rationale

1. **Discarded: Raw CSAT Bottom-10 Ranking**
   - *Reason Discarded:* Raw CSAT flags 100% Tier 2 Escalations agents (`A3039`–`A3044`) and Hardware Triage agents (`A3004`–`A3007`). As Neha Kulkarni warned, these agents handle high-friction hardware defects and angry customers by design. Flagging them penalizes queue assignment rather than agent skill. Peer normalization replaced this.
2. **Discarded: Arjun Mehta's Flat ₹2,500 Replacement Cost Metric**
   - *Reason Discarded:* Overstates replacement spend by ₹1.32M compared to the official Policy §5 formula (`unit_cost` + ₹340).
3. **Discarded: External Per-Ticket LLM Sentiment API Calls**
   - *Reason Discarded:* Arjun Mehta mandated that any solution must be cheap to run (no ₹5/ticket model calls across 12k tickets). All text analysis runs locally with ₹0 API fees.
4. **Discarded: Declaring a Certified "Manufacturing Defect"**
   - *Reason Discarded:* Helpdesk ticket logs cannot certify physical engineering causes without factory RMA teardown logs. We strictly phrase the Pulse 2 finding as *"evidence consistent with a batch-specific hardware failure."*

---

## 9. Budget & Cost Constraint Compliance

- **Total Per-Ticket External API Cost:** **₹0.00**
- All pipelines, charts, and metric calculations run 100% locally on-device.

# Vireo Audio Support Desk Assessment — 3-Minute Video Demo Script

**Total Runtime:** Exactly 3 Minutes (180 Seconds)  
**Presenter:** Analytics Lead  
**Dashboard Platform:** Streamlit (`python -m streamlit run app.py`)  

---

### Sequence Breakdown

```
+---------------+-------------------------------------------------+-------------------------------------------------------------+
| Timestamp     | On-Screen Action                                | Spoken Narration Script                                     |
+---------------+-------------------------------------------------+-------------------------------------------------------------+
| 0:00 – 0:20   | Display README.md in editor / browser.          | "Welcome. Today we present the Vireo Audio Support Desk     |
| (20 seconds)  | Highlight project title & business goal.        | Analytics and Assessment tool. Our primary objective is to  |
|               |                                                 | evaluate 11,750 customer tickets, identify operational      |
|               |                                                 | leakage, fairly evaluate agent coaching needs, and target   |
|               |                                                 | Priya Raman's ₹4 Lakh Q3 training budget effectively."     |
+---------------+-------------------------------------------------+-------------------------------------------------------------+
| 0:20 – 0:50   | Open terminal. Run:                             | "Let's start by running our automated validation suite:     |
| (30 seconds)  | `python test_pipeline.py`                       | python test_pipeline.py. The pipeline ingests all 5 raw     |
|               | Show 13/13 PASS checks on screen.               | CSVs without altering source files, corrects a 5.5-hour     |
|               | Launch: `python -m streamlit run app.py`       | legacy Freshdesk UTC timezone mismatch, disambiguates the   |
|               |                                                 | two agents named Kavya Pandey using agent_id, and validates |
|               |                                                 | all 13 deterministic assertions with 100% pass rate."       |
+---------------+-------------------------------------------------+-------------------------------------------------------------+
| 0:50 – 1:30   | Open Streamlit dashboard in browser.            | "Here is the Executive Dashboard. In Tab 2, we present the  |
| (40 seconds)  | Navigate to Tab 1 (KPIs) then                   | Training Review List. Notice that we rejected raw CSAT      |
|               | Tab 2 (Training Review List).                   | ranking because raw CSAT flagged 100% Tier 2 and hardware   |
|               | Expand queue-bias comparison drawer.            | triage agents simply because they handle angry customers    |
|               |                                                 | with broken hardware. By using a peer-normalized composite  |
|               |                                                 | score (70% CSAT Z-score, 30% handle time Z-score), 8 out of |
|               |                                                 | 10 names change, correctly identifying true coaching review |
|               |                                                 | candidates across Chat, Email, Logistics, and Returns."     |
+---------------+-------------------------------------------------+-------------------------------------------------------------+
| 1:30 – 2:00   | Switch to Tab 3 (SLA Performance) and           | "In Tab 3, we analyze First-Response SLAs: 1,064 breaches   |
| (30 seconds)  | Tab 4 (Policy Leakage).                         | incur ₹3.72 Lakh in automated ₹350 store credits, driven    |
|               | Point out ₹228,900 SLA savings and              | heavily by Email. By targeting a 3.5% breach rate, we model |
|               | ₹235,500 dual-remedy leakage table.             | ₹2.28 Lakh in avoided penalties. In Tab 4, we expose 131   |
|               |                                                 | dual-remedy orders where customers received both a refund   |
|               |                                                 | and a replacement unit—violating Policy §5 and creating an  |
|               |                                                 | immediate ₹2.35 Lakh recoverable leakage opportunity."      |
+---------------+-------------------------------------------------+-------------------------------------------------------------+
| 2:00 – 2:25   | Switch to Tab 5 (Product Signals).              | "Tab 5 examines replacement spend. Finance assumed festive  |
| (25 seconds)  | Show Pulse 2 monthly trend and lot code scatter | volume doubled replacements, but our lot-code analysis      |
|               | plot highlighting Q4 2025 anomalous batches.    | reveals empirical evidence consistent with a batch-specific |
|               |                                                 | hardware failure in Q4 2025 Pulse 2 lots, where failure     |
|               |                                                 | rates surged to 38%. We clearly state the limitation that   |
|               |                                                 | helpdesk data alone cannot certify physical root cause."    |
+---------------+-------------------------------------------------+-------------------------------------------------------------+
| 2:25 – 2:45   | Switch to Tab 7 (Data Reliability) and terminal | "Tab 7 audits data reliability, proving that legacy         |
| (20 seconds)  | showing test results.                           | timestamps are normalized, ~40 junk IVR transcripts are     |
|               |                                                 | quarantined, and joins strictly use agent_id. All metrics   |
|               |                                                 | are verified deterministically."                            |
+---------------+-------------------------------------------------+-------------------------------------------------------------+
| 2:45 – 3:00   | Display README / Methodology conclusion.        | "In closing: Antigravity CLI provided development           |
| (15 seconds)  | Wrap up with budget recommendation.             | assistance, but all calculations run locally in Python with |
|               |                                                 | zero paid per-ticket API calls. Raw CSAT ranking was        |
|               |                                                 | discarded in favor of fair peer normalization. The ₹4 Lakh  |
|               |                                                 | budget is protected for true coaching. Thank you."          |
+---------------+-------------------------------------------------+-------------------------------------------------------------+
```

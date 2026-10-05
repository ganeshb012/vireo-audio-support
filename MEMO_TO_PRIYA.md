# MEMORANDUM

**TO:** Priya Raman, Head of Customer Experience, Vireo Audio Pvt. Ltd.  
**FROM:** Kabir Nanda / Analytics Team  
**DATE:** 5 October 2026  
**SUBJECT:** Support Desk Operational Audit, Agent Review List & Q3 Training Allocation  

---

### Executive Recommendation
We have completed a comprehensive operational audit of Vireo's 11,750 support tickets across 18 months. Our core finding is that **raw CSAT ranking is structurally biased by queue difficulty**: a raw bottom-10 list flags 100% of its agents from Tier 2 Escalations and the Hardware Triage Rota ("Kavya's four"), punishing agents assigned to angry customers and defective hardware.

Instead, we recommend a **Peer-Normalized Training Review List** that evaluates agents strictly against teammates handling the same inquiry types. We also propose a **Dual-Track Operational Program** that recovers **₹5.64 Lakh in modeled financial opportunity** (easily funding your ₹4 Lakh training budget) by eliminating dual-remedy leakage and cutting SLA breaches from 9.06% to 3.50%.

---

### 1. Proposed Training Review List (Peer-Normalized Composite Score)
Evaluated via `Score = 0.70 * Z_CSAT_peer - 0.30 * Z_HandleTime_peer`. *This is an operational coaching signal, not proof of lowest capability:*

| Rank | Agent ID | Name | Department / Peer Group | CSAT | Handle Time | Primary Coaching Focus |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | `A3008` | Isha George | Frontline - Chat Frontline | 3.44 | 2.8 hrs | CSAT lags chat peers by 1.3σ; customer empathy coaching |
| **2** | `A3026` | Suresh Pereira | Frontline - Logistics | 3.12 | 41.9 hrs | Tracking escalation speed & courier coordination |
| **3** | `A3015` | Ishaan Dutta | Frontline - Email Frontline | 3.39 | 8.6 hrs | Email handle time is 1.8σ slower than department peers |
| **4** | `A3038` | Varun Reddy | Frontline - Returns Desk | 3.21 | 35.6 hrs | Return pickup follow-up & QC diagnostic accuracy |
| **5** | `A3020` | Riya Pillai | Frontline - Chat Frontline | 3.48 | 7.7 hrs | Chat concurrency management & macro speed |
| **6** | `A3041` | Jaspreet Desai | Tier 2 (Escalations & Warranty) | 2.42 | 131.5 hrs | Complex warranty case closure & RMA partner turnaround |
| **7** | `A3034` | Meera Pereira | Frontline - Billing | 3.37 | 5.0 hrs | Payment gateway dispute resolution efficiency |
| **8** | `A3017` | Aadhya Rao | Frontline - Email Frontline | 3.53 | 7.1 hrs | Asynchronous email diagnostic completeness |
| **9** | `A3004` | Siddharth Kapoor | Hardware Triage Rota | 2.98 | 2.9 hrs | De-escalation techniques for angry hardware claimants |
| **10**| `A3024` | Suresh Sethi | Frontline - Chat Frontline | 3.54 | 3.8 hrs | Chat closing clarity & customer sentiment recovery |

---

### 2. Operational Issues & Modeled Financial Opportunities

1. **First-Response SLA Breaches (₹228,900 Modeled Saving):**
   - 1,064 tickets breached channel SLAs (9.06% breach rate), incurring **₹372,400 in automatic ₹350 store credits** (Policy §3).
   - Email is the largest bottleneck (445 breaches; 12.21% breach rate).
   - *Target:* Reduce breaches to 3.50% ($\le 410$ breaches), avoiding 654 penalties and saving **₹228,900**.
2. **Dual-Remedy Policy Leakage (₹235,500 Modeled Saving):**
   - 131 orders received **both a refund and a replacement unit** (violating Policy §5), costing ₹590,934 combined.
   - *Target:* 0 dual remedies. Enforcing a CRM single-remedy validation lock recovers **₹235,500** in redundant replacement costs.
3. **Goodwill Cap Overages (₹99,732 Modeled Saving):**
   - 32 `GW-OTHER` refunds breached the ₹500 policy cap (reaching up to ₹11,998). Capping at ₹500 saves **₹99,732**.
4. **Pulse 2 Hardware Signal:**
   - Replacements doubled not because of "festive volume," but due to **evidence consistent with a batch-specific hardware issue in Q4 2025 Pulse 2 batches** (`PL2-2510-*` to `PL2-2512-*`), which exhibited an abnormal 37.5% failure rate (₹911,820 in excess replacement cost). Helpdesk data alone cannot certify physical root cause.

---

### 3. Recommended Allocation of the ₹4 Lakh Training Budget
We advise against spending training funds on CRM control gaps or hardware manufacturing defects. Allocate as follows:
- **₹2.0 Lakh (Frontline FCR & Troubleshooting):** Upskill the 10 flagged review candidates on diagnostic completeness to reduce the 2,455 repeat contacts.
- **₹1.0 Lakh (SLA Queue Management Coaching):** Train email and chat teams on queue prioritization and triage macros.
- **₹1.0 Lakh (Quality Assurance Audits & Contingency):** Monthly supervisor spot-checks and de-escalation coaching.

### 4. What Training CAN vs. CANNOT Fix
- **Training CAN Fix:** First-contact resolution quality, customer empathy, diagnostic accuracy, and SLA intake speed.
- **Requires CRM / Operational Locks (Zero Budget Cost):** Dual-remedy prevention, goodwill cap enforcement, and restricting replacement approvals strictly to Tier 2 roles (blocking the 1,281 unauthorized Tier 1 replacements).
- **Requires Product / Manufacturing Action:** Pulse 2 charging case battery circuit failures require OEM vendor warranty claims and engineering firmware calibration. Training support agents cannot fix defective hardware.

### 5. Key Limitations
- Customer messages alone cannot certify the physical engineering root cause of the Pulse 2 batch issue without lab RMA reports.
- Calculations reflect modeled potential savings based on observed 18-month historical rates, requiring active operational enforcement.

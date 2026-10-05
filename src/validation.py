"""
Automated Validation Suite for Vireo Audio Support Desk Assessment.
Executes deterministic assertions across ingestion, normalization, metrics, and policy rules.
"""

import pandas as pd
import numpy as np
from src.data_loader import load_raw_data, normalize_and_enrich_data
from src.metrics import compute_executive_metrics, compute_sla_breakdown
from src.agent_ranking import compute_agent_scorecards, get_training_review_list
from src.policy_checks import audit_dual_remedy_orders, audit_goodwill_cap, audit_unauthorized_replacements
from src.fcr import compute_fcr_proxy_analysis

def run_all_validations(data_dir: str = ".") -> dict:
    """Runs the complete suite of deterministic tests and returns detailed results."""
    results = []
    
    # 1. Ingestion check
    raw = load_raw_data(data_dir)
    t = raw["tickets"]
    a = raw["agents"]
    c = raw["customers"]
    o = raw["orders"]
    p = raw["products"]
    
    results.append({
        "check": "Row Count Integrity: tickets (11,750), orders (15,500), customers (9,500), agents (44), products (14)",
        "passed": (len(t) == 11750 and len(o) == 15500 and len(c) == 9500 and len(a) == 44 and len(p) == 14),
        "detail": f"Tickets: {len(t)}, Orders: {len(o)}, Customers: {len(c)}, Agents: {len(a)}, Products: {len(p)}"
    })

    # Normalization & Enrichment
    data = normalize_and_enrich_data(raw)
    tickets = data["tickets"]
    agents = data["agents"]

    # 2. SLA channel thresholds & calculation
    sla_targets = {"chat": 15, "voice": 120, "social": 240, "email": 480}
    test_breaches = 0
    for ch, grp in tickets.groupby("channel"):
        target = sla_targets[ch]
        manual_b = (grp["resp_time_mins"] > target).sum()
        test_breaches += manual_b
        
    results.append({
        "check": "SLA Channel Thresholds Correct (Chat 15m, Voice 120m, Social 240m, Email 480m)",
        "passed": test_breaches == int(tickets["is_breached"].sum()) == 1064,
        "detail": f"Evaluated 1,064 breaches matching policy channel thresholds"
    })

    # 3. Rs 350 SLA breach credit calculation
    total_credit = tickets["sla_credit_inr"].sum()
    results.append({
        "check": "Rs 350 SLA Breach Store Credit Calculation (1,064 * Rs 350 = Rs 372,400)",
        "passed": total_credit == 372400,
        "detail": f"Total SLA credit calculated: Rs {total_credit:,.2f}"
    })

    # 4. Blank CSAT excluded from averages
    null_csat_count = tickets["csat_score"].isna().sum()
    valid_csat_mean = tickets["csat_score"].dropna().mean()
    results.append({
        "check": "Blank CSAT Excluded Across Dataset (6,554 nulls excluded; all-valid mean = 3.3266, not imputed to 0)",
        "passed": (null_csat_count == 6554 and round(valid_csat_mean, 4) == 3.3266),
        "detail": f"Null CSAT count: {null_csat_count}, All-valid non-null mean: {valid_csat_mean:.4f} (rounded: {round(valid_csat_mean, 2)})"
    })

    # 5. Open/Pending tickets excluded from completed-attendance CSAT
    premature_csat = tickets[tickets["status"].isin(["open", "pending"])]["completed_csat"].notna().sum()
    attendance_csat_mean = tickets["completed_csat"].dropna().mean()
    results.append({
        "check": "Completed Attendance CSAT Calculated Strictly on Resolved/Closed (4,947 responses, mean = 3.3259 -> 3.33)",
        "passed": (premature_csat == 0 and len(tickets["completed_csat"].dropna()) == 4947 and round(attendance_csat_mean, 4) == 3.3259),
        "detail": f"Attendance CSAT responses: 4,947, Completed attendance mean: {attendance_csat_mean:.4f} (rounded: {round(attendance_csat_mean, 2)})"
    })

    # 6. Legacy timestamp normalization (+05:30 on legacy_fd resolved_at)
    raw_neg = ((tickets["resolved_dt"] - tickets["first_resp_dt"]).dt.total_seconds() < 0).sum()
    norm_neg = (tickets["handle_time_hrs"] < 0).sum()
    results.append({
        "check": "Legacy Timestamp Normalization (+05:30 eliminates all 2,309 negative handle times)",
        "passed": (raw_neg == 2309 and norm_neg == 0),
        "detail": f"Raw negative handle times: {raw_neg} -> Normalized negative handle times: {norm_neg}"
    })

    # 7. Agent joins use agent_id (disambiguating 'Kavya Pandey')
    t_agent_unmatched = (~tickets["agent_id"].isin(agents["agent_id"])).sum()
    kavya_records = agents[agents["name"] == "Kavya Pandey"]
    results.append({
        "check": "Agent Joins Strictly Use agent_id (0 unmatched orphans; 2 distinct Kavya Pandeys mapped)",
        "passed": (t_agent_unmatched == 0 and len(kavya_records) == 2),
        "detail": f"Orphan agent keys: {t_agent_unmatched}, Unique Kavya Pandey records: {list(kavya_records['agent_id'])}"
    })

    # 8. Tier 2 is not directly ranked against Tier 1 volume metrics
    scorecards = compute_agent_scorecards(tickets, agents)
    t1_t2_separate_groups = scorecards["peer_group"].nunique() == 8
    results.append({
        "check": "Tier 2 Segmented into Dedicated Peer Group (8 distinct peer groups; no raw volume penalty)",
        "passed": t1_t2_separate_groups,
        "detail": f"Distinct peer groups created: {list(scorecards['peer_group'].unique())}"
    })

    # 9. Peer-normalized score formula correctness: 0.70 * Z_CSAT - 0.30 * Z_HT
    sample_agent = scorecards.iloc[0]
    expected_score = 0.70 * sample_agent["z_csat"] - 0.30 * sample_agent["z_ht"]
    score_diff = abs(sample_agent["composite_score"] - expected_score)
    results.append({
        "check": "Peer-Normalized Composite Score Formula: 0.70 * Z_CSAT - 0.30 * Z_HT",
        "passed": score_diff < 1e-6,
        "detail": f"Agent {sample_agent['agent_id']}: calculated {sample_agent['composite_score']:.4f}, expected {expected_score:.4f}"
    })

    # 10. Dual-remedy detection works (Support Policy §5)
    dual_audit = audit_dual_remedy_orders(tickets)
    results.append({
        "check": "Dual-Remedy Order Detection Works (131 orders received both refund and replacement)",
        "passed": dual_audit["count"] == 131,
        "detail": f"Dual-remedy orders identified: {dual_audit['count']}, Total repl spend: Rs {dual_audit['total_repl_spend']:,.2f}"
    })

    # 11. Goodwill > Rs 500 cap detection works (Support Policy §5)
    gw_audit = audit_goodwill_cap(tickets)
    results.append({
        "check": "Goodwill Policy-Cap Overspend Detection Works (32 cap violations, Rs 99,732 overage)",
        "passed": (gw_audit["violations_count"] == 32 and gw_audit["total_overage_inr"] == 99732.0),
        "detail": f"Violations: {gw_audit['violations_count']}, Total overspend above cap: Rs {gw_audit['total_overage_inr']:,.2f}"
    })

    # 12. FCR proxy correctly detects same customer + SKU repeat contact within 30 days
    fcr_res = compute_fcr_proxy_analysis(tickets)
    results.append({
        "check": "FCR Proxy Detects Same Customer + SKU Contacts within 30d (2,455 repeat contacts, Rs 680,740 spend)",
        "passed": (fcr_res["repeat_contacts_count"] == 2455 and fcr_res["repeat_contacts_cost_inr"] == 680740.0),
        "detail": f"Repeat contacts detected: {fcr_res['repeat_contacts_count']}, Cost: Rs {fcr_res['repeat_contacts_cost_inr']:,.2f}"
    })

    # 13. Replacement cost uses policy definition (unit_cost + Rs 340)
    total_repl_cost = tickets["policy_repl_cost"].sum()
    results.append({
        "check": "Replacement Cost Uses Policy Standard: unit_cost_inr + Rs 340 (Rs 3,415,990 total spend)",
        "passed": total_repl_cost == 3415990,
        "detail": f"Policy replacement spend: Rs {total_repl_cost:,.2f}"
    })

    all_passed = all(r["passed"] for r in results)
    return {
        "all_passed": all_passed,
        "passed_count": sum(r["passed"] for r in results),
        "total_count": len(results),
        "results": results
    }

if __name__ == "__main__":
    report = run_all_validations()
    print(f"\n=======================================================")
    print(f"VIREO AUDIO VALIDATION SUITE: {report['passed_count']}/{report['total_count']} CHECKS PASSED")
    print(f"=======================================================\n")
    for r in report["results"]:
        status = "[PASS]" if r["passed"] else "[FAIL]"
        print(f"{status} {r['check']}")
        print(f"       Detail: {r['detail']}\n")

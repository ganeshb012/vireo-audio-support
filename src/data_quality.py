"""
Data Quality, Telephony Audit & Reliability Module.
Tracks anomalies, junk IVRs, duplicate agent names, and legacy timestamp adjustments.
"""

import pandas as pd
import numpy as np

def audit_data_quality(tickets: pd.DataFrame, agents: pd.DataFrame) -> dict:
    """Computes comprehensive data-quality metrics and flags."""
    # 1. Negative handle times raw vs normalized
    raw_ht = (tickets["resolved_dt"] - tickets["first_resp_dt"]).dt.total_seconds() / 3600.0
    raw_negative_count = int((raw_ht < 0).sum())
    norm_negative_count = int((tickets["handle_time_hrs"] < 0).sum())
    
    # 2. Duplicate display names
    dup_names = agents.groupby("name")["agent_id"].apply(list).to_dict()
    multi_agents = {k: v for k, v in dup_names.items() if len(v) > 1}
    
    # 3. Missing order IDs
    missing_order_count = int(tickets["order_id"].isna().sum())
    missing_order_pct = (missing_order_count / len(tickets)) * 100
    
    # 4. Junk IVR / Telephony errors
    def is_junk_telephony(msg):
        m = str(msg).strip()
        if any(tok in m for tok in ["[line dropped]", "[inaudible]", "[crosstalk]"]):
            return True, "Audio artifact"
        if m in ["-", ".", "...", "??", "test"]:
            return True, "Punctuation / test"
        if len(m) <= 5 and m != "":
            return True, "Truncated transcript"
        return False, "Normal"

    junk_flags = [is_junk_telephony(msg) for msg in tickets["customer_message"]]
    junk_mask = [j[0] for j in junk_flags]
    junk_reasons = [j[1] for j in junk_flags]
    
    junk_tickets_df = tickets[junk_mask].copy()
    junk_tickets_df["junk_reason"] = [r for r, m in zip(junk_reasons, junk_mask) if m]
    
    # 5. Premature CSAT on open/pending tickets
    premature_csat = tickets[tickets["status"].isin(["open", "pending"]) & tickets["csat_score"].notna()].copy()
    
    return {
        "raw_negative_handle_times": raw_negative_count,
        "normalized_negative_handle_times": norm_negative_count,
        "duplicate_agent_names": multi_agents,
        "missing_order_count": missing_order_count,
        "missing_order_pct": round(missing_order_pct, 2),
        "junk_ivr_count": len(junk_tickets_df),
        "junk_ivr_df": junk_tickets_df[["ticket_id", "channel", "status", "customer_message", "junk_reason"]],
        "premature_csat_count": len(premature_csat),
        "premature_csat_mean": premature_csat["csat_score"].mean() if len(premature_csat) > 0 else 0.0
    }

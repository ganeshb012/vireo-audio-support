"""
First-Contact Resolution (FCR) & Repeat Contact Analysis Module.
Calculates operational 30-day repeat contact proxies strictly per Support Policy §10.
"""

import pandas as pd
import numpy as np

def compute_fcr_proxy_analysis(tickets: pd.DataFrame) -> dict:
    """
    Computes First-Contact Resolution using the transparent Operational Proxy:
    'Same customer + same product_sku within 30 days of resolution.'
    
    Clearly labeled as an Operational Proxy because helpdesk logs lack a standardized
    sub-category issue identifier across all channels.
    """
    # Sort chronologically by customer and ticket creation
    df = tickets.sort_values(by=["customer_id", "created_dt"]).copy()
    
    total_tickets = len(df)
    repeat_ticket_indices = set()
    repeat_cost_total = 0.0
    
    # Iterate customers to find repeat contacts within 30 days of prior resolution
    for cust_id, grp in df.groupby("customer_id"):
        if len(grp) < 2:
            continue
        
        resolved_history = []
        for idx, row in grp.iterrows():
            c_time = row["created_dt"]
            sku = row["product_sku"]
            cost = row["contact_cost_inr"]
            
            is_repeat = False
            for prev_res, prev_sku in resolved_history:
                if pd.notna(prev_res):
                    diff_days = (c_time - prev_res).total_seconds() / 86400.0
                    if 0.0 <= diff_days <= 30.0 and sku == prev_sku:
                        is_repeat = True
                        break
            
            if is_repeat:
                repeat_ticket_indices.add(idx)
                repeat_cost_total += cost
                
            resolved_history.append((row["resolved_dt_norm"], sku))
            
    repeat_count = len(repeat_ticket_indices)
    fcr_rate = ((total_tickets - repeat_count) / total_tickets) * 100 if total_tickets > 0 else 0.0
    avg_repeat_cost = (repeat_cost_total / repeat_count) if repeat_count > 0 else 0.0
    
    # Modeled 15% improvement target
    target_reduction_pct = 15.0
    avoided_repeats = int(round(repeat_count * (target_reduction_pct / 100.0)))
    potential_savings = avoided_repeats * avg_repeat_cost

    return {
        "total_tickets": total_tickets,
        "repeat_contacts_count": repeat_count,
        "fcr_proxy_rate_pct": round(fcr_rate, 2),
        "repeat_contacts_cost_inr": repeat_cost_total,
        "avg_repeat_contact_cost_inr": round(avg_repeat_cost, 2),
        "target_reduction_pct": target_reduction_pct,
        "avoided_repeats_target": avoided_repeats,
        "potential_savings_inr": round(potential_savings, 2),
        "repeat_indices": repeat_ticket_indices
    }

"""
Policy Compliance & Operational Leakage Module.
Audits dual remedy violations, goodwill cap overages, and unauthorized frontline replacements.
"""

import pandas as pd
import numpy as np

def audit_dual_remedy_orders(tickets: pd.DataFrame) -> dict:
    """
    Identifies customer orders that received both a refund and a replacement.
    Support Policy §5 prohibits dual remedy on the same order.
    """
    valid_orders = tickets[tickets["order_id"].notna()].copy()
    
    order_summary = valid_orders.groupby("order_id").agg(
        ticket_count=("ticket_id", "count"),
        total_refund=("refund_amount_inr", "sum"),
        refund_ticket_count=("refund_amount_inr", lambda x: x.notna().sum()),
        repl_ticket_count=("replacement_issued", lambda x: (x == "Y").sum()),
        total_policy_repl_cost=("policy_repl_cost", "sum"),
        customer_id=("customer_id", "first"),
        product_sku=("product_sku", "first"),
        tickets_list=("ticket_id", lambda x: list(x))
    ).reset_index()

    dual_mask = (order_summary["refund_ticket_count"] > 0) & (order_summary["repl_ticket_count"] > 0)
    dual_orders_df = order_summary[dual_mask].copy()
    
    dual_orders_df["combined_spend"] = dual_orders_df["total_refund"] + dual_orders_df["total_policy_repl_cost"]
    
    # Calculate potential leakage savings (assuming secondary replacement is avoided)
    total_dual_orders = len(dual_orders_df)
    total_refund_spend = dual_orders_df["total_refund"].sum()
    total_repl_spend = dual_orders_df["total_policy_repl_cost"].sum()
    total_combined_spend = dual_orders_df["combined_spend"].sum()
    
    return {
        "count": total_dual_orders,
        "total_refund_spend": total_refund_spend,
        "total_repl_spend": total_repl_spend,
        "total_combined_spend": total_combined_spend,
        "potential_leakage_savings": total_repl_spend,
        "df": dual_orders_df.sort_values("combined_spend", ascending=False)
    }

def audit_goodwill_cap(tickets: pd.DataFrame) -> dict:
    """
    Audits adherence to Support Policy §5:
    'Goodwill credits are capped at Rs 500 per ticket and require Team Lead approval.'
    """
    gw_tickets = tickets[tickets["refund_reason_code"] == "GW-OTHER"].copy()
    total_gw = len(gw_tickets)
    
    over_cap_mask = gw_tickets["refund_amount_inr"] > 500.0
    over_cap_df = gw_tickets[over_cap_mask].copy()
    over_cap_df["overage_inr"] = over_cap_df["refund_amount_inr"] - 500.0
    
    violations_count = len(over_cap_df)
    total_gw_spend = gw_tickets["refund_amount_inr"].sum()
    total_overage = over_cap_df["overage_inr"].sum()
    
    return {
        "total_gw_tickets": total_gw,
        "violations_count": violations_count,
        "total_gw_spend": total_gw_spend,
        "total_overage_inr": total_overage,
        "max_goodwill_incurred": gw_tickets["refund_amount_inr"].max() if total_gw > 0 else 0.0,
        "df": over_cap_df.sort_values("overage_inr", ascending=False)
    }

def audit_unauthorized_replacements(tickets: pd.DataFrame, agents: pd.DataFrame) -> dict:
    """
    Audits adherence to Support Policy §6:
    'Tier 2 work is certified: only Tier 2 agents may approve warranty replacements.'
    """
    t_a = tickets.merge(agents[["agent_id", "tier", "team"]], on="agent_id", how="left")
    
    repl_tickets = t_a[t_a["replacement_issued"] == "Y"].copy()
    
    tier1_repl = repl_tickets[repl_tickets["tier"] == 1]
    tier2_repl = repl_tickets[repl_tickets["tier"] == 2]
    
    team_breakdown = tier1_repl.groupby("team").agg(
        replacement_count=("ticket_id", "count"),
        total_policy_cost=("policy_repl_cost", "sum")
    ).reset_index().sort_values("replacement_count", ascending=False)
    
    return {
        "tier1_count": len(tier1_repl),
        "tier1_spend": tier1_repl["policy_repl_cost"].sum(),
        "tier2_count": len(tier2_repl),
        "tier2_spend": tier2_repl["policy_repl_cost"].sum(),
        "team_breakdown": team_breakdown,
        "df": tier1_repl
    }

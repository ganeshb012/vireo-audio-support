"""
Data Loader & Normalization Module for Vireo Audio Support Desk.
Handles file discovery (with or without UUID prefixes), timestamp normalization,
and deterministic relational joins without modifying original source files.
"""

import os
import glob
import pandas as pd
import numpy as np

def find_file(directory: str, pattern: str) -> str:
    """Find a file matching pattern or base name."""
    # Direct match
    direct = os.path.join(directory, pattern)
    if os.path.exists(direct):
        return direct
    
    # Search with pattern
    matches = glob.glob(os.path.join(directory, f"*{pattern}"))
    if matches:
        return matches[0]
    
    raise FileNotFoundError(f"Could not locate file matching pattern '{pattern}' in '{directory}'")

def load_raw_data(data_dir: str = ".") -> dict:
    """Load all 5 CSV files from disk."""
    tickets_path = find_file(data_dir, "tickets.csv")
    agents_path = find_file(data_dir, "agents.csv")
    customers_path = find_file(data_dir, "customers.csv")
    orders_path = find_file(data_dir, "orders.csv")
    products_path = find_file(data_dir, "products.csv")

    tickets = pd.read_csv(tickets_path)
    agents = pd.read_csv(agents_path)
    customers = pd.read_csv(customers_path)
    orders = pd.read_csv(orders_path)
    products = pd.read_csv(products_path)

    return {
        "tickets": tickets,
        "agents": agents,
        "customers": customers,
        "orders": orders,
        "products": products,
        "paths": {
            "tickets": tickets_path,
            "agents": agents_path,
            "customers": customers_path,
            "orders": orders_path,
            "products": products_path
        }
    }

def normalize_and_enrich_data(raw_data: dict) -> dict:
    """
    Applies strict data cleaning, timestamp normalization (+5:30 on legacy_fd),
    deterministic order joins with fallback tie-breaking, and peer group assignments.
    """
    tickets = raw_data["tickets"].copy()
    agents = raw_data["agents"].copy()
    customers = raw_data["customers"].copy()
    orders = raw_data["orders"].copy()
    products = raw_data["products"].copy()

    # 1. Parse timestamps
    tickets["created_dt"] = pd.to_datetime(tickets["created_at"])
    tickets["first_resp_dt"] = pd.to_datetime(tickets["first_response_at"])
    tickets["resolved_dt"] = pd.to_datetime(tickets["resolved_at"])

    # 2. Legacy timestamp normalization (Policy §9: legacy_fd resolution was logged in UTC)
    legacy_mask = (tickets["source_system"] == "legacy_fd") & (tickets["resolved_dt"].notna())
    tickets["resolved_dt_norm"] = tickets["resolved_dt"]
    tickets.loc[legacy_mask, "resolved_dt_norm"] = tickets.loc[legacy_mask, "resolved_dt"] + pd.Timedelta(hours=5, minutes=30)

    # 3. Handle time (in hours) only for completed attendance (resolved or closed)
    # Tickets open or pending remain NaN
    completed_mask = tickets["status"].isin(["resolved", "closed"])
    tickets["handle_time_hrs"] = np.nan
    tickets.loc[completed_mask, "handle_time_hrs"] = (
        tickets.loc[completed_mask, "resolved_dt_norm"] - tickets.loc[completed_mask, "first_resp_dt"]
    ).dt.total_seconds() / 3600.0

    # 4. First-response time (in minutes) and SLA breach evaluation
    sla_targets = {"chat": 15, "voice": 120, "social": 240, "email": 480}
    tickets["resp_time_mins"] = (tickets["first_resp_dt"] - tickets["created_dt"]).dt.total_seconds() / 60.0
    tickets["sla_target_mins"] = tickets["channel"].map(sla_targets)
    tickets["is_breached"] = tickets["resp_time_mins"] > tickets["sla_target_mins"]
    tickets["sla_credit_inr"] = tickets["is_breached"].astype(int) * 350

    # 5. Completed attendance CSAT mask
    tickets["completed_csat"] = np.nan
    tickets.loc[completed_mask & tickets["csat_score"].notna(), "completed_csat"] = tickets.loc[completed_mask & tickets["csat_score"].notna(), "csat_score"]

    # 6. Channel contact costs
    ch_costs = {"chat": 210, "email": 260, "voice": 520, "social": 240}
    tickets["contact_cost_inr"] = tickets["channel"].map(ch_costs)

    # 7. Peer group assignment for agents
    kavya_four = ["A3004", "A3005", "A3006", "A3007"]
    def assign_peer_group(row):
        if row["tier"] == 2:
            return "Tier 2 (Escalations & Warranty)"
        elif row["agent_id"] in kavya_four:
            return "Hardware Triage Rota"
        else:
            return f"Frontline - {row['team']}"

    agents["peer_group"] = agents.apply(assign_peer_group, axis=1)

    # 8. Deterministic order join with fallback
    # Direct order_id match
    orders_lookup = orders.set_index("order_id")
    tickets["lot_code"] = tickets["order_id"].map(orders_lookup["lot_code"])
    tickets["order_channel"] = tickets["order_id"].map(orders_lookup["channel"])
    tickets["order_value_inr"] = tickets["order_id"].map(orders_lookup["order_value_inr"])
    tickets["order_date"] = tickets["order_id"].map(orders_lookup["order_date"])

    # Fallback for missing order_id using (customer_id + product_sku)
    missing_orders = tickets[tickets["order_id"].isna()].copy()
    if len(missing_orders) > 0:
        orders_sorted = orders.copy()
        orders_sorted["order_dt"] = pd.to_datetime(orders_sorted["order_date"])
        # Map grouped orders for tie breaking
        grouped_orders = orders_sorted.groupby(["customer_id", "sku"])
        
        fallback_lot = {}
        fallback_chan = {}
        fallback_val = {}
        fallback_date = {}

        for idx, row in missing_orders.iterrows():
            key = (row["customer_id"], row["product_sku"])
            if key in grouped_orders.groups:
                matched_orders = grouped_orders.get_group(key)
                # Find prior order closest to created_at
                c_dt = row["created_dt"]
                priors = matched_orders[matched_orders["order_dt"] <= c_dt]
                if len(priors) > 0:
                    chosen = priors.sort_values("order_dt", ascending=False).iloc[0]
                else:
                    chosen = matched_orders.sort_values("order_dt", ascending=True).iloc[0]
                
                fallback_lot[idx] = chosen["lot_code"]
                fallback_chan[idx] = chosen["channel"]
                fallback_val[idx] = chosen["order_value_inr"]
                fallback_date[idx] = chosen["order_date"]

        for idx, lot in fallback_lot.items():
            tickets.at[idx, "lot_code"] = lot
            tickets.at[idx, "order_channel"] = fallback_chan[idx]
            tickets.at[idx, "order_value_inr"] = fallback_val[idx]
            tickets.at[idx, "order_date"] = fallback_date[idx]

    # 9. Product cost join
    prod_lookup = products.set_index("sku")
    tickets["unit_cost_inr"] = tickets["product_sku"].map(prod_lookup["unit_cost_inr"])
    tickets["retail_price_inr"] = tickets["product_sku"].map(prod_lookup["retail_price_inr"])
    tickets["product_name"] = tickets["product_sku"].map(prod_lookup["product_name"])
    tickets["product_family"] = tickets["product_sku"].map(prod_lookup["family"])
    
    # Policy replacement cost: unit_cost + 340 logistics
    tickets["policy_repl_cost"] = (tickets["replacement_issued"] == "Y").astype(int) * (tickets["unit_cost_inr"] + 340)

    # 10. Agent join (strictly on agent_id)
    agent_lookup = agents.set_index("agent_id")
    tickets["agent_name"] = tickets["agent_id"].map(agent_lookup["name"])
    tickets["agent_site"] = tickets["agent_id"].map(agent_lookup["site"])
    tickets["agent_team"] = tickets["agent_id"].map(agent_lookup["team"])
    tickets["agent_shift"] = tickets["agent_id"].map(agent_lookup["shift"])
    tickets["agent_tier"] = tickets["agent_id"].map(agent_lookup["tier"])
    tickets["agent_peer_group"] = tickets["agent_id"].map(agent_lookup["peer_group"])

    return {
        "tickets": tickets,
        "agents": agents,
        "customers": customers,
        "orders": orders,
        "products": products
    }

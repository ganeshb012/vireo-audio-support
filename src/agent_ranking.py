"""
Agent Performance & Peer-Normalized Ranking Module.
Computes peer-normalized Z-scores and composite rankings for training review candidate identification.
"""

import pandas as pd
import numpy as np

def compute_agent_scorecards(tickets: pd.DataFrame, agents: pd.DataFrame) -> pd.DataFrame:
    """
    Computes comprehensive performance scorecards for all 44 agents.
    Strictly joins on agent_id.
    """
    # Join tickets to agents
    t_a = tickets.merge(agents, on="agent_id", how="left")

    # Aggregate by agent_id
    metrics = t_a.groupby("agent_id").agg(
        total_assigned=("ticket_id", "count"),
        attendance_count=("status", lambda s: s.isin(["resolved", "closed"]).sum()),
        csat_responses=("completed_csat", "count"),
        avg_csat=("completed_csat", "mean"),
        avg_handle_time_hrs=("handle_time_hrs", "mean"),
        median_handle_time_hrs=("handle_time_hrs", "median"),
        sla_breaches=("is_breached", "sum"),
        sla_breach_rate=("is_breached", "mean"),
        replacements_issued=("replacement_issued", lambda r: (r == "Y").sum())
    ).reset_index()

    # Merge back roster information
    df = agents.merge(metrics, on="agent_id", how="left")

    # Peer normalization within operational peer groups
    def z_calc(s):
        if len(s) <= 1 or s.std() == 0 or np.isnan(s.std()):
            return s * 0.0
        return (s - s.mean()) / s.std()

    df["peer_csat_mean"] = df.groupby("peer_group")["avg_csat"].transform("mean")
    df["peer_csat_std"] = df.groupby("peer_group")["avg_csat"].transform("std")
    df["z_csat"] = df.groupby("peer_group")["avg_csat"].transform(z_calc)

    df["peer_ht_mean"] = df.groupby("peer_group")["avg_handle_time_hrs"].transform("mean")
    df["peer_ht_std"] = df.groupby("peer_group")["avg_handle_time_hrs"].transform("std")
    df["z_ht"] = df.groupby("peer_group")["avg_handle_time_hrs"].transform(z_calc)

    # Composite Score: 70% CSAT Z-Score - 30% Handle Time Z-Score
    # Higher is better; lower indicates candidate for training review
    df["composite_score"] = 0.70 * df["z_csat"] - 0.30 * df["z_ht"]

    # Rank ascending: lowest composite score = rank 1 (review candidate)
    df["composite_rank"] = df["composite_score"].rank(ascending=True, method="min").astype(int)
    # Raw CSAT rank for comparison
    df["raw_csat_rank"] = df["avg_csat"].rank(ascending=True, method="min").astype(int)

    return df

def generate_review_reasons(df: pd.DataFrame) -> pd.DataFrame:
    """Generates human-readable, diagnostic coaching review reasons for flagged agents."""
    reasons = []
    for _, row in df.iterrows():
        z_c = row["z_csat"]
        z_h = row["z_ht"]
        team = row["team"]
        
        flags = []
        if z_c <= -1.0:
            flags.append(f"CSAT is {abs(z_c):.1f}σ below {team} peer benchmark")
        elif z_c < -0.5:
            flags.append(f"CSAT lags {team} peer average ({row['avg_csat']:.2f} vs {row['peer_csat_mean']:.2f})")
        
        if z_h >= 1.0:
            flags.append(f"Handle time is {z_h:.1f}σ slower than {team} peer benchmark")
        elif z_h > 0.3:
            flags.append(f"Turnaround time slower than departmental peers ({row['avg_handle_time_hrs']:.1f}h vs {row['peer_ht_mean']:.1f}h)")
        
        if not flags:
            flags.append("Departmental composite score in lower peer quartile")
            
        reasons.append(" • ".join(flags))
        
    df["review_reason"] = reasons
    return df

def get_training_review_list(scorecards_df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Returns the top N training review candidates sorted by composite score ascending."""
    df_with_reasons = generate_review_reasons(scorecards_df.copy())
    review_list = df_with_reasons.sort_values("composite_rank", ascending=True).head(n).copy()
    
    # Assign explicit 1-10 display rank
    review_list["Rank"] = range(1, len(review_list) + 1)
    
    display_cols = [
        "Rank", "agent_id", "name", "team", "peer_group", "tier",
        "attendance_count", "csat_responses", "avg_csat", "z_csat",
        "avg_handle_time_hrs", "z_ht", "composite_score", "review_reason"
    ]
    return review_list[display_cols]

def get_raw_csat_bottom_list(scorecards_df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Returns the raw unadjusted bottom N agents by CSAT for queue-bias comparison."""
    df = scorecards_df.sort_values("avg_csat", ascending=True).head(n).copy()
    df["Raw_Rank"] = range(1, len(df) + 1)
    display_cols = [
        "Raw_Rank", "agent_id", "name", "team", "peer_group", "tier",
        "attendance_count", "csat_responses", "avg_csat", "avg_handle_time_hrs"
    ]
    return df[display_cols]

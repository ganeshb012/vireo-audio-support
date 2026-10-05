"""
Vireo Audio — Support Desk Analytics & Operational Assessment Dashboard
Built for executive visibility, coaching allocation, and policy compliance auditing.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from src.data_loader import load_raw_data, normalize_and_enrich_data
from src.metrics import compute_executive_metrics, compute_sla_breakdown, compute_sla_opportunity
from src.agent_ranking import compute_agent_scorecards, get_training_review_list, get_raw_csat_bottom_list
from src.policy_checks import audit_dual_remedy_orders, audit_goodwill_cap, audit_unauthorized_replacements
from src.fcr import compute_fcr_proxy_analysis
from src.data_quality import audit_data_quality

# Page Config
st.set_page_config(
    page_title="Vireo Audio — Support Desk Analytics",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header { font-size: 26px; font-weight: 700; color: #1E293B; margin-bottom: 2px; }
    .sub-header { font-size: 14px; color: #64748B; margin-bottom: 20px; }
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; }
    .stMetric { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px; }
    .notice-box { background-color: #EFF6FF; border-left: 4px solid #3B82F6; padding: 12px; border-radius: 4px; margin-bottom: 16px; font-size: 14px; }
    .warning-box { background-color: #FFFBEB; border-left: 4px solid #F59E0B; padding: 12px; border-radius: 4px; margin-bottom: 16px; font-size: 14px; }
    .alert-box { background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 12px; border-radius: 4px; margin-bottom: 16px; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_prepare():
    raw = load_raw_data(".")
    normalized = normalize_and_enrich_data(raw)
    return normalized

data = load_and_prepare()
all_tickets = data["tickets"]
all_agents = data["agents"]
all_products = data["products"]
all_orders = data["orders"]

# ==============================================================================
# SIDEBAR FILTERS
# ==============================================================================
st.sidebar.image("https://img.icons8.com/color/96/headphones.png", width=64)
st.sidebar.title("Vireo Analytics Filters")

# Date range filter
min_date = all_tickets["created_dt"].min().date()
max_date = all_tickets["created_dt"].max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

if isinstance(date_range, list) and len(date_range) == 2:
    start_d, end_d = date_range
else:
    start_d, end_d = min_date, max_date

# Filter multiselects
channels = st.sidebar.multiselect("Channel", sorted(all_tickets["channel"].unique()), default=[])
teams = st.sidebar.multiselect("Assigned Team", sorted(all_tickets["assigned_team"].unique()), default=[])
peer_groups = st.sidebar.multiselect("Agent Peer Group", sorted(all_agents["peer_group"].unique()), default=[])
statuses = st.sidebar.multiselect("Ticket Status", sorted(all_tickets["status"].unique()), default=[])
products_filter = st.sidebar.multiselect("Product SKU", sorted(all_products["sku"].unique()), default=[])

# Apply filters to tickets
filtered_tickets = all_tickets.copy()
filtered_tickets = filtered_tickets[(filtered_tickets["created_dt"].dt.date >= start_d) & (filtered_tickets["created_dt"].dt.date <= end_d)]

if channels:
    filtered_tickets = filtered_tickets[filtered_tickets["channel"].isin(channels)]
if teams:
    filtered_tickets = filtered_tickets[filtered_tickets["assigned_team"].isin(teams)]
if peer_groups:
    filtered_tickets = filtered_tickets[filtered_tickets["agent_peer_group"].isin(peer_groups)]
if statuses:
    filtered_tickets = filtered_tickets[filtered_tickets["status"].isin(statuses)]
if products_filter:
    filtered_tickets = filtered_tickets[filtered_tickets["product_sku"].isin(products_filter)]

# Header
st.markdown("<div class='main-header'>🎧 Vireo Audio — Customer Support Desk Analytics</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-header'>Operational Performance, Quality Control & Policy Audit Dashboard • Analyzed Period: {start_d.strftime('%d %b %Y')} to {end_d.strftime('%d %b %Y')} ({len(filtered_tickets):,} Tickets)</div>", unsafe_allow_html=True)

# Tabs
tabs = st.tabs([
    "📊 Executive Summary",
    "👥 Training Review List",
    "⏱️ SLA Performance",
    "⚠️ Policy Leakage",
    "📦 Product & Batch Signals",
    "🔄 FCR & Repeat Contacts",
    "🛠️ Data Reliability"
])

# ==============================================================================
# TAB 1: EXECUTIVE SUMMARY
# ==============================================================================
with tabs[0]:
    exec_metrics = compute_executive_metrics(filtered_tickets)
    dual_audit = audit_dual_remedy_orders(filtered_tickets)
    gw_audit = audit_goodwill_cap(filtered_tickets)
    
    # KPI Row 1
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Tickets", f"{exec_metrics['total_tickets']:,}")
    col2.metric("Overall CSAT", f"{exec_metrics['overall_csat']:.2f} / 5.0", help="Excludes blank surveys & open/pending tickets per Policy §8")
    col3.metric("Avg Handle Time", f"{exec_metrics['avg_handle_time_hrs']:.1f} hrs", help="Measured from first response to normalized resolution")
    col4.metric("SLA Breach Rate", f"{exec_metrics['sla_breach_rate']:.2f}%", f"{exec_metrics['total_breaches']:,} breaches", delta_color="inverse")
    col5.metric("SLA Credit Liability", f"₹{exec_metrics['sla_credit_exposure']:,}", help="₹350 auto store credit per breach (Policy §3)")
    
    # KPI Row 2
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Dual-Remedy Orders", f"{dual_audit['count']:,}", f"₹{dual_audit['total_repl_spend']:,.0f} repl cost", delta_color="inverse", help="Orders receiving both refund & replacement (Policy §5 breach)")
    c2.metric("Goodwill Cap Overages", f"{gw_audit['violations_count']:,}", f"₹{gw_audit['total_overage_inr']:,.0f} overage", delta_color="inverse", help="Refunds using GW-OTHER > ₹500 cap")
    c3.metric("Replacement Rate", f"{exec_metrics['replacement_rate']:.2f}%", f"{exec_metrics['total_replacements']:,} units")
    c4.metric("Policy Replacement Spend", f"₹{exec_metrics['total_policy_repl_cost']:,}", help="Calculated as Unit Cost + ₹340 Logistics per Policy §5")
    c5.metric("Pulse 2 Repl. Rate", f"{exec_metrics['pl2_repl_rate']:.1f}%", f"{exec_metrics['pl2_replacements']:,} / {exec_metrics['pl2_tickets']:,} tkts", delta_color="inverse")

    st.markdown("---")
    
    # Visual Highlights
    r1_col1, r1_col2 = st.columns([1, 1])
    with r1_col1:
        st.subheader("Ticket Volume by Channel & First-Response SLA Compliance")
        sla_df = compute_sla_breakdown(filtered_tickets)
        fig_sla = px.bar(
            sla_df,
            x="Channel",
            y=["Total Tickets", "Breach Count"],
            barmode="group",
            title="Total Tickets vs. SLA Breaches by Channel",
            color_discrete_sequence=["#3B82F6", "#EF4444"]
        )
        st.plotly_chart(fig_sla, use_container_width=True)
        
    with r1_col2:
        st.subheader("Replacement Cost Breakdown by Product Family")
        family_df = filtered_tickets[filtered_tickets["replacement_issued"] == "Y"].groupby("product_family").agg(
            replacements=("ticket_id", "count"),
            spend=("policy_repl_cost", "sum")
        ).reset_index()
        fig_fam = px.pie(
            family_df,
            names="product_family",
            values="spend",
            title="Replacement Expenditure by Product Category (Policy Cost)",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(fig_fam, use_container_width=True)

    # Opportunity Banner
    st.markdown("""
    <div class='notice-box'>
        <b>🎯 Recommended Executive Goal: Dual-Track Operational Leakage Elimination & SLA Breach Reduction</b><br>
        • Modeled potential cash savings of <b>₹564,132 over 18 months (~₹376,088/year)</b> through SLA breach containment, zero dual-remedy leakage, and goodwill cap enforcement.<br>
        • Fully funds the ₹4 Lakh Q3 training budget while directing IT to implement critical CRM validation rules.
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# TAB 2: AGENT PERFORMANCE / TRAINING REVIEW LIST
# ==============================================================================
with tabs[1]:
    st.subheader("👥 Agent Performance & Training Review Candidates")
    
    st.markdown("""
    <div class='notice-box'>
        <b>📋 Coaching Review Protocol:</b><br>
        Candidates are identified relative to functional peer groups; this is a coaching-review signal, not proof that these agents are objectively the lowest performers.<br>
        • <b>Strict Metric Standards:</b> CSAT includes only completed attendances (resolved/closed); blank surveys and open/pending scores are strictly excluded.<br>
        • <b>Queue Normalization:</b> Agents are evaluated via composite score: <code>0.70 * Z_CSAT_peer - 0.30 * Z_HT_peer</code>.<br>
        • <b>Tier 2 Protection:</b> Tier 2 Escalations agents are measured against fellow warranty specialists, not against Tier 1 speed/volume.
    </div>
    """, unsafe_allow_html=True)
    
    scorecards = compute_agent_scorecards(filtered_tickets, all_agents)
    review_list = get_training_review_list(scorecards, n=10)
    raw_bottom_list = get_raw_csat_bottom_list(scorecards, n=10)
    
    st.markdown("### Top 10 Training Review Candidates (Peer-Normalized Composite Score)")
    st.dataframe(
        review_list.rename(columns={
            "agent_id": "Agent ID",
            "name": "Agent Name",
            "team": "Team",
            "peer_group": "Operating Peer Group",
            "tier": "Tier",
            "attendance_count": "Completed Tickets",
            "csat_responses": "CSAT Responses",
            "avg_csat": "CSAT",
            "z_csat": "Peer CSAT Z-Score",
            "avg_handle_time_hrs": "Handle Time (hrs)",
            "z_ht": "Peer HT Z-Score",
            "composite_score": "Composite Score",
            "review_reason": "Training Review Reason"
        }).style.format({
            "CSAT": "{:.2f}",
            "Peer CSAT Z-Score": "{:+.2f}",
            "Handle Time (hrs)": "{:.1f}",
            "Peer HT Z-Score": "{:+.2f}",
            "Composite Score": "{:.3f}"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    with st.expander("🔍 Queue-Bias Analysis: Compare Peer-Normalized Review List vs. Raw Unadjusted CSAT"):
        st.markdown("""
        **Why 8 out of 10 names change:**
        In the raw CSAT table below, 100% of the agents are from Tier 2 Escalations (6 agents) and the Hardware Triage Rota (4 agents).
        As Neha Kulkarni warned, these agents handle hardware escalations and defective Pulse 2 batches by design.
        Comparing them directly against frontline chat agents answering simple account queries unfairly penalizes queue assignment.
        Peer-normalization correctly surfaces frontline agents whose performance lags their direct departmental peers.
        """)
        st.dataframe(
            raw_bottom_list.rename(columns={
                "Raw_Rank": "Raw Rank",
                "agent_id": "Agent ID",
                "name": "Agent Name",
                "team": "Team",
                "peer_group": "Peer Group",
                "tier": "Tier",
                "attendance_count": "Tickets",
                "csat_responses": "CSAT Count",
                "avg_csat": "Raw CSAT",
                "avg_handle_time_hrs": "Handle Time (hrs)"
            }).style.format({
                "Raw CSAT": "{:.2f}",
                "Handle Time (hrs)": "{:.1f}"
            }),
            use_container_width=True,
            hide_index=True
        )

# ==============================================================================
# TAB 3: SLA PERFORMANCE
# ==============================================================================
with tabs[2]:
    st.subheader("⏱️ First-Response SLA Compliance & Liability")
    
    sla_summary = compute_sla_breakdown(filtered_tickets)
    sla_opp = compute_sla_opportunity(len(filtered_tickets), int(filtered_tickets["is_breached"].sum()), target_rate=3.50)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Breach Rate", f"{sla_opp['current_breach_rate']:.2f}%", f"{sla_opp['current_breaches']:,} total breaches", delta_color="inverse")
    c2.metric("Target Breach Rate", f"{sla_opp['target_rate']:.2f}%", f"{sla_opp['target_breaches']:,} target breaches")
    c3.metric("Avoided Breaches Target", f"{sla_opp['avoided_breaches']:,} breaches", "Targeted potential improvement")
    c4.metric("Modeled Credit Savings", f"₹{sla_opp['potential_savings_inr']:,}", f"₹{sla_opp['annualized_savings_inr']:,}/yr run-rate")
    
    st.markdown("""
    <div class='warning-box'>
        <b>⚠️ Financial Disclosure:</b><br>
        The modeled ₹228,900 saving is a <b>TARGETED POTENTIAL SAVING</b> based on reducing the breach rate from 9.06% to 3.50% (saving 654 breaches × ₹350 store credit). It is not guaranteed realized cash until operational thresholds and intake queue controls are actively enforced.
    </div>
    """, unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns([1.2, 0.8])
    with col_t1:
        st.markdown("#### Channel SLA Thresholds & Breach Breakdown")
        st.dataframe(sla_summary, use_container_width=True, hide_index=True)
        
    with col_t2:
        st.markdown("#### SLA Breach Concentration")
        fig_br = px.pie(
            sla_summary,
            names="Channel",
            values="Breach Count",
            title="Distribution of SLA Breaches by Channel",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_br, use_container_width=True)

# ==============================================================================
# TAB 4: POLICY / OPERATIONAL LEAKAGE
# ==============================================================================
with tabs[3]:
    st.subheader("⚠️ Policy Compliance Audit & Financial Leakage")
    
    dual_audit = audit_dual_remedy_orders(filtered_tickets)
    gw_audit = audit_goodwill_cap(filtered_tickets)
    unauth_audit = audit_unauthorized_replacements(filtered_tickets, all_agents)
    
    st.markdown("""
    <div class='alert-box'>
        <b>🛡️ Policy Exception & Leakage Summary:</b><br>
        Transactions flagged below are <b>policy exception / leakage review candidates</b>. They do not imply deliberate employee or customer fraud, but represent clear deviations from Support Policy v3.2 operating standards.
    </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns(3)
    col_l1.metric("Dual-Remedy Orders", f"{dual_audit['count']:,}", f"₹{dual_audit['total_repl_spend']:,.0f} repl loss", delta_color="inverse")
    col_l2.metric("Goodwill Cap Overages", f"{gw_audit['violations_count']:,}", f"₹{gw_audit['total_overage_inr']:,.0f} overage", delta_color="inverse")
    col_l3.metric("Tier 1 Replacements", f"{unauth_audit['tier1_count']:,}", f"₹{unauth_audit['tier1_spend']:,.0f} spend", delta_color="inverse")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 1. Dual Remedy Orders (Policy §5 Prohibition)")
        st.caption("Policy §5: 'In no case is a customer to receive both a refund and a replacement for the same order.'")
        st.dataframe(
            dual_audit["df"][["order_id", "customer_id", "product_sku", "ticket_count", "total_refund", "total_policy_repl_cost", "combined_spend"]].head(15).rename(columns={
                "order_id": "Order ID",
                "customer_id": "Customer ID",
                "product_sku": "SKU",
                "ticket_count": "Tickets",
                "total_refund": "Refund (₹)",
                "total_policy_repl_cost": "Repl Cost (₹)",
                "combined_spend": "Combined Spend (₹)"
            }),
            use_container_width=True,
            hide_index=True
        )
        
    with col_b:
        st.markdown("#### 2. Goodwill Credits Exceeding ₹500 Cap (Policy §5)")
        st.caption("Policy §5: 'Goodwill credits are capped at Rs 500 per ticket and require Team Lead approval.'")
        st.dataframe(
            gw_audit["df"][["ticket_id", "customer_id", "refund_amount_inr", "overage_inr", "agent_notes"]].head(15).rename(columns={
                "ticket_id": "Ticket ID",
                "customer_id": "Customer ID",
                "refund_amount_inr": "Issued Refund (₹)",
                "overage_inr": "Overage above ₹500 (₹)",
                "agent_notes": "Agent Notes"
            }),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("#### 3. Unauthorized Frontline Replacements by Team (Policy §6)")
    st.caption("Policy §6: 'Tier 2 work is certified: only Tier 2 agents may approve warranty replacements.'")
    st.dataframe(
        unauth_audit["team_breakdown"].rename(columns={
            "team": "Frontline Team",
            "replacement_count": "Replacements Issued by Tier 1",
            "total_policy_cost": "Policy Replacement Spend (₹)"
        }),
        use_container_width=True,
        hide_index=True
    )

# ==============================================================================
# TAB 5: PRODUCT / REPLACEMENT SIGNAL
# ==============================================================================
with tabs[4]:
    st.subheader("📦 Product Hardware & Replacement Signals")
    
    st.markdown("""
    <div class='notice-box'>
        <b>🔬 Evidentiary Standard:</b><br>
        The observed data demonstrates <b>empirical evidence consistent with a batch-specific hardware issue</b> concentrated in Q4 2025 production lots of Pulse 2 Earbuds.<br>
        <b>Scientific Limitation:</b> The helpdesk and sales dataset alone cannot certify the physical root cause (e.g., BMS component defect vs. battery cell degradation vs. packaging). Certified physical root-cause identification requires hardware laboratory teardown reports from engineering.
    </div>
    """, unsafe_allow_html=True)
    
    # Monthly trend chart
    monthly_repl = filtered_tickets.copy()
    monthly_repl["month_year"] = monthly_repl["created_dt"].dt.to_period("M").astype(str)
    
    m_agg = monthly_repl.groupby("month_year").agg(
        total_tickets=("ticket_id", "count"),
        replacements=("replacement_issued", lambda x: (x == "Y").sum()),
        repl_cost=("policy_repl_cost", "sum")
    ).reset_index()
    m_agg["repl_rate"] = (m_agg["replacements"] / m_agg["total_tickets"]) * 100
    
    fig_trend = px.line(
        m_agg,
        x="month_year",
        y="repl_rate",
        markers=True,
        title="Monthly Overall Replacement Rate (%) Across Support Desk",
        labels={"month_year": "Month", "repl_rate": "Replacement Rate (%)"},
        color_discrete_sequence=["#EF4444"]
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    st.markdown("#### Pulse 2 (`VA-EB-PL2`) Lot Code Failure Concentration")
    pl2_tickets = filtered_tickets[filtered_tickets["product_sku"] == "VA-EB-PL2"].copy()
    
    # Lot code summary
    lot_agg = pl2_tickets.groupby("lot_code").agg(
        tickets=("ticket_id", "count"),
        replacements=("replacement_issued", lambda x: (x == "Y").sum()),
        policy_cost=("policy_repl_cost", "sum")
    ).reset_index()
    lot_agg["repl_rate"] = (lot_agg["replacements"] / lot_agg["tickets"]) * 100
    
    # Highlight Q4 lots
    lot_agg["is_q4"] = lot_agg["lot_code"].str.contains("PL2-2510|PL2-2511|PL2-2512", na=False)
    lot_agg["Lot Classification"] = lot_agg["is_q4"].map({True: "Q4 2025 Anomalous Batches (Oct-Dec)", False: "Standard Production Batches"})
    
    fig_lot = px.scatter(
        lot_agg.dropna(subset=["lot_code"]),
        x="tickets",
        y="repl_rate",
        size="replacements",
        color="Lot Classification",
        hover_name="lot_code",
        title="Pulse 2 Lot Code Performance: Tickets vs. Replacement Rate (%)",
        labels={"tickets": "Total Tickets Logged", "repl_rate": "Replacement Rate (%)"},
        color_discrete_map={"Q4 2025 Anomalous Batches (Oct-Dec)": "#EF4444", "Standard Production Batches": "#3B82F6"}
    )
    st.plotly_chart(fig_lot, use_container_width=True)
    
    st.dataframe(
        lot_agg.sort_values("replacements", ascending=False).head(15).rename(columns={
            "lot_code": "Lot Code",
            "tickets": "Tickets",
            "replacements": "Replacements",
            "repl_rate": "Replacement Rate (%)",
            "policy_cost": "Policy Spend (₹)"
        }).style.format({"Replacement Rate (%)": "{:.1f}%", "Policy Spend (₹)": "₹{:,.0f}"}),
        use_container_width=True,
        hide_index=True
    )

# ==============================================================================
# TAB 6: FCR & REPEAT CONTACTS
# ==============================================================================
with tabs[5]:
    st.subheader("🔄 First-Contact Resolution (FCR) & Repeat Contact Proxy")
    
    st.markdown("""
    <div class='notice-box'>
        <b>📌 Operational Proxy Definition:</b><br>
        Support Policy §10 defines FCR as no customer return contact within 30 days <i>'about the same issue'</i>.<br>
        Because helpdesk exports lack standardized sub-category fault codes, this calculation tracks <b>same customer + same product SKU within 30 days of resolution</b> as a transparent <b>Operational FCR Proxy</b>.
    </div>
    """, unsafe_allow_html=True)
    
    fcr_data = compute_fcr_proxy_analysis(filtered_tickets)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Operational FCR Rate", f"{fcr_data['fcr_proxy_rate_pct']:.2f}%", help="Calculated via operational proxy: same customer + SKU within 30 days")
    c2.metric("Repeat Contacts (30d)", f"{fcr_data['repeat_contacts_count']:,}", "Operational proxy count")
    c3.metric("Observed Repeat Spend", f"₹{fcr_data['repeat_contacts_cost_inr']:,.0f}", f"Avg ₹{fcr_data['avg_repeat_contact_cost_inr']:.0f}/contact", help="Total historical channel handling cost of repeat contacts")
    c4.metric("Modeled Avoidable Savings", f"₹{fcr_data['potential_savings_inr']:,.0f}", f"Target: avoid {fcr_data['avoided_repeats_target']} contacts (15% cut)", help="Modeled potential savings if 15% repeat contact reduction is achieved")

# ==============================================================================
# TAB 7: DATA RELIABILITY & QUALITY AUDIT
# ==============================================================================
with tabs[6]:
    st.subheader("🛠️ Data Reliability, Telephony Audit & Integrations")
    
    dq = audit_data_quality(filtered_tickets, all_agents)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Legacy UTC Offset Errors", f"{dq['raw_negative_handle_times']:,}", "Normalized to 0 via +05:30 fix")
    c2.metric("Missing Order IDs", f"{dq['missing_order_count']:,}", f"{dq['missing_order_pct']}% (resolved via fallback)")
    c3.metric("Junk IVR Transcripts", f"{dq['junk_ivr_count']:,}", "Quarantined phone system errors")
    c4.metric("Premature CSAT Scores", f"{dq['premature_csat_count']:,}", "Excluded from completed attendance")
    
    st.markdown("---")
    
    st.markdown("#### 1. Critical Agent Identity Warning: Duplicate Display Names")
    st.markdown("""
    Two distinct agents share the display name **'Kavya Pandey'**:
    - **`A3006`:** Site: Indore | Team: Chat Frontline | Shift: Morning | Tier: 1
    - **`A3029`:** Site: Bengaluru | Team: Voice Frontline | Shift: Day | Tier: 1
    
    **Architectural Guarantee:** All database pipelines and joins in this tool strictly join on `agent_id`. Joining on agent name is strictly blocked to prevent corrupting agent scorecards.
    """)
    
    st.markdown("#### 2. Telephony Ingestion Failures (Junk IVR Transcripts)")
    st.caption("These ~40 tickets represent telephone ingestion failures (line drops, audio static), not agent misconduct.")
    st.dataframe(dq["junk_ivr_df"].head(15), use_container_width=True, hide_index=True)

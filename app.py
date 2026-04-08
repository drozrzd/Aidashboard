"""
AI E-Commerce Decision Dashboard — Ombraz Glasses Demo
Stack: Streamlit + Pandas + Plotly + Supabase + Groq (Llama 3.3 70B)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ── Page config must be first Streamlit call ─────────────────────────────────
st.set_page_config(
    page_title="AI Decision Dashboard | Ombraz",
    page_icon="🕶️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS: Ombraz dark/earthy aesthetic ──────────────────────────────────
st.markdown("""
<style>
    /* Core backgrounds */
    .stApp { background-color: #1A1A18; color: #F0EDE4; }
    [data-testid="stSidebar"] {
        background-color: #141412;
        border-right: 1px solid #2E2E2A;
    }
    /* Metric tiles */
    [data-testid="metric-container"] {
        background-color: #232320;
        border: 1px solid #2E2E2A;
        border-radius: 8px;
        padding: 18px 16px;
    }
    [data-testid="stMetricValue"] { color: #F0EDE4; font-weight: 700; }
    [data-testid="stMetricDelta"] { font-size: 0.78rem; }
    /* Section headers */
    .section-header {
        color: #C9A84C;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        border-bottom: 1px solid #2E2E2A;
        padding-bottom: 10px;
        margin-bottom: 16px;
        margin-top: 8px;
    }
    /* Strategy summary cards */
    .strategy-card {
        text-align: center;
        background: #232320;
        border-radius: 8px;
        padding: 14px 8px;
    }
    /* Offer timing callout */
    .offer-callout {
        background: #1A2A1A;
        border: 1px solid #4CAF79;
        border-radius: 6px;
        padding: 12px 16px;
        margin-top: 10px;
        font-size: 0.9rem;
    }
    /* Chat input area */
    [data-testid="stChatInput"] textarea {
        background-color: #232320;
        color: #F0EDE4;
        border-color: #3A3A36;
    }
    /* Sidebar brand block */
    .brand-block {
        text-align: center;
        padding: 20px 0 12px;
    }
    /* Dataframe */
    [data-testid="stDataFrame"] iframe { background: #232320; }
    /* General links */
    a { color: #C9A84C; }
    /* Divider */
    hr { border-color: #2E2E2A; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. SYNTHETIC DATA GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def generate_sku_data(seed: int = 42) -> pd.DataFrame:
    """
    Generate 50 realistic glasses SKUs.
    Data follows intentional patterns to exercise all three First Principles:
      - ~10 SKUs: low stock + high velocity  → Revenue Guard triggers
      - ~12 SKUs: high velocity + high margin → Push candidates
      - ~10 SKUs: low velocity + high margin  → Bundle candidates
      - ~10 SKUs: high velocity + low margin  → Monitor candidates
      - ~8 SKUs:  low velocity + low margin   → Discount candidates
    """
    rng = np.random.default_rng(seed)

    styles = [
        "Classic Aviator", "Sport Wraparound", "Round Lens", "Wayfarers",
        "Cat Eye", "Rectangular", "Photochromic", "Polarized Shield",
        "Slim Oval", "Bold Square", "Retro Browline", "Rimless",
        "Semi-Rimless", "Geometric", "Oversized",
    ]
    colors = [
        "Gold", "Silver", "Black", "Tortoise", "Rose Gold",
        "Navy", "Olive", "Clear", "Brown", "Gunmetal",
    ]
    categories = ["Sun", "Optical", "Blue Light"]
    month = datetime.now().month

    rows = []
    for i in range(50):
        cat = categories[i % 3]
        style = styles[i % len(styles)]
        color = colors[i % len(colors)]
        name = f"{style} - {color}"

        # Price tier
        tier = ["budget", "mid", "premium"][i % 3]
        if tier == "budget":
            cost = round(float(rng.uniform(18, 35)), 2)
            price = round(cost * float(rng.uniform(2.0, 2.8)), 2)
        elif tier == "mid":
            cost = round(float(rng.uniform(40, 80)), 2)
            price = round(cost * float(rng.uniform(2.2, 3.0)), 2)
        else:
            cost = round(float(rng.uniform(90, 180)), 2)
            price = round(cost * float(rng.uniform(2.5, 4.0)), 2)

        margin = round((price - cost) / price, 3)

        # Intentional inventory patterns
        if i < 10:
            stock = int(rng.integers(5, 46))
            velocity = round(float(rng.uniform(4.5, 9.0)), 2)
        elif i < 22:
            stock = int(rng.integers(80, 301))
            velocity = round(float(rng.uniform(3.5, 7.0)), 2)
            margin = round(float(rng.uniform(0.45, 0.65)), 3)
        elif i < 32:
            stock = int(rng.integers(150, 501))
            velocity = round(float(rng.uniform(0.3, 1.2)), 2)
            margin = round(float(rng.uniform(0.48, 0.70)), 3)
        elif i < 42:
            stock = int(rng.integers(60, 201))
            velocity = round(float(rng.uniform(3.0, 6.5)), 2)
            margin = round(float(rng.uniform(0.22, 0.38)), 3)
        else:
            stock = int(rng.integers(100, 401))
            velocity = round(float(rng.uniform(0.1, 0.8)), 2)
            margin = round(float(rng.uniform(0.15, 0.30)), 3)

        # Seasonality score by category and month
        if cat == "Sun":
            base = 0.5 + 0.4 * np.sin((month - 3) * np.pi / 6)
        elif cat == "Blue Light":
            base = 0.65 + 0.1 * np.sin((month - 9) * np.pi / 6)
        else:
            base = 0.55 + 0.2 * np.sin((month - 1) * np.pi / 6)

        seasonality = round(float(np.clip(base + rng.uniform(-0.1, 0.1), 0.1, 1.0)), 3)

        # Recalculate margin-consistent cost/price if margin was overridden
        cost = round(price * (1 - margin), 2)

        rows.append({
            "sku_id": f"GL-{str(i + 1).zfill(3)}",
            "product_name": name,
            "category": cat,
            "current_stock": stock,
            "daily_sales_velocity": velocity,
            "unit_cost": cost,
            "selling_price": price,
            "profit_margin": margin,
            "seasonality_score": seasonality,
        })

    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SUPABASE — LOAD / SEED
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def _supabase_client():
    """Return a cached Supabase client, or None if credentials are missing."""
    try:
        from supabase import create_client  # type: ignore
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
        return create_client(url, key)
    except Exception:
        return None


def _seed_supabase(client, df: pd.DataFrame) -> None:
    records = df.to_dict(orient="records")
    try:
        client.table("sku_inventory").insert(records).execute()
    except Exception as e:
        st.warning(f"Supabase seed failed: {e}")


@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    """
    Fetch SKU data from Supabase.
    Falls back to in-memory synthetic data if DB is unreachable or empty.
    """
    client = _supabase_client()
    if client:
        try:
            resp = client.table("sku_inventory").select("*").execute()
            if resp.data:
                df = pd.DataFrame(resp.data)
                drop = [c for c in ("id", "created_at") if c in df.columns]
                return df.drop(columns=drop)
            # Empty table — seed it
            df = generate_sku_data()
            _seed_supabase(client, df)
            return df
        except Exception:
            pass  # Fall through to local fallback
    return generate_sku_data()


# ═══════════════════════════════════════════════════════════════════════════════
# 3. FIRST PRINCIPLES — CORE LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

def apply_revenue_guard(df: pd.DataFrame, lead_time: int = 7, safety_days: int = 7) -> pd.DataFrame:
    """
    Principle 1 — Revenue Guard.
    DTZ = Current Stock / Daily Sales Velocity.
    Critical if DTZ < lead_time + safety_days (default: 14 days).
    Lost Revenue Risk = max(threshold - DTZ, 0) * velocity * price.
    """
    df = df.copy()
    threshold = lead_time + safety_days
    safe_vel = df["daily_sales_velocity"].replace(0, 0.01)
    df["dtz"] = (df["current_stock"] / safe_vel).round(1)
    df["is_critical"] = df["dtz"] < threshold
    df["lost_revenue_risk"] = (
        (threshold - df["dtz"]).clip(lower=0) * df["daily_sales_velocity"] * df["selling_price"]
    ).round(2)
    return df


def apply_sku_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Principle 2 — Capital Efficiency Matrix.
    Splits on median velocity and median margin to assign one of four strategies:
    Push | Bundle | Monitor | Discount.
    """
    df = df.copy()
    vel_mid = df["daily_sales_velocity"].median()
    mar_mid = df["profit_margin"].median()

    def _cat(row):
        hv = row["daily_sales_velocity"] >= vel_mid
        hm = row["profit_margin"] >= mar_mid
        if hv and hm:
            return "Push"
        if not hv and hm:
            return "Bundle"
        if hv and not hm:
            return "Monitor"
        return "Discount"

    df["strategy"] = df.apply(_cat, axis=1)
    return df


def analyze_seasonality(df: pd.DataFrame) -> dict:
    """
    Principle 3 — Temporal Relevance.
    Builds a 12-month simulated historical vs. current velocity curve.
    Flags months where current trend > historical mean + 1 std dev.
    Recommends launching offers 7-14 days before those peaks.
    """
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    m = datetime.now().month - 1
    avg_vel = df["daily_sales_velocity"].mean()

    historical = [avg_vel * (0.7 + 0.5 * np.sin((i - 2) * np.pi / 6)) for i in range(12)]
    current = [historical[i] * (1.0 + 0.18 * np.sin((i - m) * np.pi / 3)) for i in range(12)]

    h_mean = np.mean(historical)
    h_std = np.std(historical)
    offer_windows = [months[i] for i in range(12) if current[i] > h_mean + h_std]

    return {
        "months": months,
        "historical": historical,
        "current": current,
        "offer_windows": offer_windows,
        "current_month": months[m],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. GROQ AI AGENT
# ═══════════════════════════════════════════════════════════════════════════════

def _build_context(df: pd.DataFrame) -> str:
    """
    Compress processed data into a compact context string for Groq.
    Deliberately lean to minimize token spend on every chat call.
    """
    critical = (
        df[df["is_critical"]]
        .sort_values("dtz")[["sku_id", "product_name", "dtz", "lost_revenue_risk"]]
        .head(8)
        .to_string(index=False)
    )
    push = (
        df[df["strategy"] == "Push"]
        .nlargest(5, "profit_margin")[["sku_id", "product_name", "daily_sales_velocity", "profit_margin"]]
        .to_string(index=False)
    )
    discount = (
        df[df["strategy"] == "Discount"]
        .nsmallest(5, "daily_sales_velocity")[["sku_id", "product_name", "daily_sales_velocity", "profit_margin"]]
        .to_string(index=False)
    )
    counts = df["strategy"].value_counts().to_dict()

    return f"""SNAPSHOT {datetime.now().strftime('%Y-%m-%d')} | {len(df)} SKUs
Critical (DTZ<14): {df['is_critical'].sum()} | Total risk: ${df['lost_revenue_risk'].sum():,.0f}
Strategy mix: Push={counts.get('Push',0)} Bundle={counts.get('Bundle',0)} Monitor={counts.get('Monitor',0)} Discount={counts.get('Discount',0)}

CRITICAL SKUs:
{critical}

TOP PUSH:
{push}

TOP DISCOUNT:
{discount}"""


def _mock_response(question: str, df: pd.DataFrame) -> str:
    """Rule-based fallback when Groq is unavailable."""
    q = question.lower()
    critical = df[df["is_critical"]]
    if any(w in q for w in ["stock", "run out", "reorder", "critical"]):
        top = critical.nsmallest(3, "dtz")
        names = "; ".join(f"{r.sku_id} — {r.dtz:.0f} days" for _, r in top.iterrows())
        return (f"{critical.shape[0]} SKUs need reorder now. "
                f"Most urgent: {names}. "
                f"Total revenue at risk: ${critical['lost_revenue_risk'].sum():,.0f}.")
    if any(w in q for w in ["discount", "slow", "liquidat"]):
        items = df[df["strategy"] == "Discount"].nsmallest(3, "daily_sales_velocity")
        names = ", ".join(items["product_name"].tolist())
        return f"Discount candidates: {names}. Low velocity and thin margins — liquidate to free capital."
    if any(w in q for w in ["push", "ad spend", "advertis", "feature"]):
        items = df[df["strategy"] == "Push"].nlargest(3, "profit_margin")
        names = ", ".join(items["product_name"].tolist())
        return f"Push these: {names}. Strong velocity with margins above {df['profit_margin'].median():.0%}."
    return (f"Tracking {len(df)} SKUs. {df['is_critical'].sum()} need immediate reorder. "
            f"{len(df[df['strategy']=='Push'])} are ready to push. "
            f"Ask me about stockouts, discounts, or ad spend priorities.")


def get_agent_response(history: list, df: pd.DataFrame) -> str:
    """Send conversation history + data context to Groq Llama 3.3 70B."""
    try:
        from groq import Groq  # type: ignore
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        system = (
            "You are a sharp, data-driven inventory analyst for Ombraz, a premium eyewear brand. "
            "Give direct, specific recommendations. Always reference SKU IDs and numbers. "
            "Never give generic advice. Be concise — max 3 sentences unless a list is needed.\n\n"
            f"CURRENT DATA:\n{_build_context(df)}"
        )
        messages = [{"role": "system", "content": system}] + history
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=400,
            temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception:
        last_user = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
        return _mock_response(last_user, df)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

STRATEGY_COLORS = {
    "Push": "#4CAF79",
    "Bundle": "#C9A84C",
    "Monitor": "#5B8ED6",
    "Discount": "#CC4444",
}


def render_sidebar(df: pd.DataFrame) -> None:
    with st.sidebar:
        st.markdown("""
        <div class="brand-block">
            <div style="font-size:1.5rem;font-weight:800;color:#C9A84C;letter-spacing:0.15em;">
                OMBRAZ
            </div>
            <div style="font-size:0.65rem;color:#666;letter-spacing:0.25em;
                        text-transform:uppercase;margin-top:2px;">
                AI Decision Agent
            </div>
        </div>
        <hr>
        """, unsafe_allow_html=True)

        # Seed opening message once per session
        if "messages" not in st.session_state:
            critical_n = int(df["is_critical"].sum())
            risk = df["lost_revenue_risk"].sum()
            st.session_state.messages = [{
                "role": "assistant",
                "content": (
                    f"Inventory loaded. {critical_n} SKUs need reorder now "
                    f"— ${risk:,.0f} in revenue at risk. "
                    "Ask me what to push, discount, or reorder."
                ),
            }]

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about inventory, strategy..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    reply = get_agent_response(
                        [m for m in st.session_state.messages],
                        df,
                    )
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})


def render_kpis(df: pd.DataFrame) -> None:
    monthly_rev = (df["selling_price"] * df["daily_sales_velocity"] * 30).sum()
    aov = df["selling_price"].mean()
    healthy_pct = (~df["is_critical"]).sum() / len(df) * 100
    risk = df["lost_revenue_risk"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Est. Monthly Revenue", f"${monthly_rev:,.0f}", "30-day projection")
    c2.metric("Avg Selling Price", f"${aov:,.2f}", f"{len(df)} SKUs")
    c3.metric("Stock Health", f"{healthy_pct:.1f}%",
              f"{int(df['is_critical'].sum())} critical", delta_color="inverse")
    c4.metric("Revenue at Risk", f"${risk:,.0f}",
              "without reorder action", delta_color="inverse")


def render_revenue_guard(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-header">Revenue Guard — Critical Reorder Alerts</div>',
                unsafe_allow_html=True)

    crit = (
        df[df["is_critical"]]
        .sort_values("dtz")[["sku_id", "product_name", "category",
                              "current_stock", "daily_sales_velocity",
                              "dtz", "lost_revenue_risk"]]
        .copy()
    )
    crit.columns = ["SKU", "Product", "Cat", "Stock", "Vel/Day", "DTZ", "Risk ($)"]

    if crit.empty:
        st.success("All SKUs healthy — no reorders required.")
        return

    def _dtz_style(val):
        if val < 7:
            return "background-color:#3D1515;color:#FF6B6B;font-weight:700"
        if val < 14:
            return "background-color:#2A1F0A;color:#FFA040"
        return ""

    styled = crit.style.applymap(_dtz_style, subset=["DTZ"])
    st.dataframe(styled, use_container_width=True, hide_index=True)


def render_sku_matrix(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-header">Capital Efficiency Matrix — SKU Strategy</div>',
                unsafe_allow_html=True)

    vel_mid = df["daily_sales_velocity"].median()
    mar_mid = df["profit_margin"].median()

    fig = go.Figure()
    for strategy, color in STRATEGY_COLORS.items():
        sub = df[df["strategy"] == strategy]
        fig.add_trace(go.Scatter(
            x=sub["daily_sales_velocity"],
            y=sub["profit_margin"],
            mode="markers",
            name=strategy,
            marker=dict(size=11, color=color, opacity=0.88,
                        line=dict(color="#1A1A18", width=1)),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>%{customdata[1]}<br>"
                "Velocity: %{x:.1f}/day | Margin: %{y:.1%}"
                "<extra></extra>"
            ),
            customdata=sub[["sku_id", "product_name"]].values,
        ))

    fig.add_vline(x=vel_mid, line_dash="dash", line_color="#3A3A36", line_width=1)
    fig.add_hline(y=mar_mid, line_dash="dash", line_color="#3A3A36", line_width=1)

    x_max = df["daily_sales_velocity"].max()
    y_max = df["profit_margin"].max()
    for (qx, qy, label, color) in [
        (x_max * 0.82, y_max * 0.93, "PUSH",    "#4CAF79"),
        (x_max * 0.08, y_max * 0.93, "BUNDLE",  "#C9A84C"),
        (x_max * 0.82, y_max * 0.04, "MONITOR", "#5B8ED6"),
        (x_max * 0.08, y_max * 0.04, "DISCOUNT","#CC4444"),
    ]:
        fig.add_annotation(x=qx, y=qy, text=label, showarrow=False,
                           font=dict(color=color, size=10, family="Arial"), opacity=0.45)

    fig.update_layout(
        paper_bgcolor="#1A1A18", plot_bgcolor="#1E1E1C",
        font=dict(color="#F0EDE4", family="Arial"),
        xaxis=dict(title="Daily Sales Velocity", gridcolor="#252522", zerolinecolor="#2E2E2A"),
        yaxis=dict(title="Profit Margin", gridcolor="#252522", zerolinecolor="#2E2E2A",
                   tickformat=".0%"),
        legend=dict(bgcolor="#232320", bordercolor="#3A3A36", borderwidth=1),
        margin=dict(l=10, r=10, t=10, b=10),
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Strategy count cards
    cols = st.columns(4)
    for col, (strategy, color) in zip(cols, STRATEGY_COLORS.items()):
        count = int((df["strategy"] == strategy).sum())
        col.markdown(
            f'<div class="strategy-card" style="border:1px solid {color};">'
            f'<span style="color:{color};font-size:1.5rem;font-weight:700;">{count}</span><br>'
            f'<span style="color:#888;font-size:0.7rem;text-transform:uppercase;'
            f'letter-spacing:0.1em;">{strategy}</span></div>',
            unsafe_allow_html=True,
        )


def render_seasonality(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-header">Temporal Relevance — Offer Timing Intelligence</div>',
                unsafe_allow_html=True)

    data = analyze_seasonality(df)
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data["months"], y=data["historical"],
        name="Historical Avg",
        line=dict(color="#555550", width=2, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=data["months"], y=data["current"],
        name="Current Trend",
        line=dict(color="#C9A84C", width=2.5),
        fill="tonexty", fillcolor="rgba(201,168,76,0.07)",
    ))

    for month in data["offer_windows"]:
        idx = data["months"].index(month)
        fig.add_vrect(
            x0=idx - 0.45, x1=idx + 0.45,
            fillcolor="rgba(76,175,121,0.10)", layer="below", line_width=0,
            annotation_text="Offer Window", annotation_position="top left",
            annotation_font=dict(color="#4CAF79", size=8),
        )

    cur_idx = data["months"].index(data["current_month"])
    fig.add_vline(
        x=cur_idx, line_dash="solid", line_color="#5B8ED6", line_width=1.5,
        annotation_text=f"Now ({data['current_month']})",
        annotation_font=dict(color="#5B8ED6", size=9),
    )

    fig.update_layout(
        paper_bgcolor="#1A1A18", plot_bgcolor="#1E1E1C",
        font=dict(color="#F0EDE4", family="Arial"),
        xaxis=dict(gridcolor="#252522"),
        yaxis=dict(title="Avg Daily Velocity", gridcolor="#252522"),
        legend=dict(bgcolor="#232320", bordercolor="#3A3A36", borderwidth=1),
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True)

    if data["offer_windows"]:
        windows = ", ".join(data["offer_windows"])
        st.markdown(
            f'<div class="offer-callout">'
            f'<span style="color:#4CAF79;font-weight:700;">Recommended launch windows: </span>'
            f'<span style="color:#F0EDE4;">{windows}</span>'
            f' — activate bundles or promotions 7-14 days before these peaks.'
            f'</div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 6. MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    # Load + process
    df = load_data()
    df = apply_revenue_guard(df)
    df = apply_sku_matrix(df)

    # Sidebar agent
    render_sidebar(df)

    # Page header
    st.markdown("""
    <div style="padding:6px 0 28px;">
        <span style="font-size:1.75rem;font-weight:800;color:#F0EDE4;letter-spacing:0.03em;">
            AI Decision Dashboard
        </span>
        <span style="color:#555550;margin-left:14px;font-size:0.82rem;letter-spacing:0.05em;">
            INVENTORY INTELLIGENCE FOR EYEWEAR
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Section 1 — KPIs
    render_kpis(df)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    # Sections 2 + 3 — Revenue Guard | SKU Matrix
    col_left, col_right = st.columns([1, 1.45], gap="large")
    with col_left:
        render_revenue_guard(df)
    with col_right:
        render_sku_matrix(df)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Section 4 — Seasonality
    render_seasonality(df)


if __name__ == "__main__":
    main()

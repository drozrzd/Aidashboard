"""
AI E-Commerce Decision Dashboard — Ombraz Glasses Demo
Stack: Streamlit + Pandas + Plotly + Supabase + Groq (Llama 3.3 70B)
Pages: Executive Overview | Trends + Competitors | Products | Customer + Delivery
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

# ── Palette ───────────────────────────────────────────────────────────────────
BG        = "#1A1A18"
BG2       = "#232320"
BG3       = "#1E1E1C"
BORDER    = "#2E2E2A"
TEXT      = "#F0EDE4"
MUTED     = "#888880"
GOLD      = "#C9A84C"
GREEN     = "#4CAF79"
RED       = "#CC4444"
BLUE      = "#5B8ED6"
SIDEBAR   = "#141412"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ── Base ── */
.stApp {{ background-color:{BG}; color:{TEXT}; }}
[data-testid="stSidebar"] {{
    background-color:{SIDEBAR};
    border-right:1px solid {BORDER};
    padding-top:0;
}}
[data-testid="stSidebar"] > div:first-child {{ padding-top:0; }}

/* ── Nav buttons ── */
.nav-btn {{
    display:block; width:100%; text-align:left;
    padding:11px 16px; margin:2px 0;
    border:none; border-radius:8px;
    background:transparent; color:{MUTED};
    font-size:0.875rem; font-weight:500; letter-spacing:0.02em;
    cursor:pointer; transition:all 0.15s ease;
}}
.nav-btn:hover {{ background:{BG2}; color:{TEXT}; }}
.nav-btn.active {{
    background:{BG2};
    color:{TEXT};
    border-left:3px solid {GOLD};
    padding-left:13px;
    font-weight:600;
}}

/* ── Cards ── */
.card {{
    background:{BG2};
    border:1px solid {BORDER};
    border-radius:12px;
    padding:20px;
    margin-bottom:16px;
}}
.card-sm {{
    background:{BG2};
    border:1px solid {BORDER};
    border-radius:10px;
    padding:14px 16px;
    margin-bottom:12px;
}}

/* ── Section headers ── */
.sec-head {{
    color:{GOLD};
    font-size:0.75rem;
    font-weight:700;
    text-transform:uppercase;
    letter-spacing:0.14em;
    border-bottom:1px solid {BORDER};
    padding-bottom:8px;
    margin-bottom:14px;
    margin-top:4px;
}}

/* ── KPI tiles ── */
[data-testid="metric-container"] {{
    background:{BG2};
    border:1px solid {BORDER};
    border-radius:10px;
    padding:16px;
}}
[data-testid="stMetricValue"] {{ color:{TEXT}; font-weight:700; }}
[data-testid="stMetricDelta"] {{ font-size:0.76rem; }}

/* ── Page title ── */
.page-title {{
    font-size:1.55rem; font-weight:800;
    color:{TEXT}; letter-spacing:0.02em;
    padding:8px 0 24px;
}}
.page-sub {{
    color:{MUTED}; font-size:0.78rem;
    letter-spacing:0.06em; text-transform:uppercase;
    margin-left:14px;
}}

/* ── Callouts ── */
.callout-green {{
    background:#1A2A1A; border:1px solid {GREEN};
    border-radius:8px; padding:12px 16px; margin:10px 0;
    font-size:0.875rem;
}}
.callout-gold {{
    background:#1E1A0A; border:1px solid {GOLD};
    border-radius:8px; padding:12px 16px; margin:10px 0;
    font-size:0.875rem;
}}
.callout-red {{
    background:#2A1010; border:1px solid {RED};
    border-radius:8px; padding:12px 16px; margin:10px 0;
    font-size:0.875rem;
}}

/* ── Tags ── */
.tag {{
    display:inline-block; border-radius:4px;
    padding:2px 8px; font-size:0.72rem; font-weight:700;
    text-transform:uppercase; letter-spacing:0.08em;
}}

/* ── Chat panel ── */
.chat-panel {{
    border-top:1px solid {BORDER};
    padding-top:16px;
    margin-top:auto;
}}
[data-testid="stChatInput"] textarea {{
    background:{BG2}; color:{TEXT}; border-color:#3A3A36;
    font-size:0.85rem;
}}
[data-testid="stChatMessage"] {{
    background:{BG3}; border-radius:8px; margin:4px 0;
    font-size:0.84rem;
}}

/* ── Divider ── */
hr {{ border-color:{BORDER}; margin:16px 0; }}

/* ── Dataframes ── */
[data-testid="stDataFrame"] iframe {{ background:{BG2}; }}
a {{ color:{GOLD}; }}

/* ── Strategy pills ── */
.pill-push    {{ background:#0E2A1A; color:{GREEN}; border:1px solid {GREEN}; }}
.pill-bundle  {{ background:#1E1A0A; color:{GOLD};  border:1px solid {GOLD};  }}
.pill-monitor {{ background:#0A1020; color:{BLUE};  border:1px solid {BLUE};  }}
.pill-disc    {{ background:#2A0E0E; color:{RED};   border:1px solid {RED};   }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. DATA GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_sku_data(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    styles = [
        "Classic Aviator", "Sport Wraparound", "Round Lens", "Wayfarers",
        "Cat Eye", "Rectangular", "Photochromic", "Polarized Shield",
        "Slim Oval", "Bold Square", "Retro Browline", "Rimless",
        "Semi-Rimless", "Geometric", "Oversized",
    ]
    colors = ["Gold", "Silver", "Black", "Tortoise", "Rose Gold",
              "Navy", "Olive", "Clear", "Brown", "Gunmetal"]
    categories = ["Sun", "Optical", "Blue Light"]
    month = datetime.now().month
    rows = []
    for i in range(50):
        cat = categories[i % 3]
        style = styles[i % len(styles)]
        color = colors[i % len(colors)]
        name = f"{style} - {color}"
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
        if cat == "Sun":
            base = 0.5 + 0.4 * np.sin((month - 3) * np.pi / 6)
        elif cat == "Blue Light":
            base = 0.65 + 0.1 * np.sin((month - 9) * np.pi / 6)
        else:
            base = 0.55 + 0.2 * np.sin((month - 1) * np.pi / 6)
        seasonality = round(float(np.clip(base + rng.uniform(-0.1, 0.1), 0.1, 1.0)), 3)
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


def generate_competitor_data() -> dict:
    """Price benchmarks, market share, ad spend, and recent releases for 5 brands."""
    brands = ["Ombraz", "Warby Parker", "Ray-Ban", "Oakley", "Maui Jim"]
    avg_prices = [189, 145, 172, 158, 229]
    market_share = [4.2, 8.7, 22.1, 14.3, 6.8]
    ad_spend_idx = [38, 72, 100, 85, 55]   # index: Ray-Ban = 100
    yoy_growth = [18.4, 6.2, 3.1, 4.8, 7.9]

    price_df = pd.DataFrame({
        "Brand": brands,
        "Avg Price ($)": avg_prices,
        "Market Share (%)": market_share,
        "Ad Spend Index": ad_spend_idx,
        "YoY Growth (%)": yoy_growth,
    })

    # 12-month search trend index by category
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    rng = np.random.default_rng(7)
    sun_trend    = [35, 42, 58, 74, 88, 95, 98, 90, 72, 50, 38, 32]
    optical_trend = [62, 65, 68, 60, 55, 52, 50, 54, 65, 70, 72, 75]
    bl_trend     = [70, 72, 68, 65, 62, 58, 60, 65, 72, 78, 80, 76]

    search_df = pd.DataFrame({
        "Month": months,
        "Sun": sun_trend,
        "Optical": optical_trend,
        "Blue Light": bl_trend,
    })

    # Recent releases / ad campaigns table
    releases_df = pd.DataFrame({
        "Brand": ["Ray-Ban", "Oakley", "Warby Parker", "Maui Jim", "Ombraz"],
        "Product": ["Meta Smart Glasses v3", "Kato Prizm Trail",
                    "Barkley Titanium", "Peahi Polarized", "Ridgeline Carbon"],
        "Category": ["Sun/Tech", "Sport", "Optical", "Sun", "Sun"],
        "Est. Ad Spend": ["$8.2M", "$5.1M", "$3.4M", "$2.8M", "$0.9M"],
        "Launch Month": ["Feb 2026", "Jan 2026", "Mar 2026", "Feb 2026", "Apr 2026"],
        "Price": ["$299", "$189", "$195", "$279", "$215"],
    })

    return {
        "price_df": price_df,
        "search_df": search_df,
        "releases_df": releases_df,
        "brands": brands,
        "avg_prices": avg_prices,
        "market_share": market_share,
        "months": months,
    }


def generate_customer_data(seed: int = 42) -> dict:
    """Order statuses, segments, regional distribution, delivery KPIs."""
    rng = np.random.default_rng(seed)

    order_statuses = {
        "Delivered": 1842,
        "In Transit": 387,
        "Processing": 214,
        "Returned": 93,
        "Cancelled": 41,
    }

    segments = pd.DataFrame({
        "Segment": ["Repeat Buyers", "First-Time", "At-Risk", "VIP (LTV > $500)", "Lapsed (90d+)"],
        "Count": [1124, 893, 312, 287, 441],
        "Avg LTV ($)": [342, 189, 210, 687, 156],
        "Avg Order ($)": [198, 176, 165, 312, 142],
    })

    regions = pd.DataFrame({
        "Region": ["California", "New York", "Texas", "Colorado", "Florida",
                   "Washington", "Oregon", "Arizona", "Nevada", "Utah"],
        "Orders": [487, 312, 241, 198, 167, 143, 128, 97, 84, 71],
        "Avg Order ($)": [214, 228, 187, 242, 195, 231, 219, 178, 203, 256],
        "Return Rate (%)": [4.1, 3.8, 5.2, 2.9, 4.7, 3.1, 3.4, 5.8, 4.2, 2.7],
    })

    delivery_kpis = {
        "avg_delivery_days": 3.4,
        "on_time_pct": 91.2,
        "return_rate_pct": 4.1,
        "csat_score": 4.6,
        "repeat_purchase_rate": 44.8,
        "avg_time_to_first_order": 2.1,
    }

    # 12-week order volume trend
    weeks = [f"W{i}" for i in range(1, 13)]
    order_vol = [320, 298, 345, 412, 389, 427, 455, 481, 443, 468, 502, 519]

    return {
        "order_statuses": order_statuses,
        "segments": segments,
        "regions": regions,
        "delivery_kpis": delivery_kpis,
        "weeks": weeks,
        "order_vol": order_vol,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SUPABASE + LOAD
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def _supabase_client():
    try:
        from supabase import create_client
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
        return create_client(url, key)
    except Exception:
        return None


def _seed_supabase(client, df: pd.DataFrame) -> None:
    try:
        client.table("sku_inventory").insert(df.to_dict(orient="records")).execute()
    except Exception as e:
        st.warning(f"Supabase seed failed: {e}")


@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    client = _supabase_client()
    if client:
        try:
            resp = client.table("sku_inventory").select("*").execute()
            if resp.data:
                df = pd.DataFrame(resp.data)
                drop = [c for c in ("id", "created_at") if c in df.columns]
                return df.drop(columns=drop)
            df = generate_sku_data()
            _seed_supabase(client, df)
            return df
        except Exception:
            pass
    return generate_sku_data()


# ═══════════════════════════════════════════════════════════════════════════════
# 3. CORE LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

def apply_revenue_guard(df: pd.DataFrame, lead_time: int = 7, safety_days: int = 7) -> pd.DataFrame:
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
    df = df.copy()
    vel_mid = df["daily_sales_velocity"].median()
    mar_mid = df["profit_margin"].median()

    def _cat(row):
        hv = row["daily_sales_velocity"] >= vel_mid
        hm = row["profit_margin"] >= mar_mid
        if hv and hm:   return "Push"
        if not hv and hm: return "Bundle"
        if hv and not hm: return "Monitor"
        return "Discount"

    df["strategy"] = df.apply(_cat, axis=1)
    return df


def analyze_seasonality(df: pd.DataFrame) -> dict:
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    m = datetime.now().month - 1
    avg_vel = df["daily_sales_velocity"].mean()
    historical = [avg_vel * (0.7 + 0.5 * np.sin((i - 2) * np.pi / 6)) for i in range(12)]
    current    = [historical[i] * (1.0 + 0.18 * np.sin((i - m) * np.pi / 3)) for i in range(12)]
    h_mean, h_std = np.mean(historical), np.std(historical)
    offer_windows = [months[i] for i in range(12) if current[i] > h_mean + h_std]
    return {"months": months, "historical": historical, "current": current,
            "offer_windows": offer_windows, "current_month": months[m]}


# ═══════════════════════════════════════════════════════════════════════════════
# 4. GROQ AI AGENT
# ═══════════════════════════════════════════════════════════════════════════════

def _build_context(df: pd.DataFrame) -> str:
    critical = (
        df[df["is_critical"]].sort_values("dtz")
        [["sku_id","product_name","dtz","lost_revenue_risk"]].head(8).to_string(index=False)
    )
    push = (
        df[df["strategy"]=="Push"].nlargest(5,"profit_margin")
        [["sku_id","product_name","daily_sales_velocity","profit_margin"]].to_string(index=False)
    )
    discount = (
        df[df["strategy"]=="Discount"].nsmallest(5,"daily_sales_velocity")
        [["sku_id","product_name","daily_sales_velocity","profit_margin"]].to_string(index=False)
    )
    counts = df["strategy"].value_counts().to_dict()
    return (
        f"SNAPSHOT {datetime.now().strftime('%Y-%m-%d')} | {len(df)} SKUs\n"
        f"Critical (DTZ<14): {df['is_critical'].sum()} | Total risk: ${df['lost_revenue_risk'].sum():,.0f}\n"
        f"Strategy mix: Push={counts.get('Push',0)} Bundle={counts.get('Bundle',0)} "
        f"Monitor={counts.get('Monitor',0)} Discount={counts.get('Discount',0)}\n\n"
        f"CRITICAL SKUs:\n{critical}\n\nTOP PUSH:\n{push}\n\nTOP DISCOUNT:\n{discount}"
    )


def _mock_response(question: str, df: pd.DataFrame) -> str:
    q = question.lower()
    critical = df[df["is_critical"]]
    if any(w in q for w in ["stock","run out","reorder","critical"]):
        top = critical.nsmallest(3,"dtz")
        names = "; ".join(f"{r.sku_id} — {r.dtz:.0f} days" for _,r in top.iterrows())
        return (f"{critical.shape[0]} SKUs need reorder now. Most urgent: {names}. "
                f"Total revenue at risk: ${critical['lost_revenue_risk'].sum():,.0f}.")
    if any(w in q for w in ["discount","slow","liquidat"]):
        items = df[df["strategy"]=="Discount"].nsmallest(3,"daily_sales_velocity")
        return f"Discount candidates: {', '.join(items['product_name'].tolist())}. Low velocity and thin margins."
    if any(w in q for w in ["push","ad spend","advertis","feature"]):
        items = df[df["strategy"]=="Push"].nlargest(3,"profit_margin")
        return f"Push these: {', '.join(items['product_name'].tolist())}. Strong velocity with high margins."
    return (f"Tracking {len(df)} SKUs. {df['is_critical'].sum()} need immediate reorder. "
            f"{len(df[df['strategy']=='Push'])} ready to push. Ask about stockouts, discounts, or ad spend.")


def get_agent_response(history: list, df: pd.DataFrame) -> str:
    try:
        from groq import Groq
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        system = (
            "You are a sharp, data-driven inventory analyst for Ombraz, a premium eyewear brand. "
            "Give direct, specific recommendations. Always reference SKU IDs and numbers. "
            "Never give generic advice. Be concise — max 3 sentences unless a list is needed.\n\n"
            f"CURRENT DATA:\n{_build_context(df)}"
        )
        messages = [{"role": "system", "content": system}] + history
        resp = Groq(api_key=st.secrets["GROQ_API_KEY"]).chat.completions.create(
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
# 5. SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

PAGES = [
    ("overview",   "Overview",              "📊"),
    ("trends",     "Trends + Competitors",  "📈"),
    ("products",   "Products",              "🕶️"),
    ("customers",  "Customer + Delivery",   "🚚"),
]


def render_sidebar(df: pd.DataFrame) -> None:
    with st.sidebar:
        # Brand block
        st.markdown(f"""
        <div style="text-align:center;padding:24px 0 16px;">
            <div style="font-size:1.45rem;font-weight:800;color:{GOLD};letter-spacing:0.18em;">
                OMBRAZ
            </div>
            <div style="font-size:0.6rem;color:{MUTED};letter-spacing:0.28em;
                        text-transform:uppercase;margin-top:3px;">
                AI Decision Agent
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f'<div style="border-bottom:1px solid {BORDER};margin:0 0 12px;"></div>',
                    unsafe_allow_html=True)

        # Navigation
        st.markdown(f'<div style="font-size:0.65rem;color:{MUTED};letter-spacing:0.14em;'
                    f'text-transform:uppercase;padding:4px 8px 6px;">Navigation</div>',
                    unsafe_allow_html=True)

        current = st.session_state.get("page", "overview")
        for page_id, label, icon in PAGES:
            is_active = current == page_id
            active_class = "active" if is_active else ""
            if st.button(f"{icon}  {label}", key=f"nav_{page_id}",
                         use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state["page"] = page_id
                st.rerun()

        st.markdown(f'<div style="border-bottom:1px solid {BORDER};margin:12px 0;"></div>',
                    unsafe_allow_html=True)

        # Quick stats
        st.markdown(f'<div style="font-size:0.65rem;color:{MUTED};letter-spacing:0.14em;'
                    f'text-transform:uppercase;padding:4px 8px 6px;">Quick Stats</div>',
                    unsafe_allow_html=True)

        critical_n = int(df["is_critical"].sum())
        risk = df["lost_revenue_risk"].sum()
        push_n = int((df["strategy"] == "Push").sum())

        st.markdown(f"""
        <div style="padding:0 4px;">
            <div style="display:flex;justify-content:space-between;
                        padding:7px 8px;border-radius:6px;margin:2px 0;">
                <span style="color:{MUTED};font-size:0.8rem;">Critical SKUs</span>
                <span style="color:{RED};font-weight:700;font-size:0.8rem;">{critical_n}</span>
            </div>
            <div style="display:flex;justify-content:space-between;
                        padding:7px 8px;border-radius:6px;margin:2px 0;">
                <span style="color:{MUTED};font-size:0.8rem;">Revenue Risk</span>
                <span style="color:{GOLD};font-weight:700;font-size:0.8rem;">${risk:,.0f}</span>
            </div>
            <div style="display:flex;justify-content:space-between;
                        padding:7px 8px;border-radius:6px;margin:2px 0;">
                <span style="color:{MUTED};font-size:0.8rem;">Push Ready</span>
                <span style="color:{GREEN};font-weight:700;font-size:0.8rem;">{push_n} SKUs</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f'<div style="border-bottom:1px solid {BORDER};margin:12px 0;"></div>',
                    unsafe_allow_html=True)

        # AI Chat
        st.markdown(f'<div style="font-size:0.65rem;color:{MUTED};letter-spacing:0.14em;'
                    f'text-transform:uppercase;padding:4px 8px 8px;">AI Agent Chat</div>',
                    unsafe_allow_html=True)

        if "messages" not in st.session_state:
            st.session_state.messages = [{
                "role": "assistant",
                "content": (
                    f"Inventory loaded. {critical_n} SKUs need reorder — "
                    f"${risk:,.0f} revenue at risk. Ask me what to push, discount, or reorder."
                ),
            }]

        chat_container = st.container(height=260)
        with chat_container:
            for msg in st.session_state.messages[-8:]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about inventory, trends..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Analyzing..."):
                reply = get_agent_response(list(st.session_state.messages), df)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# 6. PAGE: EXECUTIVE OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════

STRATEGY_COLORS = {"Push": GREEN, "Bundle": GOLD, "Monitor": BLUE, "Discount": RED}


def render_overview(df: pd.DataFrame) -> None:
    st.markdown(
        f'<div class="page-title">Executive Overview'
        f'<span class="page-sub">Inventory Intelligence</span></div>',
        unsafe_allow_html=True,
    )

    # KPI row
    monthly_rev = (df["selling_price"] * df["daily_sales_velocity"] * 30).sum()
    aov = df["selling_price"].mean()
    healthy_pct = (~df["is_critical"]).sum() / len(df) * 100
    risk = df["lost_revenue_risk"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Est. Monthly Revenue", f"${monthly_rev:,.0f}", "30-day projection")
    c2.metric("Avg Selling Price", f"${aov:,.2f}", f"{len(df)} active SKUs")
    c3.metric("Stock Health", f"{healthy_pct:.1f}%",
              f"{int(df['is_critical'].sum())} critical", delta_color="inverse")
    c4.metric("Revenue at Risk", f"${risk:,.0f}",
              "without reorder action", delta_color="inverse")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Revenue Guard | SKU Matrix
    col_left, col_right = st.columns([1, 1.5], gap="large")

    with col_left:
        st.markdown('<div class="sec-head">Revenue Guard — Reorder Alerts</div>',
                    unsafe_allow_html=True)
        crit = (
            df[df["is_critical"]].sort_values("dtz")
            [["sku_id","product_name","category","current_stock","daily_sales_velocity","dtz","lost_revenue_risk"]]
            .copy()
        )
        crit.columns = ["SKU","Product","Cat","Stock","Vel/Day","DTZ","Risk ($)"]

        if crit.empty:
            st.success("All SKUs healthy — no reorders required.")
        else:
            def _dtz_style(val):
                if val < 7:   return "background-color:#3D1515;color:#FF6B6B;font-weight:700"
                if val < 14:  return "background-color:#2A1F0A;color:#FFA040"
                return ""
            styled = crit.style.map(_dtz_style, subset=["DTZ"])
            st.dataframe(styled, use_container_width=True, hide_index=True)

    with col_right:
        st.markdown('<div class="sec-head">Capital Efficiency Matrix</div>',
                    unsafe_allow_html=True)
        vel_mid = df["daily_sales_velocity"].median()
        mar_mid = df["profit_margin"].median()
        fig = go.Figure()
        for strategy, color in STRATEGY_COLORS.items():
            sub = df[df["strategy"] == strategy]
            fig.add_trace(go.Scatter(
                x=sub["daily_sales_velocity"], y=sub["profit_margin"],
                mode="markers", name=strategy,
                marker=dict(size=10, color=color, opacity=0.88,
                            line=dict(color=BG, width=1)),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>%{customdata[1]}<br>"
                    "Velocity: %{x:.1f}/day | Margin: %{y:.1%}<extra></extra>"
                ),
                customdata=sub[["sku_id","product_name"]].values,
            ))
        fig.add_vline(x=vel_mid, line_dash="dash", line_color="#3A3A36", line_width=1)
        fig.add_hline(y=mar_mid, line_dash="dash", line_color="#3A3A36", line_width=1)
        x_max, y_max = df["daily_sales_velocity"].max(), df["profit_margin"].max()
        for qx, qy, label, color in [
            (x_max*0.82, y_max*0.93, "PUSH",    GREEN),
            (x_max*0.08, y_max*0.93, "BUNDLE",  GOLD),
            (x_max*0.82, y_max*0.04, "MONITOR", BLUE),
            (x_max*0.08, y_max*0.04, "DISCOUNT",RED),
        ]:
            fig.add_annotation(x=qx, y=qy, text=label, showarrow=False,
                               font=dict(color=color, size=10), opacity=0.45)
        fig.update_layout(
            paper_bgcolor=BG, plot_bgcolor=BG3,
            font=dict(color=TEXT, family="Arial"),
            xaxis=dict(title="Daily Sales Velocity", gridcolor="#252522", zerolinecolor=BORDER),
            yaxis=dict(title="Profit Margin", gridcolor="#252522", zerolinecolor=BORDER, tickformat=".0%"),
            legend=dict(bgcolor=BG2, bordercolor="#3A3A36", borderwidth=1),
            margin=dict(l=10, r=10, t=10, b=10), height=360,
        )
        st.plotly_chart(fig, use_container_width=True)

        cols = st.columns(4)
        for col, (strategy, color) in zip(cols, STRATEGY_COLORS.items()):
            count = int((df["strategy"] == strategy).sum())
            col.markdown(
                f'<div style="text-align:center;background:{BG2};border:1px solid {color};'
                f'border-radius:8px;padding:10px 4px;">'
                f'<span style="color:{color};font-size:1.4rem;font-weight:700;">{count}</span><br>'
                f'<span style="color:{MUTED};font-size:0.68rem;text-transform:uppercase;'
                f'letter-spacing:0.1em;">{strategy}</span></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Seasonality
    st.markdown('<div class="sec-head">Offer Timing Intelligence</div>', unsafe_allow_html=True)
    data = analyze_seasonality(df)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=data["months"], y=data["historical"], name="Historical Avg",
        line=dict(color="#555550", width=2, dash="dot"),
    ))
    fig2.add_trace(go.Scatter(
        x=data["months"], y=data["current"], name="Current Trend",
        line=dict(color=GOLD, width=2.5),
        fill="tonexty", fillcolor="rgba(201,168,76,0.07)",
    ))
    for month in data["offer_windows"]:
        idx = data["months"].index(month)
        fig2.add_vrect(
            x0=idx-0.45, x1=idx+0.45, fillcolor="rgba(76,175,121,0.10)",
            layer="below", line_width=0,
            annotation_text="Offer Window", annotation_position="top left",
            annotation_font=dict(color=GREEN, size=8),
        )
    cur_idx = data["months"].index(data["current_month"])
    fig2.add_vline(x=cur_idx, line_dash="solid", line_color=BLUE, line_width=1.5,
                  annotation_text=f"Now ({data['current_month']})",
                  annotation_font=dict(color=BLUE, size=9))
    fig2.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG3,
        font=dict(color=TEXT, family="Arial"),
        xaxis=dict(gridcolor="#252522"), yaxis=dict(title="Avg Daily Velocity", gridcolor="#252522"),
        legend=dict(bgcolor=BG2, bordercolor="#3A3A36", borderwidth=1),
        margin=dict(l=10, r=10, t=10, b=10), height=280,
    )
    st.plotly_chart(fig2, use_container_width=True)
    if data["offer_windows"]:
        windows = ", ".join(data["offer_windows"])
        st.markdown(
            f'<div class="callout-green">'
            f'<span style="color:{GREEN};font-weight:700;">Recommended launch windows: </span>'
            f'<span style="color:{TEXT};">{windows}</span>'
            f' — activate bundles or promotions 7-14 days before these peaks.</div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 7. PAGE: TRENDS + COMPETITORS
# ═══════════════════════════════════════════════════════════════════════════════

def render_trends() -> None:
    st.markdown(
        f'<div class="page-title">Trends + Competitors'
        f'<span class="page-sub">Market Intelligence</span></div>',
        unsafe_allow_html=True,
    )

    data = generate_competitor_data()
    price_df = data["price_df"]
    search_df = data["search_df"]

    # Row 1: Price Positioning | Market Share
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="sec-head">Price Positioning vs. Competitors</div>',
                    unsafe_allow_html=True)
        colors_bar = [GOLD if b == "Ombraz" else "#3A3A36" for b in price_df["Brand"]]
        fig = go.Figure(go.Bar(
            x=price_df["Brand"], y=price_df["Avg Price ($)"],
            marker_color=colors_bar,
            text=[f"${p}" for p in price_df["Avg Price ($)"]],
            textposition="outside",
            textfont=dict(color=TEXT, size=11),
        ))
        fig.update_layout(
            paper_bgcolor=BG, plot_bgcolor=BG3,
            font=dict(color=TEXT, family="Arial"),
            xaxis=dict(gridcolor="#252522"),
            yaxis=dict(title="Avg Price ($)", gridcolor="#252522", range=[0, 280]),
            margin=dict(l=10, r=10, t=10, b=10), height=300,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Positioning note
        ombraz_price = 189
        ray_ban_price = 172
        maui_price = 229
        st.markdown(
            f'<div class="callout-gold">'
            f'<span style="color:{GOLD};font-weight:700;">Positioning: </span>'
            f'Ombraz sits 10% above Ray-Ban (${ray_ban_price}) and 17% below Maui Jim (${maui_price}). '
            f'Premium-adjacent — justified by direct-to-consumer margins.</div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown('<div class="sec-head">Competitor Snapshot</div>',
                    unsafe_allow_html=True)

        for _, row in price_df.iterrows():
            is_ombraz = row["Brand"] == "Ombraz"
            border_color = GOLD if is_ombraz else BORDER
            growth_color = GREEN if row["YoY Growth (%)"] > 10 else (GOLD if row["YoY Growth (%)"] > 5 else MUTED)
            st.markdown(
                f'<div style="background:{BG2};border:1px solid {border_color};'
                f'border-radius:8px;padding:10px 14px;margin-bottom:8px;'
                f'display:flex;justify-content:space-between;align-items:center;">'
                f'<div>'
                f'<span style="color:{"#C9A84C" if is_ombraz else TEXT};font-weight:{"700" if is_ombraz else "500"};'
                f'font-size:0.88rem;">{row["Brand"]}</span>'
                f'<span style="color:{MUTED};font-size:0.75rem;margin-left:8px;">'
                f'Mkt Share: {row["Market Share (%)"]}%</span>'
                f'</div>'
                f'<div style="text-align:right;">'
                f'<span style="color:{TEXT};font-weight:700;font-size:0.88rem;">${row["Avg Price ($)"]}</span>'
                f'<span style="color:{growth_color};font-size:0.75rem;margin-left:10px;">'
                f'+{row["YoY Growth (%)"]}% YoY</span>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Row 2: Search Trends | Ad Spend
    col3, col4 = st.columns([1.6, 1], gap="large")

    with col3:
        st.markdown('<div class="sec-head">Search Demand Trends by Category (12 Months)</div>',
                    unsafe_allow_html=True)
        fig2 = go.Figure()
        trend_colors = {"Sun": GOLD, "Optical": BLUE, "Blue Light": GREEN}
        for cat, color in trend_colors.items():
            fig2.add_trace(go.Scatter(
                x=search_df["Month"], y=search_df[cat],
                name=cat, line=dict(color=color, width=2.5),
                fill="tozeroy", fillcolor=color.replace("#", "rgba(") + ",0.05)" if "#" in color else color,
            ))
        cur_month_abbr = datetime.now().strftime("%b")
        if cur_month_abbr in search_df["Month"].values:
            cur_idx = list(search_df["Month"]).index(cur_month_abbr)
            fig2.add_vline(x=cur_idx, line_dash="solid", line_color=MUTED, line_width=1,
                          annotation_text="Now", annotation_font=dict(color=MUTED, size=9))
        fig2.update_layout(
            paper_bgcolor=BG, plot_bgcolor=BG3,
            font=dict(color=TEXT, family="Arial"),
            xaxis=dict(gridcolor="#252522"),
            yaxis=dict(title="Search Index", gridcolor="#252522"),
            legend=dict(bgcolor=BG2, bordercolor="#3A3A36", borderwidth=1),
            margin=dict(l=10, r=10, t=10, b=10), height=300,
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col4:
        st.markdown('<div class="sec-head">Ad Spend Index</div>', unsafe_allow_html=True)
        spend_df = price_df.sort_values("Ad Spend Index", ascending=True)
        colors_spend = [GOLD if b == "Ombraz" else "#3A3A36" for b in spend_df["Brand"]]
        fig3 = go.Figure(go.Bar(
            x=spend_df["Ad Spend Index"], y=spend_df["Brand"],
            orientation="h",
            marker_color=colors_spend,
            text=spend_df["Ad Spend Index"],
            textposition="outside",
            textfont=dict(color=TEXT, size=10),
        ))
        fig3.update_layout(
            paper_bgcolor=BG, plot_bgcolor=BG3,
            font=dict(color=TEXT, family="Arial"),
            xaxis=dict(title="Index (Ray-Ban = 100)", gridcolor="#252522", range=[0, 120]),
            yaxis=dict(gridcolor="#252522"),
            margin=dict(l=10, r=10, t=10, b=10), height=300,
            showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Row 3: New Releases + Ad Campaigns Table
    st.markdown('<div class="sec-head">Recent Launches + Ad Campaigns</div>',
                unsafe_allow_html=True)
    releases_df = data["releases_df"]

    def highlight_ombraz(row):
        if row["Brand"] == "Ombraz":
            return [f"background-color:#1E1A0A;color:{GOLD}"] * len(row)
        return [""] * len(row)

    styled = releases_df.style.apply(highlight_ombraz, axis=1)
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown(
        f'<div class="callout-red">'
        f'<span style="color:{RED};font-weight:700;">Watch: </span>'
        f'Ray-Ban Meta v3 and Oakley Kato are commanding the largest ad budgets heading into Q2. '
        f'Ombraz Ridgeline Carbon launched April 2026 with a fraction of the spend — '
        f'organic and influencer channels are critical to close the awareness gap.</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 8. PAGE: PRODUCTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_products(df: pd.DataFrame) -> None:
    st.markdown(
        f'<div class="page-title">Products'
        f'<span class="page-sub">SKU Performance</span></div>',
        unsafe_allow_html=True,
    )

    # Row 1: Category summary cards
    st.markdown('<div class="sec-head">Category Breakdown</div>', unsafe_allow_html=True)
    cats = ["Sun", "Optical", "Blue Light"]
    cat_cols = st.columns(3, gap="medium")
    cat_icons = {"Sun": "☀️", "Optical": "👓", "Blue Light": "💻"}
    cat_colors = {"Sun": GOLD, "Optical": BLUE, "Blue Light": GREEN}

    for col, cat in zip(cat_cols, cats):
        sub = df[df["category"] == cat]
        monthly = (sub["selling_price"] * sub["daily_sales_velocity"] * 30).sum()
        avg_margin = sub["profit_margin"].mean()
        critical_n = sub["is_critical"].sum()
        push_n = (sub["strategy"] == "Push").sum()
        color = cat_colors[cat]
        with col:
            st.markdown(
                f'<div style="background:{BG2};border:1px solid {color};border-radius:12px;'
                f'padding:18px;margin-bottom:4px;">'
                f'<div style="font-size:1.3rem;margin-bottom:6px;">{cat_icons[cat]}</div>'
                f'<div style="color:{TEXT};font-weight:700;font-size:1rem;margin-bottom:10px;">{cat}</div>'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:5px;">'
                f'<span style="color:{MUTED};font-size:0.78rem;">Monthly Rev</span>'
                f'<span style="color:{TEXT};font-size:0.78rem;font-weight:600;">${monthly:,.0f}</span>'
                f'</div>'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:5px;">'
                f'<span style="color:{MUTED};font-size:0.78rem;">Avg Margin</span>'
                f'<span style="color:{color};font-size:0.78rem;font-weight:600;">{avg_margin:.1%}</span>'
                f'</div>'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:5px;">'
                f'<span style="color:{MUTED};font-size:0.78rem;">Critical SKUs</span>'
                f'<span style="color:{RED if critical_n > 0 else GREEN};font-size:0.78rem;'
                f'font-weight:600;">{critical_n}</span>'
                f'</div>'
                f'<div style="display:flex;justify-content:space-between;">'
                f'<span style="color:{MUTED};font-size:0.78rem;">Push Ready</span>'
                f'<span style="color:{GREEN};font-size:0.78rem;font-weight:600;">{push_n}</span>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Row 2: Velocity chart | Reorder planner
    col_left, col_right = st.columns([1.4, 1], gap="large")

    with col_left:
        st.markdown('<div class="sec-head">Sales Velocity by SKU — Top 20</div>',
                    unsafe_allow_html=True)

        # Velocity toggle
        period = st.radio("View period", ["Daily", "Weekly", "Monthly"],
                          horizontal=True, key="velocity_period", label_visibility="collapsed")
        mult = {"Daily": 1, "Weekly": 7, "Monthly": 30}[period]
        unit = {"Daily": "/day", "Weekly": "/wk", "Monthly": "/mo"}[period]

        top20 = df.nlargest(20, "daily_sales_velocity").copy()
        top20["display_vel"] = (top20["daily_sales_velocity"] * mult).round(1)
        bar_colors = [STRATEGY_COLORS.get(s, MUTED) for s in top20["strategy"]]

        fig4 = go.Figure(go.Bar(
            x=top20["display_vel"],
            y=top20["product_name"].str[:28],
            orientation="h",
            marker_color=bar_colors,
            text=[f'{v:.1f}{unit}' for v in top20["display_vel"]],
            textposition="outside",
            textfont=dict(color=TEXT, size=9),
        ))
        fig4.update_layout(
            paper_bgcolor=BG, plot_bgcolor=BG3,
            font=dict(color=TEXT, family="Arial", size=10),
            xaxis=dict(title=f"Units Sold ({unit})", gridcolor="#252522"),
            yaxis=dict(gridcolor="#252522", autorange="reversed"),
            margin=dict(l=10, r=60, t=10, b=10), height=460,
            showlegend=False,
        )
        st.plotly_chart(fig4, use_container_width=True)

    with col_right:
        st.markdown('<div class="sec-head">Reorder Planner</div>', unsafe_allow_html=True)

        reorder = (
            df[df["is_critical"]]
            .sort_values("dtz")
            [["sku_id","product_name","current_stock","daily_sales_velocity","dtz","selling_price"]]
            .copy()
        )
        if reorder.empty:
            st.markdown(
                f'<div class="callout-green"><span style="color:{GREEN};font-weight:700;">All clear</span>'
                f' — no reorders needed right now.</div>',
                unsafe_allow_html=True,
            )
        else:
            # Compute suggested order qty (30-day supply)
            reorder["Suggest Qty"] = (reorder["daily_sales_velocity"] * 30 - reorder["current_stock"]).clip(lower=0).astype(int)
            reorder["Est. Cost"] = (reorder["Suggest Qty"] * reorder["selling_price"] * 0.42).round(0).astype(int)
            display = reorder[["sku_id","product_name","dtz","Suggest Qty","Est. Cost"]].copy()
            display.columns = ["SKU","Product","DTZ","Qty","Est Cost ($)"]
            display["Product"] = display["Product"].str[:22]

            def _dtz_style(val):
                if val < 7:  return "background-color:#3D1515;color:#FF6B6B;font-weight:700"
                if val < 14: return "background-color:#2A1F0A;color:#FFA040"
                return ""

            styled = display.style.map(_dtz_style, subset=["DTZ"])
            st.dataframe(styled, use_container_width=True, hide_index=True)

            total_cost = reorder["Est. Cost"].sum()
            st.markdown(
                f'<div class="callout-gold">'
                f'<span style="color:{GOLD};font-weight:700;">Est. Reorder Spend: </span>'
                f'${total_cost:,.0f} to restore 30-day coverage across {len(reorder)} SKUs.</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Row 3: Margin distribution
    st.markdown('<div class="sec-head">Margin vs. Velocity — Full SKU View</div>',
                unsafe_allow_html=True)
    col5, col6 = st.columns(2, gap="large")

    with col5:
        # Margin histogram by category
        fig5 = go.Figure()
        for cat, color in cat_colors.items():
            sub = df[df["category"] == cat]
            fig5.add_trace(go.Histogram(
                x=sub["profit_margin"], name=cat,
                nbinsx=12, marker_color=color, opacity=0.75,
            ))
        fig5.update_layout(
            paper_bgcolor=BG, plot_bgcolor=BG3,
            font=dict(color=TEXT, family="Arial"),
            xaxis=dict(title="Profit Margin", tickformat=".0%", gridcolor="#252522"),
            yaxis=dict(title="SKU Count", gridcolor="#252522"),
            legend=dict(bgcolor=BG2, bordercolor="#3A3A36", borderwidth=1),
            barmode="overlay",
            margin=dict(l=10, r=10, t=10, b=10), height=260,
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        # Strategy distribution donut
        strategy_counts = df["strategy"].value_counts()
        fig6 = go.Figure(go.Pie(
            labels=strategy_counts.index,
            values=strategy_counts.values,
            hole=0.55,
            marker_colors=[STRATEGY_COLORS.get(s, MUTED) for s in strategy_counts.index],
            textinfo="label+percent",
            textfont=dict(color=TEXT, size=11),
        ))
        fig6.update_layout(
            paper_bgcolor=BG,
            font=dict(color=TEXT, family="Arial"),
            legend=dict(bgcolor=BG2, bordercolor="#3A3A36", borderwidth=1),
            margin=dict(l=10, r=10, t=10, b=10), height=260,
            showlegend=False,
            annotations=[dict(text="SKU Mix", x=0.5, y=0.5, font_size=13,
                             font_color=TEXT, showarrow=False)],
        )
        st.plotly_chart(fig6, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 9. PAGE: CUSTOMER + DELIVERY
# ═══════════════════════════════════════════════════════════════════════════════

def render_customers() -> None:
    st.markdown(
        f'<div class="page-title">Customer + Delivery'
        f'<span class="page-sub">Order Intelligence</span></div>',
        unsafe_allow_html=True,
    )

    cdata = generate_customer_data()
    kpis = cdata["delivery_kpis"]

    # KPI row
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Avg Delivery",   f"{kpis['avg_delivery_days']} days", "Target: 3.0d", delta_color="inverse")
    c2.metric("On-Time Rate",   f"{kpis['on_time_pct']}%",   "+1.4% vs last qtr")
    c3.metric("Return Rate",    f"{kpis['return_rate_pct']}%", "-0.3% vs last qtr")
    c4.metric("CSAT Score",     f"{kpis['csat_score']} / 5",  "Based on 1,842 reviews")
    c5.metric("Repeat Purchase", f"{kpis['repeat_purchase_rate']}%", "+3.1% vs last qtr")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Row 2: Order status donut | Customer segments
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="sec-head">Order Status Breakdown</div>',
                    unsafe_allow_html=True)
        statuses = cdata["order_statuses"]
        status_colors = {
            "Delivered": GREEN, "In Transit": BLUE,
            "Processing": GOLD, "Returned": RED, "Cancelled": "#664444",
        }
        fig1 = go.Figure(go.Pie(
            labels=list(statuses.keys()),
            values=list(statuses.values()),
            hole=0.58,
            marker_colors=[status_colors.get(s, MUTED) for s in statuses.keys()],
            textinfo="label+percent",
            textfont=dict(color=TEXT, size=11),
        ))
        total_orders = sum(statuses.values())
        fig1.update_layout(
            paper_bgcolor=BG,
            font=dict(color=TEXT, family="Arial"),
            margin=dict(l=10, r=10, t=10, b=10), height=300,
            showlegend=False,
            annotations=[dict(
                text=f"<b>{total_orders:,}</b><br>Orders",
                x=0.5, y=0.5, font_size=13, font_color=TEXT, showarrow=False,
            )],
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Status detail rows
        for status, count in statuses.items():
            pct = count / total_orders * 100
            color = status_colors.get(status, MUTED)
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:5px 8px;margin:2px 0;border-radius:5px;">'
                f'<span style="color:{color};font-size:0.82rem;font-weight:500;">{status}</span>'
                f'<span style="color:{MUTED};font-size:0.78rem;">{count:,} &nbsp; '
                f'<span style="color:{TEXT};">{pct:.1f}%</span></span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown('<div class="sec-head">Customer Segments</div>',
                    unsafe_allow_html=True)
        segs = cdata["segments"]
        seg_colors_list = [GREEN, BLUE, RED, GOLD, MUTED]
        fig2 = go.Figure(go.Bar(
            x=segs["Segment"],
            y=segs["Count"],
            marker_color=seg_colors_list,
            text=segs["Count"],
            textposition="outside",
            textfont=dict(color=TEXT, size=10),
        ))
        fig2.update_layout(
            paper_bgcolor=BG, plot_bgcolor=BG3,
            font=dict(color=TEXT, family="Arial"),
            xaxis=dict(gridcolor="#252522"),
            yaxis=dict(title="Customers", gridcolor="#252522"),
            margin=dict(l=10, r=10, t=10, b=10), height=240,
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

        # LTV summary
        st.markdown(
            f'<div class="callout-gold">'
            f'<span style="color:{GOLD};font-weight:700;">VIP Focus: </span>'
            f'{int(segs[segs["Segment"]=="VIP (LTV > $500)"]["Count"])} customers with avg LTV $687 '
            f'account for disproportionate revenue. Priority for loyalty programs and early access.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Row 3: Regional distribution | Order volume trend
    col3, col4 = st.columns([1, 1.2], gap="large")

    with col3:
        st.markdown('<div class="sec-head">Regional Distribution — Top 10</div>',
                    unsafe_allow_html=True)
        regions = cdata["regions"]

        def highlight_region(row):
            if row["Orders"] == regions["Orders"].max():
                return [f"background-color:#1E1A0A;color:{GOLD}"] * len(row)
            return [""] * len(row)

        styled = regions.style.apply(highlight_region, axis=1)
        st.dataframe(styled, use_container_width=True, hide_index=True)

        st.markdown(
            f'<div class="callout-green" style="margin-top:8px;">'
            f'<span style="color:{GREEN};font-weight:700;">Top market: </span>'
            f'California — 487 orders with ${regions[regions["Region"]=="California"]["Avg Order ($)"].values[0]} AOV. '
            f'Colorado shows lowest return rate at 2.9%.</div>',
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown('<div class="sec-head">Order Volume — 12 Week Trend</div>',
                    unsafe_allow_html=True)
        weeks = cdata["weeks"]
        order_vol = cdata["order_vol"]
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=weeks, y=order_vol,
            line=dict(color=GOLD, width=2.5),
            fill="tozeroy", fillcolor="rgba(201,168,76,0.08)",
            mode="lines+markers",
            marker=dict(color=GOLD, size=6),
        ))
        # Trend line
        z = np.polyfit(range(len(order_vol)), order_vol, 1)
        p = np.poly1d(z)
        fig3.add_trace(go.Scatter(
            x=weeks, y=[p(i) for i in range(len(weeks))],
            line=dict(color=GREEN, width=1.5, dash="dash"),
            name="Trend", showlegend=False,
        ))
        fig3.update_layout(
            paper_bgcolor=BG, plot_bgcolor=BG3,
            font=dict(color=TEXT, family="Arial"),
            xaxis=dict(gridcolor="#252522"),
            yaxis=dict(title="Orders", gridcolor="#252522"),
            margin=dict(l=10, r=10, t=10, b=10), height=280,
            showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)

        # Week-over-week growth
        wow = (order_vol[-1] - order_vol[-2]) / order_vol[-2] * 100
        total_12w = sum(order_vol)
        st.markdown(
            f'<div style="display:flex;gap:16px;margin-top:4px;">'
            f'<div style="background:{BG2};border:1px solid {BORDER};border-radius:8px;'
            f'padding:12px 18px;flex:1;text-align:center;">'
            f'<div style="color:{GREEN};font-size:1.2rem;font-weight:700;">+{wow:.1f}%</div>'
            f'<div style="color:{MUTED};font-size:0.72rem;text-transform:uppercase;'
            f'letter-spacing:0.08em;">WoW Growth</div>'
            f'</div>'
            f'<div style="background:{BG2};border:1px solid {BORDER};border-radius:8px;'
            f'padding:12px 18px;flex:1;text-align:center;">'
            f'<div style="color:{TEXT};font-size:1.2rem;font-weight:700;">{total_12w:,}</div>'
            f'<div style="color:{MUTED};font-size:0.72rem;text-transform:uppercase;'
            f'letter-spacing:0.08em;">12-Week Total</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 10. MAIN — ROUTER
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    df = load_data()
    df = apply_revenue_guard(df)
    df = apply_sku_matrix(df)

    render_sidebar(df)

    page = st.session_state.get("page", "overview")

    if page == "overview":
        render_overview(df)
    elif page == "trends":
        render_trends()
    elif page == "products":
        render_products(df)
    elif page == "customers":
        render_customers()
    else:
        render_overview(df)


if __name__ == "__main__":
    main()

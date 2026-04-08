"""
AI E-Commerce Decision Dashboard — Ombraz Glasses Demo
Stack: Streamlit + Pandas + Plotly + Supabase + Groq (Llama 3.3 70B)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="AI Decision Dashboard | Ombraz",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Palette ───────────────────────────────────────────────────────────────────
BG      = "#1A1A18"
BG2     = "#232320"
BG3     = "#1E1E1C"
BORDER  = "#2E2E2A"
TEXT    = "#F0EDE4"
MUTED   = "#7A7A72"
GOLD    = "#C9A84C"
GREEN   = "#4CAF79"
RED     = "#CC4444"
BLUE    = "#5B8ED6"
SIDEBAR = "#141412"

def rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Montserrat:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], [data-testid="stAppViewContainer"],
.stApp, .stMarkdown, p, span, div, label, input {{
    font-family: 'Montserrat', sans-serif !important;
}}

.stApp {{ background-color:{BG}; color:{TEXT}; }}
[data-testid="stSidebar"] {{
    background-color:{SIDEBAR};
    border-right:1px solid {BORDER};
}}
[data-testid="stSidebar"] > div:first-child {{ padding-top:0 !important; }}

/* ── Sidebar nav buttons ── */
[data-testid="stSidebar"] .stButton > button {{
    background:transparent !important;
    border:none !important;
    border-left:3px solid transparent !important;
    border-radius:0 6px 6px 0 !important;
    color:{MUTED} !important;
    font-family:'Montserrat',sans-serif !important;
    font-size:0.8rem !important;
    font-weight:500 !important;
    text-align:left !important;
    padding:9px 14px 9px 11px !important;
    margin:1px 0 !important;
    width:100% !important;
    box-shadow:none !important;
    transition:all 0.12s ease !important;
    justify-content:flex-start !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background:{BG2} !important;
    color:{TEXT} !important;
    border-left:3px solid {BORDER} !important;
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    background:{BG2} !important;
    color:{TEXT} !important;
    border-left:3px solid {GOLD} !important;
    font-weight:600 !important;
}}
[data-testid="stSidebar"] .stButton > button:focus:not(:active) {{
    box-shadow:none !important;
}}

/* ── KPI tiles ── */
[data-testid="metric-container"] {{
    background:{BG2}; border:1px solid {BORDER};
    border-radius:10px; padding:16px 18px;
}}
[data-testid="stMetricLabel"] {{
    color:{MUTED} !important; font-size:0.68rem !important;
    font-weight:600 !important; text-transform:uppercase; letter-spacing:0.12em;
}}
[data-testid="stMetricValue"] {{
    color:{TEXT} !important; font-weight:700 !important; font-size:1.45rem !important;
}}
[data-testid="stMetricDelta"] {{ font-size:0.7rem !important; }}

/* ── Section headers ── */
.sec-head {{
    color:{MUTED}; font-size:0.64rem; font-weight:700;
    text-transform:uppercase; letter-spacing:0.16em;
    border-bottom:1px solid {BORDER}; padding-bottom:7px;
    margin-bottom:12px; margin-top:2px;
}}

/* ── Page title ── */
.page-title {{ font-size:1.45rem; font-weight:800; color:{TEXT};
    letter-spacing:0.01em; padding:4px 0 18px; line-height:1.1; }}
.page-sub {{ color:{MUTED}; font-size:0.62rem; font-weight:500;
    letter-spacing:0.12em; text-transform:uppercase; margin-left:14px; vertical-align:middle; }}

/* ── Callouts ── */
.callout-green {{ background:rgba(76,175,121,0.08); border:1px solid rgba(76,175,121,0.28);
    border-radius:8px; padding:10px 14px; margin:7px 0; font-size:0.8rem; line-height:1.5; }}
.callout-gold  {{ background:rgba(201,168,76,0.08);  border:1px solid rgba(201,168,76,0.28);
    border-radius:8px; padding:10px 14px; margin:7px 0; font-size:0.8rem; line-height:1.5; }}
.callout-red   {{ background:rgba(204,68,68,0.08);   border:1px solid rgba(204,68,68,0.28);
    border-radius:8px; padding:10px 14px; margin:7px 0; font-size:0.8rem; line-height:1.5; }}
.callout-blue  {{ background:rgba(91,142,214,0.08);  border:1px solid rgba(91,142,214,0.28);
    border-radius:8px; padding:10px 14px; margin:7px 0; font-size:0.8rem; line-height:1.5; }}

/* ── Legend boxes ── */
.legend-box {{
    background:{BG3}; border:1px solid {BORDER}; border-radius:8px;
    padding:12px 14px; margin:6px 0; font-size:0.76rem; line-height:1.7;
}}
.legend-row {{ display:flex; align-items:flex-start; gap:10px; margin:4px 0; }}
.legend-dot {{ width:10px; height:10px; border-radius:50%; flex-shrink:0; margin-top:3px; }}

/* ── Chat ── */
[data-testid="stChatInput"] textarea {{
    background:{BG2}; color:{TEXT}; border-color:#3A3A36;
    font-family:'Montserrat',sans-serif !important; font-size:0.8rem;
}}
[data-testid="stChatMessage"] {{ font-size:0.8rem; }}

/* ── Customer table rows ── */
.cust-row {{
    background:{BG2}; border:1px solid {BORDER}; border-radius:8px;
    padding:10px 14px; margin-bottom:6px;
}}

hr {{ border-color:{BORDER}; margin:10px 0; }}
a {{ color:{GOLD}; }}
[data-testid="stDataFrame"] iframe {{ background:{BG2}; }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SVG ICONS
# ═══════════════════════════════════════════════════════════════════════════════

def icon_chart(size=15, color=MUTED):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
            f'<rect x="2" y="12" width="4" height="10" rx="1"/>'
            f'<rect x="10" y="6" width="4" height="16" rx="1"/>'
            f'<rect x="18" y="2" width="4" height="20" rx="1"/>'
            f'</svg>')

def icon_trending(size=15, color=MUTED):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
            f'<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>'
            f'<polyline points="17 6 23 6 23 12"/>'
            f'</svg>')

def icon_tag(size=15, color=MUTED):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/>'
            f'<line x1="7" y1="7" x2="7.01" y2="7"/>'
            f'</svg>')

def icon_truck(size=15, color=MUTED):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
            f'<rect x="1" y="3" width="15" height="13" rx="1"/>'
            f'<path d="M16 8h4l3 5v3h-7V8z"/>'
            f'<circle cx="5.5" cy="18.5" r="2.5"/>'
            f'<circle cx="18.5" cy="18.5" r="2.5"/>'
            f'</svg>')

def icon_sun(size=26, color=GOLD):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="1.5" stroke-linecap="round">'
            f'<circle cx="12" cy="12" r="4"/>'
            f'<line x1="12" y1="2" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="22"/>'
            f'<line x1="4.22" y1="4.22" x2="6.34" y2="6.34"/>'
            f'<line x1="17.66" y1="17.66" x2="19.78" y2="19.78"/>'
            f'<line x1="2" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="22" y2="12"/>'
            f'<line x1="4.22" y1="19.78" x2="6.34" y2="17.66"/>'
            f'<line x1="17.66" y1="6.34" x2="19.78" y2="4.22"/>'
            f'</svg>')

def icon_glasses(size=26, color=BLUE):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            f'<circle cx="7" cy="13" r="4"/><circle cx="17" cy="13" r="4"/>'
            f'<path d="M11 13h2"/>'
            f'<path d="M3 13C3 11 2 9 2 9"/><path d="M21 13c0-2 1-4 1-4"/>'
            f'</svg>')

def icon_monitor(size=26, color=GREEN):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            f'<rect x="2" y="3" width="20" height="14" rx="2"/>'
            f'<path d="M8 21h8"/><path d="M12 17v4"/>'
            f'</svg>')


# ═══════════════════════════════════════════════════════════════════════════════
# TEST CUSTOMERS
# ═══════════════════════════════════════════════════════════════════════════════

TEST_CUSTOMERS = [
    {
        "id": "C-001", "name": "Alex Rivera",  "city": "Denver, CO",
        "segment": "VIP",    "orders": 8,  "ltv": 847, "aov": 212,
        "last_order": "Mar 28, 2026",
        "skus": ["GL-001", "GL-004", "GL-013"],
        "categories": ["Sun", "Optical"],
        "note": "Prefers polarized Sun frames. High reorder rate, rarely returns.",
    },
    {
        "id": "C-002", "name": "Maya Chen",    "city": "New York, NY",
        "segment": "Repeat", "orders": 5,  "ltv": 512, "aov": 178,
        "last_order": "Apr 2, 2026",
        "skus": ["GL-003", "GL-006", "GL-021"],
        "categories": ["Blue Light"],
        "note": "Works remote. Buys Blue Light annually for team gifting.",
    },
    {
        "id": "C-003", "name": "Jordan Walsh",  "city": "Los Angeles, CA",
        "segment": "VIP",    "orders": 11, "ltv": 1340, "aov": 298,
        "last_order": "Apr 5, 2026",
        "skus": ["GL-001", "GL-007", "GL-003", "GL-010"],
        "categories": ["Sun", "Optical", "Blue Light"],
        "note": "Buys across all categories. Brand-loyal. High average order.",
    },
    {
        "id": "C-004", "name": "Sam Torres",   "city": "Austin, TX",
        "segment": "New",    "orders": 1,  "ltv": 189, "aov": 189,
        "last_order": "Mar 31, 2026",
        "skus": ["GL-010"],
        "categories": ["Sun"],
        "note": "First purchase. Discovery via Instagram. Sun category.",
    },
    {
        "id": "C-005", "name": "Riley Kim",    "city": "Seattle, WA",
        "segment": "Repeat", "orders": 4,  "ltv": 489, "aov": 163,
        "last_order": "Mar 15, 2026",
        "skus": ["GL-002", "GL-005", "GL-009"],
        "categories": ["Optical", "Blue Light"],
        "note": "Tech professional. Buys Optical and Blue Light. Low return rate.",
    },
    {
        "id": "C-006", "name": "Casey Morgan",  "city": "Boulder, CO",
        "segment": "VIP",    "orders": 9,  "ltv": 1124, "aov": 249,
        "last_order": "Apr 6, 2026",
        "skus": ["GL-007", "GL-013", "GL-004", "GL-016"],
        "categories": ["Sun"],
        "note": "Outdoor enthusiast. Sun-only buyer. Refers 2 friends per year on average.",
    },
    {
        "id": "C-007", "name": "Drew Patel",   "city": "San Francisco, CA",
        "segment": "At-Risk","orders": 3,  "ltv": 310, "aov": 155,
        "last_order": "Jan 12, 2026",
        "skus": ["GL-002", "GL-008"],
        "categories": ["Optical"],
        "note": "Was buying quarterly. Went silent after Jan. Potential churn — needs win-back.",
    },
    {
        "id": "C-008", "name": "Taylor Brooks", "city": "Portland, OR",
        "segment": "Repeat", "orders": 6,  "ltv": 634, "aov": 192,
        "last_order": "Mar 20, 2026",
        "skus": ["GL-003", "GL-015", "GL-006"],
        "categories": ["Blue Light", "Optical"],
        "note": "Designer. Buys for aesthetic. Blue Light primary. Optical secondary.",
    },
    {
        "id": "C-009", "name": "Morgan Lee",   "city": "Scottsdale, AZ",
        "segment": "Lapsed", "orders": 2,  "ltv": 198, "aov": 142,
        "last_order": "Oct 4, 2025",
        "skus": ["GL-001", "GL-007"],
        "categories": ["Sun"],
        "note": "Inactive 90+ days. Bought Sun frames twice. Re-engagement candidate.",
    },
    {
        "id": "C-010", "name": "Jamie Nguyen", "city": "Chicago, IL",
        "segment": "New",    "orders": 2,  "ltv": 386, "aov": 193,
        "last_order": "Apr 3, 2026",
        "skus": ["GL-002", "GL-010"],
        "categories": ["Optical", "Sun"],
        "note": "Two quick back-to-back orders in 5 days. High potential for VIP track.",
    },
]

SEG_COLORS = {
    "VIP": GOLD, "Repeat": GREEN, "New": BLUE,
    "At-Risk": RED, "Lapsed": MUTED,
}


# ═══════════════════════════════════════════════════════════════════════════════
# DATA GENERATORS
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
    brands = ["Ombraz", "Warby Parker", "Ray-Ban", "Oakley", "Maui Jim"]
    price_df = pd.DataFrame({
        "Brand": brands,
        "Avg Price ($)": [189, 145, 172, 158, 229],
        "Market Share (%)": [4.2, 8.7, 22.1, 14.3, 6.8],
        "Ad Spend Index": [38, 72, 100, 85, 55],
        "YoY Growth (%)": [18.4, 6.2, 3.1, 4.8, 7.9],
    })
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    search_df = pd.DataFrame({
        "Month": months,
        "Sun":       [35,42,58,74,88,95,98,90,72,50,38,32],
        "Optical":   [62,65,68,60,55,52,50,54,65,70,72,75],
        "Blue Light":[70,72,68,65,62,58,60,65,72,78,80,76],
    })
    releases_df = pd.DataFrame({
        "Brand":         ["Ray-Ban","Oakley","Warby Parker","Maui Jim","Ombraz"],
        "Product":       ["Meta Smart Glasses v3","Kato Prizm Trail",
                          "Barkley Titanium","Peahi Polarized","Ridgeline Carbon"],
        "Category":      ["Sun / Tech","Sport","Optical","Sun","Sun"],
        "Est. Ad Spend": ["$8.2M","$5.1M","$3.4M","$2.8M","$0.9M"],
        "Launch":        ["Feb 2026","Jan 2026","Mar 2026","Feb 2026","Apr 2026"],
        "Price":         ["$299","$189","$195","$279","$215"],
    })
    return {"price_df": price_df, "search_df": search_df,
            "releases_df": releases_df, "months": months}


def generate_customer_data(seed: int = 42) -> dict:
    order_statuses = {"Delivered":1842,"In Transit":387,"Processing":214,"Returned":93,"Cancelled":41}
    segments = pd.DataFrame({
        "Segment":      ["Repeat Buyers","First-Time","At-Risk","VIP (LTV >$500)","Lapsed 90d+"],
        "Count":        [1124,893,312,287,441],
        "Avg LTV ($)":  [342,189,210,687,156],
        "Avg Order ($)":[198,176,165,312,142],
    })
    regions = pd.DataFrame({
        "Region":           ["California","New York","Texas","Colorado","Florida",
                             "Washington","Oregon","Arizona","Nevada","Utah"],
        "Orders":           [487,312,241,198,167,143,128,97,84,71],
        "Avg Order ($)":    [214,228,187,242,195,231,219,178,203,256],
        "Return Rate (%)":  [4.1,3.8,5.2,2.9,4.7,3.1,3.4,5.8,4.2,2.7],
    })
    delivery_kpis = {
        "avg_delivery_days":3.4,"on_time_pct":91.2,
        "return_rate_pct":4.1,"csat_score":4.6,"repeat_purchase_rate":44.8,
    }
    weeks = [f"W{i}" for i in range(1,13)]
    order_vol = [320,298,345,412,389,427,455,481,443,468,502,519]
    return {"order_statuses":order_statuses,"segments":segments,
            "regions":regions,"delivery_kpis":delivery_kpis,
            "weeks":weeks,"order_vol":order_vol}


# ═══════════════════════════════════════════════════════════════════════════════
# SUPABASE + LOAD
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


@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    client = _supabase_client()
    if client:
        try:
            resp = client.table("sku_inventory").select("*").execute()
            if resp.data:
                df = pd.DataFrame(resp.data)
                drop = [c for c in ("id","created_at") if c in df.columns]
                return df.drop(columns=drop)
            df = generate_sku_data()
            try:
                client.table("sku_inventory").insert(df.to_dict(orient="records")).execute()
            except Exception:
                pass
            return df
        except Exception:
            pass
    return generate_sku_data()


# ═══════════════════════════════════════════════════════════════════════════════
# CORE LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

def apply_revenue_guard(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    threshold = 14  # lead_time(7) + safety_days(7)
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
        if hv and hm:      return "Push"
        if not hv and hm:  return "Bundle"
        if hv and not hm:  return "Monitor"
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
    return {"months":months,"historical":historical,"current":current,
            "offer_windows":offer_windows,"current_month":months[m]}


# ═══════════════════════════════════════════════════════════════════════════════
# GROQ AI AGENT
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
    counts = df["strategy"].value_counts().to_dict()
    return (
        f"SNAPSHOT {datetime.now().strftime('%Y-%m-%d')} | {len(df)} SKUs\n"
        f"Critical (DTZ<14): {df['is_critical'].sum()} | Risk: ${df['lost_revenue_risk'].sum():,.0f}\n"
        f"Push={counts.get('Push',0)} Bundle={counts.get('Bundle',0)} "
        f"Monitor={counts.get('Monitor',0)} Discount={counts.get('Discount',0)}\n\n"
        f"CRITICAL:\n{critical}\n\nTOP PUSH:\n{push}"
    )


def _mock_response(question: str, df: pd.DataFrame) -> str:
    q = question.lower()
    critical = df[df["is_critical"]]
    if any(w in q for w in ["stock","reorder","critical","run out"]):
        top = critical.nsmallest(3,"dtz")
        names = "; ".join(f"{r.sku_id} — {r.dtz:.0f}d" for _,r in top.iterrows())
        return f"{critical.shape[0]} SKUs need reorder. Urgent: {names}. Risk: ${critical['lost_revenue_risk'].sum():,.0f}."
    if any(w in q for w in ["discount","slow","liquidat"]):
        items = df[df["strategy"]=="Discount"].nsmallest(3,"daily_sales_velocity")
        return f"Discount: {', '.join(items['product_name'].tolist())}. Low velocity, thin margins — clear to free capital."
    if any(w in q for w in ["push","advertis","feature","ad"]):
        items = df[df["strategy"]=="Push"].nlargest(3,"profit_margin")
        return f"Push: {', '.join(items['product_name'].tolist())}. High velocity + strong margins."
    return (f"{len(df)} SKUs tracked. {df['is_critical'].sum()} need reorder. "
            f"{len(df[df['strategy']=='Push'])} ready to push. Ask about reorders, discounts, or ad spend.")


def get_agent_response(history: list, df: pd.DataFrame) -> str:
    try:
        from groq import Groq
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        system = (
            "You are a sharp inventory analyst for Ombraz, a premium eyewear brand. "
            "Be direct and specific. Reference SKU IDs. Max 3 sentences unless listing.\n\n"
            f"DATA:\n{_build_context(df)}"
        )
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":system}] + history,
            max_tokens=400, temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception:
        last_user = next((m["content"] for m in reversed(history) if m["role"]=="user"), "")
        return _mock_response(last_user, df)


# ═══════════════════════════════════════════════════════════════════════════════
# SHARED HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

PAGES = [
    ("overview",  "Overview",             icon_chart),
    ("trends",    "Trends + Competitors", icon_trending),
    ("products",  "Products",             icon_tag),
    ("customers", "Customer + Delivery",  icon_truck),
]

STRATEGY_COLORS = {"Push": GREEN, "Bundle": GOLD, "Monitor": BLUE, "Discount": RED}
CAT_ICONS  = {"Sun": icon_sun, "Optical": icon_glasses, "Blue Light": icon_monitor}
CAT_COLORS = {"Sun": GOLD, "Optical": BLUE, "Blue Light": GREEN}


def base_layout(height=300, margin=None) -> dict:
    m = margin or dict(l=8, r=12, t=8, b=8)
    return dict(
        paper_bgcolor=BG, plot_bgcolor=BG3,
        font=dict(color=TEXT, family="Montserrat, sans-serif", size=11),
        xaxis=dict(gridcolor="#252522", zerolinecolor=BORDER, tickfont=dict(size=10)),
        yaxis=dict(gridcolor="#252522", zerolinecolor=BORDER, tickfont=dict(size=10)),
        legend=dict(bgcolor=BG2, bordercolor=BORDER, borderwidth=1, font=dict(size=10)),
        margin=m, height=height,
    )


def strategy_badge(strategy: str) -> str:
    color = STRATEGY_COLORS.get(strategy, MUTED)
    bg = {"Push":"#0E2A1A","Bundle":"#1E1A0A","Monitor":"#0A1020","Discount":"#2A0E0E"}.get(strategy,"#222")
    return (f'<span style="background:{bg};color:{color};border:1px solid {color};'
            f'border-radius:4px;padding:2px 7px;font-size:0.65rem;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:0.08em;">{strategy}</span>')


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

def render_sidebar(df: pd.DataFrame) -> None:
    with st.sidebar:
        # ── Logo block ──────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="text-align:center;padding:26px 16px 16px;">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:2.4rem;
                        color:{TEXT};letter-spacing:0.14em;line-height:1;">OMBRAZ</div>
            <div style="font-family:'Montserrat',sans-serif;font-size:0.52rem;
                        color:{MUTED};letter-spacing:0.38em;text-transform:uppercase;
                        font-weight:300;margin-top:3px;">Armless · Sunglasses</div>
            <div style="font-size:0.55rem;color:#444440;letter-spacing:0.22em;
                        text-transform:uppercase;margin-top:10px;font-weight:500;
                        border-top:1px solid {BORDER};padding-top:8px;">
                AI Decision Agent</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f'<div style="border-bottom:1px solid {BORDER};margin:0 12px 12px;"></div>',
                    unsafe_allow_html=True)

        # ── Nav ────────────────────────────────────────────────────────────
        st.markdown(
            f'<div style="font-size:0.58rem;color:{MUTED};letter-spacing:0.18em;'
            f'text-transform:uppercase;padding:0 14px 6px;font-weight:600;">Navigation</div>',
            unsafe_allow_html=True,
        )

        current = st.session_state.get("page", "overview")
        for page_id, label, icon_fn in PAGES:
            is_active = current == page_id
            ic, btn = st.columns([0.18, 0.82], gap="small")
            with ic:
                st.markdown(
                    f'<div style="display:flex;align-items:center;height:34px;justify-content:center;">'
                    f'{icon_fn(14, GOLD if is_active else MUTED)}</div>',
                    unsafe_allow_html=True,
                )
            with btn:
                if st.button(label, key=f"nav_{page_id}", use_container_width=True,
                             type="primary" if is_active else "secondary"):
                    st.session_state["page"] = page_id
                    st.rerun()

        st.markdown(f'<div style="border-bottom:1px solid {BORDER};margin:10px 12px;"></div>',
                    unsafe_allow_html=True)

        # ── Live signals ───────────────────────────────────────────────────
        critical_n = int(df["is_critical"].sum())
        risk = df["lost_revenue_risk"].sum()
        push_n = int((df["strategy"] == "Push").sum())

        st.markdown(
            f'<div style="font-size:0.58rem;color:{MUTED};letter-spacing:0.18em;'
            f'text-transform:uppercase;padding:0 14px 6px;font-weight:600;">Live Signals</div>',
            unsafe_allow_html=True,
        )

        def stat_row(label, val, color):
            return (f'<div style="display:flex;justify-content:space-between;padding:5px 14px;">'
                    f'<span style="color:{MUTED};font-size:0.74rem;">{label}</span>'
                    f'<span style="color:{color};font-weight:700;font-size:0.74rem;">{val}</span></div>')

        st.markdown(
            stat_row("Critical SKUs", str(critical_n), RED) +
            stat_row("Revenue Risk", f"${risk:,.0f}", GOLD) +
            stat_row("Push Ready", f"{push_n} SKUs", GREEN),
            unsafe_allow_html=True,
        )

        st.markdown(f'<div style="border-bottom:1px solid {BORDER};margin:10px 12px;"></div>',
                    unsafe_allow_html=True)

        # ── AI Chat ────────────────────────────────────────────────────────
        st.markdown(
            f'<div style="font-size:0.58rem;color:{MUTED};letter-spacing:0.18em;'
            f'text-transform:uppercase;padding:0 14px 8px;font-weight:600;">AI Agent</div>',
            unsafe_allow_html=True,
        )

        if not st.session_state.get("messages"):
            st.session_state["messages"] = [{
                "role": "assistant",
                "content": (f"{critical_n} SKUs need reorder — ${risk:,.0f} at risk. "
                            "Ask me what to push, discount, or reorder."),
            }]

        # Scrollable chat history
        with st.container(height=220):
            for msg in st.session_state["messages"][-8:]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # Chat input — keep at sidebar level, not inside container
        try:
            if prompt := st.chat_input("Ask about inventory...", key="main_chat"):
                st.session_state["messages"].append({"role":"user","content":prompt})
                with st.spinner(""):
                    reply = get_agent_response(list(st.session_state["messages"]), df)
                st.session_state["messages"].append({"role":"assistant","content":reply})
                st.rerun()
        except Exception:
            pass  # Sidebar may be collapsed — chat input gracefully suppressed


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: EXECUTIVE OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════

def render_overview(df: pd.DataFrame) -> None:
    st.markdown(
        f'<div class="page-title">Executive Overview'
        f'<span class="page-sub">What needs attention right now</span></div>',
        unsafe_allow_html=True,
    )

    monthly_rev = (df["selling_price"] * df["daily_sales_velocity"] * 30).sum()
    aov = df["selling_price"].mean()
    healthy_pct = (~df["is_critical"]).sum() / len(df) * 100
    risk = df["lost_revenue_risk"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Est. Monthly Revenue", f"${monthly_rev:,.0f}", "30-day projection")
    c2.metric("Avg Selling Price", f"${aov:,.2f}", f"{len(df)} active SKUs")
    c3.metric("Stock Health", f"{healthy_pct:.1f}%",
              f"{int(df['is_critical'].sum())} critical", delta_color="inverse")
    c4.metric("Revenue at Risk", f"${risk:,.0f}", "if no reorders placed today", delta_color="inverse")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1.5], gap="large")

    with col_left:
        st.markdown(
            '<div class="sec-head">Which products will run out of stock — and cost you money</div>',
            unsafe_allow_html=True,
        )
        crit = (
            df[df["is_critical"]].sort_values("dtz")
            [["sku_id","product_name","category","current_stock","daily_sales_velocity","dtz","lost_revenue_risk"]].copy()
        )
        crit.columns = ["SKU","Product","Cat","Stock","Sales/Day","Days Left","$ Risk"]
        if crit.empty:
            st.success("All SKUs have 14+ days of stock. No action needed.")
        else:
            def _dtz_style(val):
                if val < 7:  return "background-color:#3D1515;color:#FF6B6B;font-weight:700"
                if val < 14: return "background-color:#2A1F0A;color:#FFA040"
                return ""
            st.dataframe(crit.style.map(_dtz_style, subset=["Days Left"]),
                         use_container_width=True, hide_index=True)

        st.markdown(
            f'<div class="legend-box">'
            f'<span style="color:{RED};font-weight:700;">Red = order today</span> (under 7 days of stock left)<br>'
            f'<span style="color:#FFA040;font-weight:700;">Orange = order this week</span> (7-14 days)<br>'
            f'"$ Risk" = estimated lost sales if you run out before restocking</div>',
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            '<div class="sec-head">Where to focus ad spend and which products to clear out</div>',
            unsafe_allow_html=True,
        )

        # Matrix chart
        vel_mid = df["daily_sales_velocity"].median()
        mar_mid = df["profit_margin"].median()
        fig = go.Figure()
        for strategy, color in STRATEGY_COLORS.items():
            sub = df[df["strategy"] == strategy]
            fig.add_trace(go.Scatter(
                x=sub["daily_sales_velocity"], y=sub["profit_margin"],
                mode="markers", name=strategy,
                marker=dict(size=10, color=color, opacity=0.88, line=dict(color=BG, width=1)),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>%{customdata[1]}<br>"
                    "Sales/Day: %{x:.1f} | Margin: %{y:.1%}<extra></extra>"
                ),
                customdata=sub[["sku_id","product_name"]].values,
            ))
        fig.add_vline(x=vel_mid, line_dash="dash", line_color="#3A3A36", line_width=1)
        fig.add_hline(y=mar_mid, line_dash="dash", line_color="#3A3A36", line_width=1)
        x_max, y_max = df["daily_sales_velocity"].max(), df["profit_margin"].max()
        for qx, qy, label, color in [
            (x_max*0.82, y_max*0.93, "PUSH",     GREEN),
            (x_max*0.08, y_max*0.93, "BUNDLE",   GOLD),
            (x_max*0.82, y_max*0.04, "MONITOR",  BLUE),
            (x_max*0.08, y_max*0.04, "DISCOUNT", RED),
        ]:
            fig.add_annotation(x=qx, y=qy, text=label, showarrow=False,
                               font=dict(color=color, size=9, family="Montserrat"), opacity=0.45)
        layout = base_layout(340)
        layout["xaxis"]["title"] = "Sales Velocity (units/day)"
        layout["yaxis"]["title"] = "Profit Margin"
        layout["yaxis"]["tickformat"] = ".0%"
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            f'<div class="legend-box">'
            f'<span style="font-weight:600;color:{TEXT};">How to read this chart:</span><br>'
            f'<div class="legend-row"><div class="legend-dot" style="background:{GREEN}"></div>'
            f'<span><b style="color:{GREEN}">Push</b> — sells fast, earns well. Advertise these now.</span></div>'
            f'<div class="legend-row"><div class="legend-dot" style="background:{GOLD}"></div>'
            f'<span><b style="color:{GOLD}">Bundle</b> — high margin but slow. Pair with best-sellers.</span></div>'
            f'<div class="legend-row"><div class="legend-dot" style="background:{BLUE}"></div>'
            f'<span><b style="color:{BLUE}">Monitor</b> — sells fast but thin margin. Watch cost structure.</span></div>'
            f'<div class="legend-row"><div class="legend-dot" style="background:{RED}"></div>'
            f'<span><b style="color:{RED}">Discount</b> — slow and low margin. Clear inventory now.</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        cols = st.columns(4)
        for col, (strategy, color) in zip(cols, STRATEGY_COLORS.items()):
            count = int((df["strategy"] == strategy).sum())
            col.markdown(
                f'<div style="text-align:center;background:{BG2};border-top:2px solid {color};'
                f'border-radius:8px;padding:9px 4px;margin-top:6px;">'
                f'<span style="color:{color};font-size:1.3rem;font-weight:800;">{count}</span><br>'
                f'<span style="color:{MUTED};font-size:0.62rem;text-transform:uppercase;'
                f'letter-spacing:0.12em;font-weight:600;">{strategy}</span></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="sec-head">Best months to launch promotions — based on historical demand peaks</div>',
                unsafe_allow_html=True)
    data = analyze_seasonality(df)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=data["months"], y=data["historical"], name="Historical Average",
                              line=dict(color="#444440", width=1.5, dash="dot")))
    fig2.add_trace(go.Scatter(x=data["months"], y=data["current"], name="Current Trend",
                              line=dict(color=GOLD, width=2),
                              fill="tonexty", fillcolor=rgba(GOLD, 0.06)))
    for month in data["offer_windows"]:
        idx = data["months"].index(month)
        fig2.add_vrect(x0=idx-0.45, x1=idx+0.45, fillcolor=rgba(GREEN,0.10),
                       layer="below", line_width=0,
                       annotation_text="Promo Window",
                       annotation_font=dict(color=GREEN, size=8))
    cur_idx = data["months"].index(data["current_month"])
    fig2.add_vline(x=cur_idx, line_dash="solid", line_color=BLUE, line_width=1.5,
                  annotation_text=f"Today ({data['current_month']})",
                  annotation_font=dict(color=BLUE, size=9))
    layout2 = base_layout(250)
    layout2["yaxis"]["title"] = "Avg Daily Sales"
    fig2.update_layout(**layout2)
    st.plotly_chart(fig2, use_container_width=True)

    if data["offer_windows"]:
        st.markdown(
            f'<div class="callout-green"><span style="color:{GREEN};font-weight:700;">'
            f'Launch promotions in: {", ".join(data["offer_windows"])}</span> — '
            f'activate bundles or ads 7-14 days before these months peak.</div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: TRENDS + COMPETITORS
# ═══════════════════════════════════════════════════════════════════════════════

def render_trends() -> None:
    st.markdown(
        f'<div class="page-title">Trends + Competitors'
        f'<span class="page-sub">Are we priced right and is demand growing?</span></div>',
        unsafe_allow_html=True,
    )
    data = generate_competitor_data()
    price_df = data["price_df"]
    search_df = data["search_df"]

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="sec-head">How our price compares to competitors</div>',
                    unsafe_allow_html=True)
        bar_colors = [GOLD if b == "Ombraz" else "#2E2E2A" for b in price_df["Brand"]]
        fig = go.Figure(go.Bar(
            x=price_df["Brand"], y=price_df["Avg Price ($)"],
            marker_color=bar_colors,
            marker_line=dict(color=[GOLD if b=="Ombraz" else "#3A3A36" for b in price_df["Brand"]], width=1),
            text=[f"${p}" for p in price_df["Avg Price ($)"]],
            textposition="outside", textfont=dict(color=TEXT, size=11),
        ))
        layout = base_layout(280)
        layout["yaxis"]["range"] = [0, 280]
        layout["showlegend"] = False
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            f'<div class="callout-gold"><span style="color:{GOLD};font-weight:700;">Position: </span>'
            f'Ombraz at $189 is 10% above Ray-Ban ($172) and 17% below Maui Jim ($229). '
            f'Premium-adjacent — defensible with DTC margin advantage.</div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown('<div class="sec-head">Competitor snapshot — growth and market share</div>',
                    unsafe_allow_html=True)
        for _, row in price_df.iterrows():
            is_o = row["Brand"] == "Ombraz"
            gc = GREEN if row["YoY Growth (%)"] > 10 else (GOLD if row["YoY Growth (%)"] > 5 else MUTED)
            st.markdown(
                f'<div style="background:{BG2};border:1px solid {"#3A3028" if is_o else BORDER};'
                f'{"border-top:2px solid "+GOLD+";" if is_o else ""}'
                f'border-radius:8px;padding:10px 14px;margin-bottom:7px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'<div><span style="color:{GOLD if is_o else TEXT};font-weight:{"700" if is_o else "500"};'
                f'font-size:0.85rem;">{row["Brand"]}</span>'
                f'<span style="color:{MUTED};font-size:0.7rem;margin-left:8px;">{row["Market Share (%)"]}% share</span></div>'
                f'<div style="text-align:right;">'
                f'<span style="color:{TEXT};font-weight:700;font-size:0.88rem;">${row["Avg Price ($)"]}</span>'
                f'<span style="color:{gc};font-size:0.72rem;margin-left:10px;font-weight:600;">+{row["YoY Growth (%)"]}% YoY</span>'
                f'</div></div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    col3, col4 = st.columns([1.6, 1], gap="large")

    with col3:
        st.markdown('<div class="sec-head">What customers are searching — by frame category over 12 months</div>',
                    unsafe_allow_html=True)
        trend_colors = {"Sun": GOLD, "Optical": BLUE, "Blue Light": GREEN}
        trend_fills  = {"Sun": rgba(GOLD,0.07), "Optical": rgba(BLUE,0.07), "Blue Light": rgba(GREEN,0.07)}
        fig2 = go.Figure()
        for cat, color in trend_colors.items():
            fig2.add_trace(go.Scatter(
                x=search_df["Month"], y=search_df[cat],
                name=cat, line=dict(color=color, width=2),
                fill="tozeroy", fillcolor=trend_fills[cat],
            ))
        cur_m = datetime.now().strftime("%b")
        if cur_m in list(search_df["Month"]):
            cur_idx = list(search_df["Month"]).index(cur_m)
            fig2.add_vline(x=cur_idx, line_dash="solid", line_color=MUTED, line_width=1,
                          annotation_text="Today", annotation_font=dict(color=MUTED, size=9))
        layout2 = base_layout(280)
        layout2["yaxis"]["title"] = "Search Index (100 = peak)"
        fig2.update_layout(**layout2)
        st.plotly_chart(fig2, use_container_width=True)

    with col4:
        st.markdown('<div class="sec-head">Who is spending on ads — relative comparison</div>',
                    unsafe_allow_html=True)
        spend_df = price_df.sort_values("Ad Spend Index", ascending=True)
        fig3 = go.Figure(go.Bar(
            x=spend_df["Ad Spend Index"], y=spend_df["Brand"],
            orientation="h",
            marker_color=[GOLD if b=="Ombraz" else "#2E2E2A" for b in spend_df["Brand"]],
            text=spend_df["Ad Spend Index"], textposition="outside",
            textfont=dict(color=TEXT, size=10),
        ))
        layout3 = base_layout(280)
        layout3["xaxis"]["title"] = "Ad Spend (Ray-Ban = 100)"
        layout3["xaxis"]["range"] = [0, 120]
        layout3["showlegend"] = False
        fig3.update_layout(**layout3)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sec-head">New product launches and campaigns to watch</div>',
                unsafe_allow_html=True)

    def highlight_ombraz(row):
        if row["Brand"] == "Ombraz":
            return [f"background-color:#1E1A0A;color:{GOLD}"] * len(row)
        return [""] * len(row)

    st.dataframe(data["releases_df"].style.apply(highlight_ombraz, axis=1),
                 use_container_width=True, hide_index=True)
    st.markdown(
        f'<div class="callout-red"><span style="color:{RED};font-weight:700;">Watch: </span>'
        f'Ray-Ban Meta v3 and Oakley Kato are commanding the largest budgets in Q2. '
        f'Ombraz Ridgeline Carbon launched April 2026 with 9x less spend — '
        f'organic and influencer channels are the lever.</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PRODUCTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_products(df: pd.DataFrame) -> None:
    st.markdown(
        f'<div class="page-title">Products'
        f'<span class="page-sub">Click a category to drill into its SKUs and customers</span></div>',
        unsafe_allow_html=True,
    )

    # ── Category cards (clickable filter) ─────────────────────────────────
    st.markdown('<div class="sec-head">Category breakdown — click any card to filter below</div>',
                unsafe_allow_html=True)

    selected_cat = st.session_state.get("product_cat_filter", "All")
    cat_cols = st.columns(4, gap="medium")

    # "All" card
    with cat_cols[0]:
        all_active = selected_cat == "All"
        border = f"border-top:2px solid {TEXT};" if all_active else ""
        if st.button("All Categories", key="cat_all", use_container_width=True,
                     type="primary" if all_active else "secondary"):
            st.session_state["product_cat_filter"] = "All"
            st.rerun()
        # Override label since button is above
        st.markdown(
            f'<div style="background:{BG2};{border}border:1px solid {BORDER};'
            f'border-radius:8px;padding:10px;text-align:center;margin-top:-8px;">'
            f'<div style="color:{TEXT};font-size:1.1rem;font-weight:800;">{len(df)}</div>'
            f'<div style="color:{MUTED};font-size:0.68rem;">total SKUs</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    for col, cat in zip(cat_cols[1:], ["Sun", "Optical", "Blue Light"]):
        sub = df[df["category"] == cat]
        monthly = (sub["selling_price"] * sub["daily_sales_velocity"] * 30).sum()
        avg_margin = sub["profit_margin"].mean()
        critical_n = int(sub["is_critical"].sum())
        push_n = int((sub["strategy"] == "Push").sum())
        color = CAT_COLORS[cat]
        icon_svg = CAT_ICONS[cat](24, color)
        is_active = selected_cat == cat
        border_top = f"border-top:2px solid {color};" if is_active else f"border-top:2px solid transparent;"

        with col:
            if st.button(cat, key=f"cat_{cat}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                if selected_cat == cat:
                    st.session_state["product_cat_filter"] = "All"
                else:
                    st.session_state["product_cat_filter"] = cat
                st.rerun()

            st.markdown(
                f'<div style="background:{BG2};{border_top}border:1px solid {color+"33"};'
                f'border-radius:8px;padding:10px 12px;margin-top:-8px;">'
                f'<div style="margin-bottom:6px;">{icon_svg}</div>'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:4px;">'
                f'<span style="color:{MUTED};font-size:0.72rem;">Monthly Rev</span>'
                f'<span style="color:{TEXT};font-size:0.72rem;font-weight:600;">${monthly:,.0f}</span></div>'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:4px;">'
                f'<span style="color:{MUTED};font-size:0.72rem;">Avg Margin</span>'
                f'<span style="color:{color};font-size:0.72rem;font-weight:700;">{avg_margin:.1%}</span></div>'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:4px;">'
                f'<span style="color:{MUTED};font-size:0.72rem;">Critical</span>'
                f'<span style="color:{RED if critical_n>0 else GREEN};font-size:0.72rem;font-weight:700;">{critical_n}</span></div>'
                f'<div style="display:flex;justify-content:space-between;">'
                f'<span style="color:{MUTED};font-size:0.72rem;">Push Ready</span>'
                f'<span style="color:{GREEN};font-size:0.72rem;font-weight:700;">{push_n}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── SKU Detail Table ───────────────────────────────────────────────────
    filtered = df if selected_cat == "All" else df[df["category"] == selected_cat]
    filter_label = selected_cat if selected_cat != "All" else "All Categories"
    st.markdown(
        f'<div class="sec-head">Individual SKUs — {filter_label} '
        f'({len(filtered)} products, sorted by sales velocity)</div>',
        unsafe_allow_html=True,
    )

    sku_display = (
        filtered.sort_values("daily_sales_velocity", ascending=False)
        [["sku_id","product_name","category","current_stock","daily_sales_velocity",
          "selling_price","profit_margin","dtz","lost_revenue_risk","strategy"]]
        .copy()
    )
    sku_display.columns = ["SKU","Product","Category","Stock","Sales/Day",
                           "Price ($)","Margin","Days Left","$ Risk","Strategy"]
    sku_display["Price ($)"] = sku_display["Price ($)"].apply(lambda x: f"${x:.0f}")
    sku_display["Margin"] = sku_display["Margin"].apply(lambda x: f"{x:.1%}")
    sku_display["Days Left"] = sku_display["Days Left"].round(1)
    sku_display["$ Risk"] = sku_display["$ Risk"].apply(lambda x: f"${x:,.0f}" if x > 0 else "—")

    def _style_sku(row):
        styles = [""] * len(row)
        dtl_idx = list(sku_display.columns).index("Days Left")
        strat_idx = list(sku_display.columns).index("Strategy")
        try:
            dtl = float(str(row["Days Left"]).replace("$","").replace(",",""))
            if dtl < 7:   styles[dtl_idx] = "background-color:#3D1515;color:#FF6B6B;font-weight:700"
            elif dtl < 14: styles[dtl_idx] = "background-color:#2A1F0A;color:#FFA040"
        except Exception:
            pass
        strat = row["Strategy"]
        sc = {"Push":"#0E2A1A","Bundle":"#1E1A0A","Monitor":"#0A1020","Discount":"#2A0E0E"}.get(strat,"")
        tc = STRATEGY_COLORS.get(strat, TEXT)
        if sc:
            styles[strat_idx] = f"background-color:{sc};color:{tc};font-weight:700"
        return styles

    st.dataframe(sku_display.style.apply(_style_sku, axis=1),
                 use_container_width=True, hide_index=True, height=280)

    # ── Customers who bought this category ─────────────────────────────────
    if selected_cat != "All":
        relevant_customers = [c for c in TEST_CUSTOMERS if selected_cat in c["categories"]]
        if relevant_customers:
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            st.markdown(
                f'<div class="sec-head">Customers who have ordered from {selected_cat} — '
                f'{len(relevant_customers)} accounts</div>',
                unsafe_allow_html=True,
            )
            for c in relevant_customers:
                seg_color = SEG_COLORS.get(c["segment"], MUTED)
                purchased_here = [s for s in c["skus"] if s in list(filtered["sku_id"])]
                products_str = ", ".join(purchased_here) if purchased_here else "products in other SKU range"
                st.markdown(
                    f'<div class="cust-row" style="display:flex;justify-content:space-between;align-items:flex-start;">'
                    f'<div style="flex:1;">'
                    f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">'
                    f'<span style="color:{TEXT};font-weight:700;font-size:0.88rem;">{c["name"]}</span>'
                    f'<span style="background:{seg_color}22;color:{seg_color};border:1px solid {seg_color}44;'
                    f'border-radius:4px;padding:1px 7px;font-size:0.64rem;font-weight:700;'
                    f'text-transform:uppercase;letter-spacing:0.06em;">{c["segment"]}</span>'
                    f'<span style="color:{MUTED};font-size:0.74rem;">{c["city"]}</span>'
                    f'</div>'
                    f'<div style="color:{MUTED};font-size:0.76rem;">'
                    f'SKUs purchased: <span style="color:{TEXT};">{products_str}</span> &nbsp;·&nbsp; '
                    f'{c["note"]}</div>'
                    f'</div>'
                    f'<div style="text-align:right;min-width:120px;">'
                    f'<div style="color:{GOLD};font-weight:800;font-size:0.95rem;">${c["ltv"]:,}</div>'
                    f'<div style="color:{MUTED};font-size:0.68rem;">lifetime value</div>'
                    f'<div style="color:{MUTED};font-size:0.7rem;margin-top:2px;">Last: {c["last_order"]}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        # Velocity toggle + chart
        st.markdown('<div class="sec-head">Which products sell fastest — choose your view window</div>',
                    unsafe_allow_html=True)
        period = st.radio("Period", ["Daily","Weekly","Monthly"],
                          horizontal=True, key="vel_period", label_visibility="collapsed")
        mult = {"Daily":1,"Weekly":7,"Monthly":30}[period]
        unit = {"Daily":"/day","Weekly":"/wk","Monthly":"/mo"}[period]
        top20 = filtered.nlargest(15, "daily_sales_velocity").copy()
        top20["display_vel"] = (top20["daily_sales_velocity"] * mult).round(0)
        bar_colors = [STRATEGY_COLORS.get(s, MUTED) for s in top20["strategy"]]
        fig4 = go.Figure(go.Bar(
            x=top20["display_vel"],
            y=top20["product_name"].str[:26],
            orientation="h", marker_color=bar_colors,
            text=[f'{int(v)}{unit}' for v in top20["display_vel"]],
            textposition="outside", textfont=dict(color=MUTED, size=9),
        ))
        layout4 = base_layout(380, margin=dict(l=8, r=60, t=8, b=8))
        layout4["xaxis"]["title"] = f"Units Sold ({unit})"
        layout4["yaxis"]["autorange"] = "reversed"
        layout4["yaxis"]["tickfont"] = dict(size=9)
        layout4["showlegend"] = False
        fig4.update_layout(**layout4)
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown(
            f'<div class="legend-box">Bar color = strategy: '
            f'<span style="color:{GREEN};font-weight:600;">Push</span> / '
            f'<span style="color:{GOLD};font-weight:600;">Bundle</span> / '
            f'<span style="color:{BLUE};font-weight:600;">Monitor</span> / '
            f'<span style="color:{RED};font-weight:600;">Discount</span></div>',
            unsafe_allow_html=True,
        )

    with col_right:
        # Reorder planner
        st.markdown('<div class="sec-head">Products that need to be reordered now — with cost estimate</div>',
                    unsafe_allow_html=True)
        reorder = (
            filtered[filtered["is_critical"]].sort_values("dtz")
            [["sku_id","product_name","category","current_stock","daily_sales_velocity","dtz","selling_price"]].copy()
        )
        if reorder.empty:
            st.markdown(
                f'<div class="callout-green"><span style="color:{GREEN};font-weight:700;">All clear</span>'
                f' — no reorders needed in this category right now.</div>',
                unsafe_allow_html=True,
            )
        else:
            reorder["Suggest Qty"] = (
                reorder["daily_sales_velocity"] * 30 - reorder["current_stock"]
            ).clip(lower=0).astype(int)
            reorder["Est Cost ($)"] = (reorder["Suggest Qty"] * reorder["selling_price"] * 0.42).round(0).astype(int)
            display = reorder[["sku_id","product_name","category","dtz","Suggest Qty","Est Cost ($)"]].copy()
            display.columns = ["SKU","Product","Cat","Days Left","Qty to Order","Est Cost ($)"]
            display["Days Left"] = display["Days Left"].round(1)

            def _reorder_style(val):
                if val < 7:  return "background-color:#3D1515;color:#FF6B6B;font-weight:700"
                if val < 14: return "background-color:#2A1F0A;color:#FFA040"
                return ""

            st.dataframe(display.style.map(_reorder_style, subset=["Days Left"]),
                         use_container_width=True, hide_index=True)

            total_cost = int(reorder["Est Cost ($)"].sum())
            st.markdown(
                f'<div class="callout-gold"><span style="color:{GOLD};font-weight:700;">Estimated reorder: </span>'
                f'${total_cost:,.0f} restores 30-day coverage across {len(reorder)} SKUs.</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="legend-box">'
                f'"Days Left" = current stock ÷ daily sales rate<br>'
                f'"Qty to Order" = units needed to reach 30 days of stock<br>'
                f'"Est Cost" = order qty × selling price × 42% (assumed landed cost)</div>',
                unsafe_allow_html=True,
            )

        # Margin distribution
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec-head">Profit margin spread — how much you keep per unit sold</div>',
                    unsafe_allow_html=True)
        fig5 = go.Figure()
        for cat, color in CAT_COLORS.items():
            sub = filtered[filtered["category"] == cat] if selected_cat == "All" else filtered
            if len(sub) > 0:
                fig5.add_trace(go.Histogram(
                    x=sub["profit_margin"], name=cat if selected_cat=="All" else selected_cat,
                    nbinsx=10, marker_color=color, opacity=0.72,
                ))
            if selected_cat != "All":
                break  # only one category
        layout5 = base_layout(220)
        layout5["xaxis"]["title"] = "Profit Margin %"
        layout5["xaxis"]["tickformat"] = ".0%"
        layout5["yaxis"]["title"] = "Number of SKUs"
        layout5["barmode"] = "overlay"
        layout5["showlegend"] = selected_cat == "All"
        fig5.update_layout(**layout5)
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown(
            f'<div class="legend-box">'
            f'Each bar = SKUs earning within that margin range. '
            f'Healthy DTC target: <span style="color:{GREEN};font-weight:600;">40%+</span>. '
            f'Below 30% means pricing pressure or high landed cost — review those SKUs.</div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: CUSTOMER + DELIVERY
# ═══════════════════════════════════════════════════════════════════════════════

def render_customers() -> None:
    st.markdown(
        f'<div class="page-title">Customer + Delivery'
        f'<span class="page-sub">Who is buying and how well are we fulfilling</span></div>',
        unsafe_allow_html=True,
    )

    cdata = generate_customer_data()
    kpis = cdata["delivery_kpis"]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Avg Delivery",    f"{kpis['avg_delivery_days']}d",    "Target: 3.0d", delta_color="inverse")
    c2.metric("On-Time Rate",    f"{kpis['on_time_pct']}%",          "+1.4% vs last qtr")
    c3.metric("Return Rate",     f"{kpis['return_rate_pct']}%",      "-0.3% vs last qtr")
    c4.metric("CSAT",            f"{kpis['csat_score']} / 5",        "1,842 reviews")
    c5.metric("Repeat Purchase", f"{kpis['repeat_purchase_rate']}%", "+3.1% vs last qtr")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="sec-head">Where orders are in the pipeline right now</div>',
                    unsafe_allow_html=True)
        statuses = cdata["order_statuses"]
        status_colors = {
            "Delivered":GREEN,"In Transit":BLUE,"Processing":GOLD,"Returned":RED,"Cancelled":"#664444",
        }
        total_orders = sum(statuses.values())
        fig1 = go.Figure(go.Pie(
            labels=list(statuses.keys()), values=list(statuses.values()),
            hole=0.58,
            marker_colors=[status_colors.get(s, MUTED) for s in statuses.keys()],
            textinfo="label+percent", textfont=dict(color=TEXT, size=10),
        ))
        fig1.update_layout(
            paper_bgcolor=BG, font=dict(color=TEXT, family="Montserrat, sans-serif"),
            margin=dict(l=8,r=8,t=8,b=8), height=270, showlegend=False,
            annotations=[dict(text=f"<b>{total_orders:,}</b><br>Orders",
                             x=0.5, y=0.5, font_size=13, font_color=TEXT, showarrow=False)],
        )
        st.plotly_chart(fig1, use_container_width=True)
        for status, count in statuses.items():
            pct = count / total_orders * 100
            color = status_colors.get(status, MUTED)
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;padding:4px 8px;margin:1px 0;">'
                f'<span style="color:{color};font-size:0.79rem;font-weight:500;">{status}</span>'
                f'<span style="color:{MUTED};font-size:0.75rem;">{count:,} &nbsp;'
                f'<span style="color:{TEXT};font-weight:600;">{pct:.1f}%</span></span></div>',
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown('<div class="sec-head">How customers segment — to decide where to invest retention spend</div>',
                    unsafe_allow_html=True)
        segs = cdata["segments"]
        fig2 = go.Figure(go.Bar(
            x=segs["Segment"], y=segs["Count"],
            marker_color=[GREEN,BLUE,RED,GOLD,MUTED],
            text=segs["Count"], textposition="outside", textfont=dict(color=TEXT, size=10),
        ))
        layout2 = base_layout(230)
        layout2["yaxis"]["title"] = "Customers"
        layout2["showlegend"] = False
        fig2.update_layout(**layout2)
        st.plotly_chart(fig2, use_container_width=True)

        vip_row = segs[segs["Segment"]=="VIP (LTV >$500)"]
        vip_count = int(vip_row["Count"].iloc[0]) if not vip_row.empty else 287
        vip_ltv   = int(vip_row["Avg LTV ($)"].iloc[0]) if not vip_row.empty else 687
        at_risk_row = segs[segs["Segment"]=="At-Risk"]
        at_risk_count = int(at_risk_row["Count"].iloc[0]) if not at_risk_row.empty else 312

        st.markdown(
            f'<div class="callout-gold"><span style="color:{GOLD};font-weight:700;">VIP opportunity: </span>'
            f'{vip_count} customers with avg LTV ${vip_ltv} drive outsized revenue. '
            f'Prioritize for early access and loyalty programs.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="callout-red"><span style="color:{RED};font-weight:700;">At-Risk: </span>'
            f'{at_risk_count} customers show declining purchase frequency. '
            f'A win-back campaign with a 15% offer could recover 20-30% of them.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    col3, col4 = st.columns([1, 1.2], gap="large")

    with col3:
        st.markdown('<div class="sec-head">Top regions by order volume — where our customers are</div>',
                    unsafe_allow_html=True)
        regions = cdata["regions"]

        def highlight_top(row):
            if row["Orders"] == regions["Orders"].max():
                return [f"background-color:#1E1A0A;color:{GOLD}"] * len(row)
            return [""] * len(row)

        st.dataframe(regions.style.apply(highlight_top, axis=1),
                     use_container_width=True, hide_index=True)
        ca_aov = int(regions[regions["Region"]=="California"]["Avg Order ($)"].iloc[0])
        st.markdown(
            f'<div class="callout-green"><span style="color:{GREEN};font-weight:700;">Top market: </span>'
            f'California — 487 orders, ${ca_aov} avg order. Colorado has lowest return rate at 2.9%.</div>',
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown('<div class="sec-head">Order volume over 12 weeks — is momentum growing?</div>',
                    unsafe_allow_html=True)
        weeks = cdata["weeks"]
        order_vol = cdata["order_vol"]
        z = np.polyfit(range(len(order_vol)), order_vol, 1)
        p = np.poly1d(z)
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=weeks, y=order_vol,
            line=dict(color=GOLD, width=2),
            fill="tozeroy", fillcolor=rgba(GOLD,0.07),
            mode="lines+markers", marker=dict(color=GOLD, size=5), name="Orders",
        ))
        fig3.add_trace(go.Scatter(
            x=weeks, y=[p(i) for i in range(len(weeks))],
            line=dict(color=GREEN, width=1.5, dash="dash"), showlegend=False,
        ))
        layout3 = base_layout(240)
        layout3["yaxis"]["title"] = "Orders"
        layout3["showlegend"] = False
        fig3.update_layout(**layout3)
        st.plotly_chart(fig3, use_container_width=True)

        wow = (order_vol[-1] - order_vol[-2]) / order_vol[-2] * 100
        total_12w = sum(order_vol)
        st.markdown(
            f'<div style="display:flex;gap:12px;margin-top:4px;">'
            f'<div style="background:{BG2};border-top:2px solid {GREEN};border:1px solid {GREEN}22;'
            f'border-radius:8px;padding:11px;flex:1;text-align:center;">'
            f'<div style="color:{GREEN};font-size:1.15rem;font-weight:800;">+{wow:.1f}%</div>'
            f'<div style="color:{MUTED};font-size:0.62rem;text-transform:uppercase;'
            f'letter-spacing:0.1em;font-weight:600;margin-top:2px;">WoW Growth</div></div>'
            f'<div style="background:{BG2};border:1px solid {BORDER};'
            f'border-radius:8px;padding:11px;flex:1;text-align:center;">'
            f'<div style="color:{TEXT};font-size:1.15rem;font-weight:800;">{total_12w:,}</div>'
            f'<div style="color:{MUTED};font-size:0.62rem;text-transform:uppercase;'
            f'letter-spacing:0.1em;font-weight:600;margin-top:2px;">12-Week Total</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Test Customer Profiles ─────────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="sec-head">Test customer accounts — real profiles to reference in demos and decisions</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="callout-blue" style="margin-bottom:12px;">'
        f'<span style="color:{BLUE};font-weight:700;">10 test accounts</span> with purchase history, '
        f'segments, and SKU cross-references. Click into the Products page with a category selected '
        f'to see which of these customers bought from that category.</div>',
        unsafe_allow_html=True,
    )

    for c in TEST_CUSTOMERS:
        seg_color = SEG_COLORS.get(c["segment"], MUTED)
        skus_str = ", ".join(c["skus"])
        cats_str = " · ".join(c["categories"])
        st.markdown(
            f'<div style="background:{BG2};border:1px solid {BORDER};border-left:3px solid {seg_color};'
            f'border-radius:8px;padding:12px 16px;margin-bottom:7px;">'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
            f'<div style="flex:1;">'
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:5px;">'
            f'<span style="color:{TEXT};font-weight:700;font-size:0.9rem;">{c["name"]}</span>'
            f'<span style="background:{seg_color}1A;color:{seg_color};border:1px solid {seg_color}44;'
            f'border-radius:4px;padding:1px 8px;font-size:0.63rem;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:0.06em;">{c["segment"]}</span>'
            f'<span style="color:{MUTED};font-size:0.74rem;">{c["city"]}</span>'
            f'<span style="color:#3A3A36;font-size:0.7rem;">{c["id"]}</span>'
            f'</div>'
            f'<div style="color:{MUTED};font-size:0.76rem;margin-bottom:4px;">'
            f'Categories: <span style="color:{TEXT};">{cats_str}</span> &nbsp;·&nbsp; '
            f'SKUs: <span style="color:{TEXT};">{skus_str}</span></div>'
            f'<div style="color:{MUTED};font-size:0.75rem;">{c["note"]}</div>'
            f'</div>'
            f'<div style="text-align:right;min-width:130px;padding-left:16px;">'
            f'<div style="color:{GOLD};font-weight:800;font-size:1.05rem;">${c["ltv"]:,}</div>'
            f'<div style="color:{MUTED};font-size:0.66rem;margin-bottom:6px;">lifetime value</div>'
            f'<div style="display:flex;gap:8px;justify-content:flex-end;">'
            f'<div style="text-align:center;">'
            f'<div style="color:{TEXT};font-weight:700;font-size:0.82rem;">{c["orders"]}</div>'
            f'<div style="color:{MUTED};font-size:0.62rem;">orders</div></div>'
            f'<div style="text-align:center;">'
            f'<div style="color:{TEXT};font-weight:700;font-size:0.82rem;">${c["aov"]}</div>'
            f'<div style="color:{MUTED};font-size:0.62rem;">avg order</div></div>'
            f'</div>'
            f'<div style="color:{MUTED};font-size:0.68rem;margin-top:6px;">Last: {c["last_order"]}</div>'
            f'</div></div></div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    # Initialize all session state upfront — prevents stale state on sidebar collapse/expand
    st.session_state.setdefault("page", "overview")
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("product_cat_filter", "All")

    df = load_data()
    df = apply_revenue_guard(df)
    df = apply_sku_matrix(df)

    render_sidebar(df)

    page = st.session_state["page"]

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

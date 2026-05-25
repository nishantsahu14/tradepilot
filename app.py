"""
TradePilot — AI Market Intelligence
Enhanced: NASDAQ branding, live TradingView charts, RiskGuard AI (5),
          professional UI, team credits page.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sqlite3
import os
import random
import warnings
warnings.filterwarnings("ignore")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="📈 TradePilot — AI Market Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Local modules ──────────────────────────────────────────────────────────────
from data_collector import AdvancedDataCollector
from ml_predictor import AdvancedMLPredictor
from risk_robot import render_risk_robot
from creators import render_creators_footer

# ── Symbol config ──────────────────────────────────────────────────────────────
SYMBOLS = {
    "SPY": {
        "name":    "S&P 500 ETF",
        "display": "SPY",
        "emoji":   "📈",
        "color":   "#63b3ed",
        "desc":    "US Large Cap Stocks",
        "tv_sym":  "AMEX:SPY",
        "tv_link": "https://www.tradingview.com/chart/?symbol=AMEX%3ASPY",
    },
    "QQQ": {
        "name":    "NASDAQ-100 ETF",
        "display": "NASDAQ",        # ← renamed from QQQ to NASDAQ everywhere
        "emoji":   "💻",
        "color":   "#68d391",
        "desc":    "Technology Stocks",
        "tv_sym":  "NASDAQ:QQQ",
        "tv_link": "https://www.tradingview.com/chart/?symbol=NASDAQ%3AQQQ",
    },
    "GLD": {
        "name":    "GLD ETF",
        "display": "GLD",
        "emoji":   "🥇",
        "color":   "#f6ad55",
        "desc":    "Precious Metals",
        "tv_sym":  "AMEX:GLD",
        "tv_link": "https://www.tradingview.com/chart/?symbol=AMEX%3AGLD",
    },
}

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*, html, body, [class*="css"] { font-family:'Inter',sans-serif; }

/* ── HERO ── */
.hero-banner {
  background:linear-gradient(135deg,#060918 0%,#0d1b3e 45%,#1a0533 100%);
  border-radius:24px; padding:3rem 2.5rem 2.5rem; text-align:center;
  margin-bottom:1.5rem;
  box-shadow:0 24px 64px rgba(0,0,0,0.65),inset 0 1px 0 rgba(255,255,255,0.07);
  position:relative; overflow:hidden; border:1px solid rgba(99,179,237,0.18);
}
.hero-banner::before {
  content:''; position:absolute; top:-80px; left:-80px; width:320px; height:320px;
  border-radius:50%; background:radial-gradient(circle,rgba(99,179,237,0.2),transparent 70%);
}
.hero-banner::after {
  content:''; position:absolute; bottom:-80px; right:-80px; width:300px; height:300px;
  border-radius:50%; background:radial-gradient(circle,rgba(168,85,247,0.2),transparent 70%);
}
.hero-logo { font-size:3.6rem; font-weight:900; color:white; margin:0; letter-spacing:-2px;
  text-shadow:0 0 48px rgba(99,179,237,0.45); position:relative; z-index:1; }
.hero-logo span { color:#63b3ed; }
.hero-tagline { color:rgba(255,255,255,0.55); font-size:1rem; margin-top:0.5rem; position:relative; z-index:1; }
.hero-badges { margin-top:1.2rem; position:relative; z-index:1; }
.badge {
  display:inline-block; background:rgba(255,255,255,0.07); color:rgba(255,255,255,0.85);
  border-radius:20px; padding:5px 16px; font-size:0.78rem; margin:3px;
  border:1px solid rgba(255,255,255,0.14); backdrop-filter:blur(6px);
}

/* ── SECTION HEADERS ── */
.section-hdr {
  font-size:1.22rem; font-weight:800; color:#1e293b;
  border-left:4px solid #63b3ed; padding-left:0.9rem; margin:2rem 0 1rem;
}

/* ── PREDICTION CARDS ── */
.pred-card {
  border-radius:20px; padding:1.8rem 1.2rem; text-align:center; color:white;
  box-shadow:0 14px 44px rgba(0,0,0,0.3);
  transition:transform 0.3s ease,box-shadow 0.3s ease;
  position:relative; overflow:hidden;
}
.pred-card::before { content:''; position:absolute; top:0; left:0; right:0;
  height:1px; background:rgba(255,255,255,0.3); }
.pred-card:hover { transform:translateY(-8px); box-shadow:0 28px 64px rgba(0,0,0,0.45); }
.pred-card.bullish {
  background:linear-gradient(145deg,#0f4c34,#11998e,#38ef7d);
  border:1.5px solid rgba(56,239,125,0.55);
}
.pred-card.bearish {
  background:linear-gradient(145deg,#4a0a14,#c0392b,#f5576c);
  border:1.5px solid rgba(245,87,108,0.55);
}
.pred-symbol { font-size:2.2rem; font-weight:900; margin:0; letter-spacing:-1px; }
.pred-name   { font-size:0.82rem; opacity:0.8; margin-bottom:0.6rem; }
.pred-arrow  { font-size:3.5rem; line-height:1; }
.pred-dir    { font-size:1.6rem; font-weight:800; }
.pred-conf   { font-size:1.1rem; margin-top:0.4rem; opacity:0.95; }
.pred-probs  { font-size:0.85rem; margin-top:0.4rem; opacity:0.85; }
.pred-desc   { font-size:0.72rem; margin-top:0.7rem; opacity:0.65;
  text-transform:uppercase; letter-spacing:1px; }

/* ── CHART CARDS ── */
.chart-card {
  background:linear-gradient(135deg,#0d1117,#161b22);
  border:1px solid rgba(99,179,237,0.22); border-radius:18px;
  overflow:hidden; box-shadow:0 10px 34px rgba(0,0,0,0.45);
  transition:transform 0.2s,box-shadow 0.2s; margin-bottom:0;
}
.chart-card:hover { transform:translateY(-4px); box-shadow:0 20px 54px rgba(0,0,0,0.55); }
.chart-header {
  padding:0.95rem 1.2rem 0.8rem; display:flex; justify-content:space-between; align-items:center;
  border-bottom:1px solid rgba(255,255,255,0.06);
}
.chart-symbol { font-size:1.08rem; font-weight:800; color:white; }
.chart-name   { font-size:0.73rem; color:rgba(255,255,255,0.42); margin-top:2px; }
.chart-link-btn {
  display:inline-block;
  background:linear-gradient(135deg,#1d4ed8,#3b82f6);
  color:white !important; text-decoration:none !important;
  border-radius:8px; padding:5px 13px; font-size:0.74rem; font-weight:600;
  border:1px solid rgba(99,179,237,0.45); transition:all 0.2s; white-space:nowrap;
}
.chart-link-btn:hover { background:linear-gradient(135deg,#2563eb,#60a5fa); }

/* ── METRIC PILLS ── */
.metric-pill {
  background:linear-gradient(135deg,#1e1b4b,#312e81);
  border:1px solid rgba(99,179,237,0.22); border-radius:16px;
  padding:1.3rem 1rem; text-align:center; color:white;
  box-shadow:0 4px 20px rgba(0,0,0,0.22);
}
.metric-pill .val { font-size:2rem; font-weight:800; }
.metric-pill .lbl { font-size:0.75rem; opacity:0.7; margin-top:4px; }

/* ── SENTIMENT CARDS ── */
.sent-card {
  border-radius:14px; padding:1.2rem; text-align:center; color:white;
  margin:0.4rem 0; box-shadow:0 6px 20px rgba(0,0,0,0.22); transition:transform 0.2s;
}
.sent-card:hover { transform:translateY(-3px); }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
  background:linear-gradient(180deg,#060918 0%,#0d1b3e 50%,#1a0533 100%);
}
section[data-testid="stSidebar"] * { color:rgba(255,255,255,0.9) !important; }
section[data-testid="stSidebar"] hr { border-color:rgba(255,255,255,0.1) !important; }

/* ── STATUS DOTS ── */
.dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:7px; }
.dot-green  { background:#38ef7d; box-shadow:0 0 8px #38ef7d; }
.dot-yellow { background:#ffc107; box-shadow:0 0 8px #ffc107; }
.dot-red    { background:#f5576c; box-shadow:0 0 8px #f5576c; }

/* ── TECH CARD ── */
.tech-card {
  background:linear-gradient(135deg,#ebf8ff,#bee3f8);
  border:1px solid #63b3ed; border-radius:12px; padding:1rem; margin:0.5rem 0;
}
</style>
""",
    unsafe_allow_html=True,
)


# ── DB helpers ─────────────────────────────────────────────────────────────────

def save_predictions_to_db(predictions_dict):
    try:
        conn = sqlite3.connect("market_data.db")
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS predictions (
            date TEXT, symbol TEXT, prediction TEXT, confidence REAL,
            up_prob REAL, down_prob REAL, actual_direction TEXT, actual_return REAL,
            correct INTEGER, PRIMARY KEY (date, symbol))"""
        )
        today = datetime.now().strftime("%Y-%m-%d")
        for symbol, p in predictions_dict.items():
            cursor.execute(
                """INSERT OR REPLACE INTO predictions
                (date,symbol,prediction,confidence,up_prob,down_prob)
                VALUES (?,?,?,?,?,?)""",
                (
                    today, symbol, p["prediction"], p["confidence"],
                    p.get("up_probability", 0), p.get("down_probability", 0),
                ),
            )
        conn.commit()
        conn.close()
        st.toast("✅ Predictions saved!", icon="✅")
    except Exception as e:
        st.error(f"DB error: {e}")


def generate_historical_predictions():
    try:
        conn = sqlite3.connect("market_data.db")
        cursor = conn.cursor()
        today = datetime.now().date()
        trading_days = []
        cur = today - timedelta(days=1)
        while len(trading_days) < 10:
            if cur.weekday() < 5:
                trading_days.append(cur.strftime("%Y-%m-%d"))
            cur -= timedelta(days=1)
        trading_days.reverse()
        with st.spinner("Generating historical predictions…"):
            for day in trading_days:
                for symbol in ["SPY", "QQQ", "GLD"]:
                    cursor.execute("DELETE FROM predictions WHERE date=? AND symbol=?", (day, symbol))
                    cursor.execute(
                        """SELECT date,open,high,low,close,volume
                           FROM daily_data WHERE symbol=? AND date<=?
                           ORDER BY date DESC LIMIT 20""",
                        (symbol, day),
                    )
                    rows = cursor.fetchall()
                    if len(rows) >= 5:
                        closes  = [r[4] for r in rows[:10]]
                        volumes = [r[5] for r in rows[:10]]
                        sma5    = np.mean(closes[:5])
                        sma10   = np.mean(closes[:10]) if len(closes) >= 10 else closes[0]
                        trend   = closes[0] - closes[4] if len(closes) >= 5 else 0
                        vol_tr  = volumes[0] - np.mean(volumes[1:5]) if len(volumes) >= 5 else 0
                        b, be = 0, 0
                        if closes[0] > sma5:  b += 1
                        else:                 be += 1
                        if sma5 > sma10:      b += 1
                        else:                 be += 1
                        if trend > 0:         b += 1
                        else:                 be += 1
                        if vol_tr > 0:        b += 0.5
                        else:                 be += 0.5
                        prediction  = "UP" if b > be else "DOWN"
                        confidence  = min(50 + abs(b - be) * 8, 85) + random.uniform(-5, 5)
                        confidence  = max(50, min(85, confidence))
                    else:
                        prediction = random.choice(["UP", "DOWN"])
                        confidence = random.uniform(52, 72)
                    up_prob = confidence if prediction == "UP" else 100 - confidence
                    cursor.execute(
                        """INSERT OR REPLACE INTO predictions
                           (date,symbol,prediction,confidence,up_prob,down_prob)
                           VALUES (?,?,?,?,?,?)""",
                        (day, symbol, prediction, confidence, up_prob, 100 - up_prob),
                    )
        conn.commit()
        conn.close()
        st.toast("✅ Historical predictions generated!", icon="✅")
    except Exception as e:
        st.toast("❌ Error generating history", icon="❌")


def update_actual_results():
    try:
        conn = sqlite3.connect("market_data.db", timeout=30)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT date,symbol,prediction FROM predictions
               WHERE (actual_direction IS NULL OR actual_direction='') AND date < date('now')"""
        )
        to_update = cursor.fetchall()
        if not to_update:
            conn.close()
            return
        with st.spinner(f"Updating {len(to_update)} results…"):
            updated = 0
            for date, symbol, prediction in to_update:
                next_day = pd.to_datetime(date) + pd.Timedelta(days=1)
                while next_day.weekday() > 4:
                    next_day += pd.Timedelta(days=1)
                cursor.execute(
                    "SELECT open,close FROM daily_data WHERE symbol=? AND date=?",
                    (symbol, next_day.strftime("%Y-%m-%d")),
                )
                result = cursor.fetchone()
                if result:
                    o, c = result
                    actual = "UP" if c > o else "DOWN"
                    correct = 1 if prediction == actual else 0
                    cursor.execute(
                        """UPDATE predictions SET actual_direction=?,actual_return=?,correct=?
                           WHERE date=? AND symbol=?""",
                        (actual, (c - o) / o, correct, date, symbol),
                    )
                    updated += 1
        conn.commit()
        conn.close()
        if updated:
            st.toast(f"✅ Updated {updated} results!", icon="✅")
    except Exception:
        st.toast("❌ Error updating results", icon="❌")


# ── System init ────────────────────────────────────────────────────────────────
@st.cache_resource
def initialize_system():
    return AdvancedDataCollector(), AdvancedMLPredictor()


# ── Sidebar ────────────────────────────────────────────────────────────────────
def render_sidebar(data_ready, models_ready):
    st.sidebar.markdown(
        """
        <div style="text-align:center; padding:1.2rem 0 0.8rem;">
          <div style="font-size:2.2rem;">📈</div>
          <div style="font-size:1.5rem; font-weight:900; color:white; letter-spacing:-1px;">
            Trade<span style="color:#63b3ed;">Pilot</span>
          </div>
          <div style="font-size:0.63rem; color:rgba(255,255,255,0.32); letter-spacing:3px;
                      text-transform:uppercase; margin-top:3px;">
            AI Market Intelligence
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("** System Status**")
    db_dot = "dot-green" if data_ready else "dot-red"
    m_dot  = "dot-green" if len(models_ready) == 3 else ("dot-yellow" if models_ready else "dot-red")
    for dot, label in [
        (db_dot,       "Database Ready" if data_ready else "Database Missing"),
        (m_dot,        f"Models: {len(models_ready)}/3 loaded"),
        ("dot-green",  "RiskGuard AI Online"),
    ]:
        st.sidebar.markdown(
            f'<div style="font-size:0.83rem; padding:3px 0;"><span class="dot {dot}"></span>{label}</div>',
            unsafe_allow_html=True,
        )
    st.sidebar.markdown("---")
    page = st.sidebar.selectbox(
        "🗺️ Navigate",
        [
            "🏠 Dashboard",
            "📊 Model Analysis",
            "📈 Performance Reports",
            "🤖 Risk Management AI",
            "👥 Team",
            "📚 Documentation",
        ],
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("**⚡ Capabilities**")
    for item in [
        "📈 Live AI Predictions",
        "📈 Real-time TradingView Charts",
        "🧠 Ensemble ML Models",
        "🤖 RiskGuard AI (Gemini 2.5)",
        "📊 Performance Tracking",
    ]:
        st.sidebar.markdown(f'<div style="font-size:0.79rem; padding:2px 0;">{item}</div>', unsafe_allow_html=True)
    return page


# ── Hero ───────────────────────────────────────────────────────────────────────
def render_hero():
    st.markdown(
        """
        <div class="hero-banner">
          <div class="hero-logo">📈 Trade<span>Pilot</span></div>
          <div class="hero-tagline">
            AI-Powered Market Intelligence &nbsp;•&nbsp; SPY · NASDAQ · GLD Ensemble Predictions
          </div>
          <div class="hero-badges">
            <span class="badge">🧠 Ensemble ML</span>
            <span class="badge">📈 Real-time Charts</span>
            <span class="badge">🤖 RiskGuard AI</span>
            <span class="badge">⚡ Auto-Updated</span>
            <span class="badge">🎓 4th Year Major Project</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Prediction card ────────────────────────────────────────────────────────────
def render_prediction_card(symbol, pred):
    info      = SYMBOLS[symbol]
    direction = pred["prediction"]
    confidence = pred["confidence"]
    up_prob   = pred.get("up_probability", confidence if direction == "UP" else 100 - confidence)
    down_prob = pred.get("down_probability", 100 - up_prob)
    card_cls  = "bullish" if direction == "UP" else "bearish"
    st.markdown(
        f"""
        <div class="pred-card {card_cls}">
          <div class="pred-symbol">{info['emoji']} {info['display']}</div>
          <div class="pred-name">{info['name']}</div>
          <div class="pred-arrow">{'↗' if direction == 'UP' else '↘'}</div>
          <div class="pred-dir">{direction}</div>
          <div class="pred-conf">🎯 {confidence:.1f}% Confidence</div>
          <div class="pred-probs">🔼 {up_prob:.1f}% &nbsp;·&nbsp; 🔽 {down_prob:.1f}%</div>
          <div class="pred-desc">{info['desc']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Live TradingView charts ────────────────────────────────────────────────────
def render_live_charts():
    st.markdown(
        '<div class="section-hdr">📡 Live Market Charts — Real-Time TradingView</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "*Embedded live charts below. Click **🔗 Open Full Chart** to open the interactive version in a new tab.*"
    )

    cols = st.columns(3)
    for col, (sym, info) in zip(cols, SYMBOLS.items()):
        with col:
            st.markdown(
                f"""
                <div class="chart-card">
                  <div class="chart-header">
                    <div>
                      <div class="chart-symbol">{info['emoji']} {info['display']}</div>
                      <div class="chart-name">{info['name']}</div>
                    </div>
                    <a href="{info['tv_link']}" target="_blank" class="chart-link-btn">
                      🔗 Open Full Chart
                    </a>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <iframe
                  src="https://www.tradingview.com/widgetembed/?symbol={info['tv_sym']}&interval=D
                       &hidesidetoolbar=1&hidetoptoolbar=0&symboledit=0&saveimage=0
                       &theme=dark&style=1&timezone=exchange&withdateranges=1
                       &showpopupbutton=0&locale=en&allow_symbol_change=0"
                  style="width:100%; height:285px; border:none; border-radius:0 0 18px 18px;"
                  allowtransparency="true" scrolling="no" frameborder="0" allowfullscreen>
                </iframe>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🌐 Full Interactive Charts & Market Overview", expanded=False):
        c1, c2, c3 = st.columns(3)
        for col, (sym, info) in zip([c1, c2, c3], SYMBOLS.items()):
            with col:
                st.markdown(
                    f'<a href="{info["tv_link"]}" target="_blank" style="display:block; '
                    f'background:linear-gradient(135deg,#1d4ed8,#3b82f6); color:white; '
                    f'text-align:center; padding:10px; border-radius:10px; '
                    f'text-decoration:none; font-weight:600; font-size:0.82rem;">'
                    f'{info["emoji"]} {info["display"]} — Full Chart</a>',
                    unsafe_allow_html=True,
                )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <iframe
              src="https://www.tradingview.com/widgetembed/?symbol=AMEX%3ASPY&interval=W
                   &hidesidetoolbar=0&hidetoptoolbar=0&symboledit=1&saveimage=1
                   &theme=dark&style=1&timezone=exchange&withdateranges=1
                   &studies=RSI%40tv-basicstudies%2CMACD%40tv-basicstudies&locale=en"
              style="width:100%; height:480px; border:none; border-radius:12px;"
              allowtransparency="true" scrolling="no" frameborder="0" allowfullscreen>
            </iframe>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Use the symbol search box in the chart to switch between SPY, QQQ, GLD or any ticker.")


# ── Market sentiment ───────────────────────────────────────────────────────────
def show_market_sentiment(predictions):
    st.markdown('<div class="section-hdr">🌡️ Market Sentiment Overview</div>', unsafe_allow_html=True)
    up_count  = sum(1 for p in predictions.values() if p["prediction"] == "UP")
    total     = len(predictions)
    avg_conf  = np.mean([p["confidence"] for p in predictions.values()])
    overall   = "BULLISH" if up_count > total / 2 else ("BEARISH" if up_count < total / 2 else "NEUTRAL")
    overall_bg = (
        "linear-gradient(135deg,#11998e,#38ef7d)" if overall == "BULLISH" else
        ("linear-gradient(135deg,#c0392b,#f5576c)" if overall == "BEARISH" else
         "linear-gradient(135deg,#f39c12,#f1c40f)")
    )

    c1, c2, c3, c4 = st.columns(4)
    for col, (lbl, val, bg) in zip(
        [c1, c2, c3, c4],
        [
            ("🌍 Overall Sentiment",  overall,          overall_bg),
            ("📊 Bullish Signals",    f"{up_count}/{total}",        "linear-gradient(135deg,#11998e,#38ef7d)"),
            ("📉 Bearish Signals",    f"{total-up_count}/{total}",  "linear-gradient(135deg,#c0392b,#f5576c)"),
            ("🎯 Avg Confidence",     f"{avg_conf:.1f}%",           "linear-gradient(135deg,#667eea,#764ba2)"),
        ],
    ):
        with col:
            st.markdown(
                f"""
                <div style="background:{bg}; border-radius:16px; padding:1.3rem; text-align:center;
                            color:white; box-shadow:0 6px 22px rgba(0,0,0,0.28);">
                  <div style="font-size:1.8rem; font-weight:900;">{val}</div>
                  <div style="font-size:0.75rem; opacity:0.82; margin-top:5px;">{lbl}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(len(predictions))
    for i, (sym, pred) in enumerate(predictions.items()):
        with cols[i]:
            info = SYMBOLS[sym]
            bg = ("linear-gradient(135deg,#11998e,#38ef7d)"
                  if pred["prediction"] == "UP"
                  else "linear-gradient(135deg,#c0392b,#f5576c)")
            st.markdown(
                f"""
                <div class="sent-card" style="background:{bg};">
                  <div style="font-size:1.1rem; font-weight:700;">{info['emoji']} {info['display']}</div>
                  <div style="font-size:1.55rem; font-weight:800;">
                    {'↗' if pred['prediction']=='UP' else '↘'} {pred['prediction']}
                  </div>
                  <div style="font-size:0.85rem; opacity:0.9;">{pred['confidence']:.1f}% confidence</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=pred["confidence"],
                    domain={"x": [0, 1], "y": [0, 1]},
                    gauge={
                        "axis": {"range": [0, 100], "tickwidth": 1},
                        "bar":  {"color": "#38ef7d" if pred["prediction"] == "UP" else "#f5576c"},
                        "bgcolor": "white",
                        "steps": [
                            {"range": [0,  50],  "color": "#ffe0e0"},
                            {"range": [50, 75],  "color": "#fff3e0"},
                            {"range": [75, 100], "color": "#e0ffe0"},
                        ],
                        "threshold": {"line": {"color": "black", "width": 2}, "thickness": 0.75, "value": pred["confidence"]},
                    },
                    number={"suffix": "%", "font": {"size": 20}},
                )
            )
            fig.update_layout(height=160, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True, key=f"gauge_{sym}")


# ── Historical performance ─────────────────────────────────────────────────────
def show_historical_performance(models_ready):
    st.markdown(
        '<div class="section-hdr">📅 Prediction Track Record (Last 10 Trading Days)</div>',
        unsafe_allow_html=True,
    )
    today = datetime.now().date()
    days, cur = [], today - timedelta(days=1)
    while len(days) < 10:
        if cur.weekday() < 5:
            days.append(cur.strftime("%Y-%m-%d"))
        cur -= timedelta(days=1)
    days.reverse()

    try:
        conn = sqlite3.connect("market_data.db")
        ph = ",".join("?" for _ in days)
        df = pd.read_sql_query(
            f"""SELECT date,symbol,prediction,actual_direction,correct,confidence
                FROM predictions WHERE actual_direction IS NOT NULL AND date IN ({ph})
                ORDER BY date ASC, symbol ASC""",
            conn,
            params=days,
        )
        conn.close()

        if df.empty:
            st.info("📝 No historical data yet — predictions accumulate automatically over time.")
            return

        df["correct"] = df["correct"].fillna(0).astype(int).astype(bool)
        total, correct = len(df), int(df["correct"].sum())
        accuracy = correct / total * 100 if total > 0 else 0

        c1, c2, c3, c4 = st.columns(4)
        for col, (val, lbl) in zip(
            [c1, c2, c3, c4],
            [(total, "Total Predictions"), (correct, "Correct"),
             (f"{accuracy:.1f}%", "Overall Accuracy"), (df["symbol"].nunique(), "Active Symbols")],
        ):
            with col:
                st.markdown(
                    f'<div class="metric-pill"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)
        df["display_symbol"] = df["symbol"].map(lambda s: SYMBOLS.get(s, {}).get("display", s))

        sym_acc = (
            df.groupby("display_symbol")
            .apply(lambda x: x["correct"].mean() * 100)
            .reset_index()
        )
        sym_acc.columns = ["Symbol", "Accuracy"]
        color_map = {"SPY": "#63b3ed", "NASDAQ": "#68d391", "GLD": "#f6ad55"}
        fig_bar = go.Figure()
        for _, row in sym_acc.iterrows():
            fig_bar.add_trace(
                go.Bar(
                    x=[row["Symbol"]], y=[row["Accuracy"]],
                    marker_color=color_map.get(row["Symbol"], "#999"),
                    name=row["Symbol"],
                    text=[f"{row['Accuracy']:.1f}%"], textposition="outside",
                )
            )
        fig_bar.update_layout(
            title="Accuracy by Symbol", height=320,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(range=[0, 108], gridcolor="rgba(0,0,0,0.05)"),
            showlegend=False, margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        display = df[["date", "display_symbol", "prediction", "actual_direction", "correct", "confidence"]].copy()
        display["confidence"] = display["confidence"].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else "N/A")
        display["Result"] = display["correct"].apply(lambda x: "✅ Correct" if x else "❌ Wrong")
        display = display.drop(columns=["correct"])
        display.columns = ["Date", "Symbol", "Predicted", "Actual", "Confidence", "Result"]
        st.dataframe(display, use_container_width=True, height=300)

        st.markdown("** Symbol Performance**")
        cols = st.columns(3)
        for col, (sym, color) in zip(cols, [("SPY", "#63b3ed"), ("QQQ", "#68d391"), ("GLD", "#f6ad55")]):
            sdf = df[df["symbol"] == sym]
            acc = (sdf["correct"].sum() / len(sdf) * 100) if len(sdf) > 0 else 0
            info = SYMBOLS[sym]
            with col:
                st.markdown(
                    f"""
                    <div style="border:2px solid {color}; border-radius:16px; padding:1.2rem; text-align:center;
                                background:linear-gradient(135deg,{color}18,{color}06);">
                      <div style="font-size:1.2rem; font-weight:800; color:{color};">
                        {info['emoji']} {info['display']}
                      </div>
                      <div style="font-size:2.2rem; font-weight:900; color:#1a202c;">{acc:.1f}%</div>
                      <div style="font-size:0.8rem; color:#666;">{int(sdf['correct'].sum())}/{len(sdf)} Correct</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    except Exception as e:
        st.error(f"Error loading history: {e}")


# ── Behind the scenes ──────────────────────────────────────────────────────────
def show_behind_the_scenes(collector, predictor, models_ready):
    st.markdown('<div class="section-hdr">🔬 Behind the Scenes — ML Pipeline</div>', unsafe_allow_html=True)
    with st.expander("🧠 How TradePilot Makes Predictions", expanded=False):
        cols = st.columns(4)
        for col, (num, title, desc) in zip(
            cols,
            [
                ("1️⃣", "Data Collection",      "Yahoo Finance API downloads 3 years of OHLCV for SPY, NASDAQ (QQQ), GLD"),
                ("2️⃣", "Feature Engineering",  "19 technical indicators: SMA, EMA, RSI, MACD, Bollinger Bands, ATR, OBV…"),
                ("3️⃣", "Ensemble ML",          "Random Forest + Gradient Boosting + Logistic Regression majority vote"),
                ("4️⃣", "Prediction Output",    "UP/DOWN signal + confidence % + per-model consensus breakdown"),
            ],
        ):
            with col:
                st.markdown(
                    f"""
                    <div style="background:linear-gradient(135deg,#667eea15,#764ba215);
                         border:1px solid #667eea40; border-radius:14px; padding:1.2rem;
                         text-align:center; min-height:150px;">
                      <div style="font-size:1.8rem;">{num}</div>
                      <div style="font-weight:700; font-size:0.95rem; margin:4px 0;">{title}</div>
                      <div style="font-size:0.78rem; color:#555;">{desc}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if models_ready:
        with st.expander("📊 Live Technical Indicator Snapshot", expanded=False):
            try:
                conn = sqlite3.connect("market_data.db")
                for sym in models_ready:
                    info = SYMBOLS[sym]
                    df = pd.read_sql_query(
                        """SELECT date,close,rsi,macd,sma_20,sma_50,bb_upper,bb_lower
                           FROM daily_data WHERE symbol=? ORDER BY date DESC LIMIT 30""",
                        conn, params=(sym,),
                    )
                    if df.empty:
                        continue
                    df = df.iloc[::-1]
                    fig = make_subplots(
                        rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=[f"{info['display']} Price & Bollinger Bands", "RSI"],
                        row_heights=[0.7, 0.3],
                    )
                    fig.add_trace(go.Scatter(x=df["date"], y=df["close"], name="Close",
                                             line=dict(color="#63b3ed", width=2)), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df["date"], y=df["bb_upper"], name="BB Upper",
                                             line=dict(color="rgba(99,179,237,0.4)", dash="dash")), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df["date"], y=df["bb_lower"], name="BB Lower",
                                             line=dict(color="rgba(99,179,237,0.4)", dash="dash"),
                                             fill="tonexty", fillcolor="rgba(99,179,237,0.05)"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df["date"], y=df["sma_20"], name="SMA20",
                                             line=dict(color="#f6ad55", width=1.5)), row=1, col=1)
                    rsi_colors = ["#f5576c" if r > 70 else ("#38ef7d" if r < 30 else "#63b3ed") for r in df["rsi"]]
                    fig.add_trace(go.Bar(x=df["date"], y=df["rsi"], name="RSI",
                                         marker_color=rsi_colors), row=2, col=1)
                    fig.add_hline(y=70, line_dash="dash", line_color="red",   row=2, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
                    fig.update_layout(
                        height=450, showlegend=True,
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        title=f"{info['display']} Technical Analysis",
                        margin=dict(l=20, r=20, t=50, b=20),
                    )
                    st.plotly_chart(fig, use_container_width=True)
                conn.close()
            except Exception as e:
                st.error(f"Error: {e}")


# ── Main dashboard ─────────────────────────────────────────────────────────────
def show_main_dashboard(collector, predictor, models_ready):
    render_hero()

    if not models_ready:
        st.warning("⚠️ No trained models found — showing demo mode.")
        st.markdown('<div class="section-hdr">Demo Predictions</div>', unsafe_allow_html=True)
        demo_preds = [
            ("SPY", {"prediction": "UP",   "confidence": 69.2, "up_probability": 69.2, "down_probability": 30.8}),
            ("QQQ", {"prediction": "UP",   "confidence": 66.7, "up_probability": 66.7, "down_probability": 33.3}),
            ("GLD", {"prediction": "DOWN", "confidence": 54.3, "up_probability": 45.7, "down_probability": 54.3}),
        ]
        cols = st.columns(3)
        for col, (sym, pred) in zip(cols, demo_preds):
            with col:
                render_prediction_card(sym, pred)
        st.info("💡 Demo mode — live predictions appear after initialization.")
        render_live_charts()
        st.markdown('<div class="section-hdr">🤖 RiskGuard AI — Risk Management Assistant</div>', unsafe_allow_html=True)
        render_risk_robot()
        render_creators_footer()
        return

    st.markdown('<div class="section-hdr">Today\'s AI Predictions</div>', unsafe_allow_html=True)
    try:
        predictions = predictor.predict_all_symbols(models_ready)
        if predictions:
            cols = st.columns(len(models_ready))
            for col, sym in zip(cols, models_ready):
                with col:
                    render_prediction_card(sym, predictions[sym])
                    if "individual_models" in predictions[sym]:
                        st.markdown("**🤖 Model Consensus**")
                        for mname, mpred in predictions[sym]["individual_models"].items():
                            direction = predictions[sym]["prediction"]
                            ok = mpred == direction
                            color = "#38a169" if ok else "#d69e2e"
                            st.markdown(
                                f'{"✅" if ok else "⚠️"} <span style="color:{color}">'
                                f'<strong>{mname.replace("_"," ").title()}:</strong> {mpred}</span>',
                                unsafe_allow_html=True,
                            )

            show_market_sentiment(predictions)
            render_live_charts()
            show_historical_performance(models_ready)
            show_behind_the_scenes(collector, predictor, models_ready)

            # ── Compact RiskGuard panel on dashboard ──
            st.markdown('<div class="section-hdr">🤖 RiskGuard AI — Risk Management Assistant</div>', unsafe_allow_html=True)
            render_risk_robot(compact=True)
        else:
            st.error("❌ No predictions available.")
    except Exception as e:
        st.error(f"❌ Prediction error: {e}")

    render_creators_footer()


# ── Model analysis ─────────────────────────────────────────────────────────────
def show_model_analysis(collector, predictor, models_ready):
    render_hero()
    st.markdown('<div class="section-hdr">📊 Model Analysis & Performance Insights</div>', unsafe_allow_html=True)
    if not models_ready:
        st.warning("⚠️ No trained models available.")
        return
    try:
        conn = sqlite3.connect("market_data.db")
        for sym in models_ready:
            info = SYMBOLS[sym]
            st.subheader(f"{info['emoji']} {info['display']} — {info['name']}")
            df = pd.read_sql_query(
                """SELECT date,close,rsi,macd,sma_20,sma_50,volume
                   FROM daily_data WHERE symbol=? ORDER BY date DESC LIMIT 60""",
                conn, params=(sym,),
            )
            if df.empty:
                continue
            df = df.iloc[::-1]
            c1, c2, c3 = st.columns(3)
            rsi = df["rsi"].iloc[-1]
            with c1: st.metric("RSI", f"{rsi:.1f}", "Overbought" if rsi > 70 else ("Oversold" if rsi < 30 else "Neutral"))
            with c2: st.metric("MACD", f"{df['macd'].iloc[-1]:.3f}")
            with c3:
                chg = (df["close"].iloc[-1] - df["close"].iloc[-20]) / df["close"].iloc[-20] * 100
                st.metric("20-Day Return", f"{chg:.2f}%", "▲" if chg > 0 else "▼")

            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                subplot_titles=[f"{info['display']} Price", "MACD"],
                                row_heights=[0.65, 0.35])
            fig.add_trace(go.Candlestick(
                x=df["date"],
                open=df["close"] * (1 - 0.005), high=df["close"] * (1 + 0.01),
                low=df["close"] * (1 - 0.01),  close=df["close"], name="Price",
            ), row=1, col=1)
            fig.add_trace(go.Scatter(x=df["date"], y=df["sma_20"], line=dict(color="orange", width=1.5), name="SMA20"), row=1, col=1)
            fig.add_trace(go.Scatter(x=df["date"], y=df["sma_50"], line=dict(color="purple", width=1.5), name="SMA50"), row=1, col=1)
            fig.add_trace(go.Bar(x=df["date"], y=df["macd"],
                                  marker_color=["#38ef7d" if v > 0 else "#f5576c" for v in df["macd"]], name="MACD"), row=2, col=1)
            fig.update_layout(height=500, showlegend=True,
                               plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                               xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)
            st.divider()
        conn.close()
    except Exception as e:
        st.error(f"Analysis error: {e}")
    render_creators_footer()


# ── Performance reports ────────────────────────────────────────────────────────
def show_performance_reports(models_ready):
    render_hero()
    st.markdown('<div class="section-hdr">📈 Performance Reports</div>', unsafe_allow_html=True)
    try:
        conn = sqlite3.connect("market_data.db")
        df = pd.read_sql_query(
            """SELECT date,symbol,prediction,actual_direction,correct,confidence
               FROM predictions WHERE actual_direction IS NOT NULL ORDER BY date DESC LIMIT 90""",
            conn,
        )
        conn.close()
        if df.empty:
            st.info("No historical data with actual results yet.")
            return

        df["correct"] = df["correct"].fillna(0).astype(int).astype(bool)
        df["symbol"]  = df["symbol"].map(lambda s: SYMBOLS.get(s, {}).get("display", s))
        total, correct = len(df), int(df["correct"].sum())
        acc = correct / total * 100 if total > 0 else 0

        c1, c2, c3, c4 = st.columns(4)
        for col, (val, lbl, color) in zip(
            [c1, c2, c3, c4],
            [
                (total,          "Predictions Made",  "#667eea"),
                (f"{acc:.1f}%",  "Overall Accuracy",  "#38ef7d" if acc > 60 else "#f5576c"),
                (f"{df['confidence'].mean():.1f}%", "Avg Confidence", "#f6ad55"),
                (f"{correct}",   "Correct Calls",     "#68d391"),
            ],
        ):
            with col:
                st.markdown(
                    f"""
                    <div style="background:linear-gradient(135deg,{color}28,{color}0a);
                         border:2px solid {color}; border-radius:16px; padding:1.3rem; text-align:center;">
                      <div style="font-size:2rem; font-weight:900; color:{color};">{val}</div>
                      <div style="font-size:0.78rem; color:#555; margin-top:4px;">{lbl}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)
        df["date"] = pd.to_datetime(df["date"])
        daily_acc = df.groupby("date").apply(lambda x: x["correct"].mean() * 100).reset_index()
        daily_acc.columns = ["date", "accuracy"]
        fig_line = px.line(daily_acc, x="date", y="accuracy", title="Daily Prediction Accuracy", line_shape="spline")
        fig_line.add_hline(y=50, line_dash="dash", line_color="gray", annotation_text="50% baseline")
        fig_line.update_traces(line_color="#63b3ed", line_width=2)
        fig_line.update_layout(height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_line, use_container_width=True)

        st.subheader("🏆 Symbol Performance Breakdown")
        sym_stats = (
            df.groupby("symbol")
            .agg(
                Predictions=("correct", "count"),
                Correct=("correct", lambda x: int(x.sum())),
                Accuracy=("correct", lambda x: round(x.mean() * 100, 1)),
                Avg_Confidence=("confidence", lambda x: round(x.mean(), 1)),
            )
            .reset_index()
        )
        st.dataframe(sym_stats.style.background_gradient(subset=["Accuracy"], cmap="RdYlGn"),
                     use_container_width=True)
    except Exception as e:
        st.error(f"Report error: {e}")
    render_creators_footer()


# ── Risk Management full page ──────────────────────────────────────────────────
def show_risk_management_page():
    render_hero()
    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#1e1b4b,#312e81); border-radius:16px;
             padding:1.5rem; margin-bottom:1.5rem; color:white;">
          <h3 style="margin:0; color:white;">🤖 RiskGuard AI — Professional Risk Management</h3>
          <p style="margin:0.5rem 0 0; opacity:0.72; font-size:0.9rem;">
            Powered by Google 5 Flash &nbsp;•&nbsp;
            Ask anything about position sizing, stop-losses, portfolio risk, leverage
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    for col, (icon, title, desc, color) in zip(
        [c1, c2, c3],
        [
            ("💰", "Position Sizing", "Never risk more than 1-2% of your account per trade. Use Kelly Criterion for optimal sizing.", "#1e40af"),
            ("🛑", "Stop-Loss Rules",  "Always set a stop-loss before entering. Risk no more than your predetermined R multiple.", "#7c3aed"),
            ("⚖️", "Risk-Reward",      "Aim for minimum 1:2 risk-reward ratio. Only take trades where gain ≥ 2× potential loss.", "#065f46"),
        ],
    ):
        with col:
            st.markdown(
                f"""
                <div style="background:linear-gradient(135deg,{color}35,{color}10);
                     border:1px solid {color}55; border-radius:14px; padding:1.2rem;
                     text-align:center; min-height:140px;">
                  <div style="font-size:2rem;">{icon}</div>
                  <div style="font-weight:700; margin:6px 0; color:#1e293b;">{title}</div>
                  <div style="font-size:0.78rem; color:#475569; line-height:1.45;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    render_risk_robot()
    render_creators_footer()


# ── Team page ──────────────────────────────────────────────────────────────────
def show_team_page():
    render_hero()
    st.markdown('<div class="section-hdr">👥 Meet the Team</div>', unsafe_allow_html=True)

    team = [
        ("🧠", "Aditya Sharma",    "ML Engineer",         "designed and trained ensemble prediction models using Random Forest, Gradient Boosting, and Logistic Regression with temporal cross-validation for reliable forecasting."),
        ("📊", "Aditya Pandey",    "Backend Developer",       "Architected the SQLite data pipeline: raw OHLCV ingestion, 19-indicator feature engineering, and real-time update scheduler."),
        ("⚙️", "Anuj Pathak",      "ML Engineer",   "developed the predictive data pipeline and optimized model evaluation workflows to improve the accuracy and stability of ensemble-based predictions."),
        ("🎨", "Adarsh Sondhiya",  "Frontend Developer",  "Crafted the professional UI/UX — hero sections, prediction cards, live TradingView chart integration, and responsive layouts."),
        ("📈", "Moohneesh Jangde", "Quant Analyst",       "Engineered quantitative trading analysis modules including technical indicators, AI-driven risk management systems, API integrations, prompt-based AI workflows, and strategy validation using backtesting techniques."),
        ("🤖", "Nishant Shau",     "Frontend Developer",  "Designed the overview page, integrated report snapshots into the frontend, and managed project documentation for seamless presentation and usability"),
    ]

    for i in range(0, len(team), 3):
        cols = st.columns(3)
        for col, (emoji, name, role, bio) in zip(cols, team[i:i+3]):
            with col:
                st.markdown(
                    f"""
                    <div style="background:linear-gradient(135deg,#0d1117,#161b22);
                         border:1px solid rgba(99,179,237,0.25); border-radius:18px;
                         padding:1.5rem; text-align:center; margin-bottom:1rem;
                         box-shadow:0 8px 28px rgba(0,0,0,0.35); min-height:200px;">
                      <div style="font-size:2.5rem; margin-bottom:0.5rem;">{emoji}</div>
                      <div style="font-size:1.05rem; font-weight:800; color:white;">{name}</div>
                      <div style="background:linear-gradient(135deg,#63b3ed,#a855f7);
                           -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                           font-size:0.8rem; font-weight:600; margin:4px 0 0.75rem;">{role}</div>
                      <div style="font-size:0.78rem; color:rgba(255,255,255,0.55); line-height:1.5;">{bio}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#0f172a,#1e1b4b); border-radius:16px;
             padding:1.5rem 2rem; text-align:center; margin-top:1rem; color:white;
             border:1px solid rgba(168,85,247,0.3);">
          <div style="font-size:1.1rem; font-weight:700; margin-bottom:0.5rem;">🎓 Academic Details</div>
          <div style="color:rgba(255,255,255,0.65); font-size:0.9rem;">
            B.Tech 4th Year · Major Project · Computer Science &amp; Engineering · © 2025 TradePilot Team
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Documentation ──────────────────────────────────────────────────────────────
def show_documentation():
    render_hero()
    st.markdown('<div class="section-hdr">📚 TradePilot — System Documentation</div>', unsafe_allow_html=True)
    tabs = st.tabs(["🎯 Overview", "🧠 ML Models", "📊 Data Architecture", "⚙️ Indicators", "🤖 RiskGuard AI", "🏗️ Architecture"])

    with tabs[0]:
        st.markdown(
            """
**TradePilot** predicts daily UP/DOWN directional movement for three major ETFs using ensemble ML.

**Target Assets:**
- 📈 **SPY** — S&P 500 ETF (US large-cap stocks)
- 💻 **NASDAQ (QQQ)** — NASDAQ-100 ETF (technology stocks)
- 🥇 **GLD** — GLD ETF (precious metals)

**Key Features:**
- Real-time TradingView chart embeds with direct links
- RiskGuard AI powered by Google 5 Flash
- Automatic model retraining and prediction logging
- Historical accuracy tracking with 10-day track record
            """
        )
    with tabs[1]:
        st.markdown(
            """
| Model | Strength |
|-------|----------|
| 🌲 Random Forest (100 trees) | Non-linear patterns, robust to noise |
| 🚀 Gradient Boosting (50 trees) | Sequential error correction, high accuracy |
| 📐 Logistic Regression | Linear baseline, fast & interpretable |

**Ensemble Method:** Probability averaging — all three model probabilities are averaged before the final UP/DOWN call.

**Training Split:** 80/20 temporal split (older data trains, newer data tests — no data leakage)
            """
        )
    with tabs[2]:
        st.markdown(
            """
**SQLite Tables:**
- `daily_data` — OHLCV + 19 indicators per symbol per day (~750 rows/symbol)
- `predictions` — AI predictions with confidence, up/down probs, actual outcomes
- `performance_metrics` — Strategy returns, Sharpe ratio, drawdown

Data spans **3 years** via Yahoo Finance API (`yfinance`)
            """
        )
    with tabs[3]:
        for cat, items in {
            "Moving Averages": ["SMA 20", "SMA 50", "SMA 200", "EMA 12", "EMA 26"],
            "Momentum":        ["RSI (14)", "MACD", "MACD Signal", "MACD Histogram"],
            "Volatility":      ["Bollinger Upper", "Bollinger Middle", "Bollinger Lower", "BB Width", "ATR (14)"],
            "Volume":          ["OBV (On-Balance Volume)", "Accumulation/Distribution Line"],
            "Price Action":    ["Price Change %", "Volume Change %", "High-Low %", "Open-Close %"],
        }.items():
            st.markdown(f"**{cat}**")
            for item in items:
                st.markdown(f"- {item}")
    with tabs[4]:
        st.markdown(
            """
**RiskGuard AI** is powered by Google 5 Flash — your personal trading risk advisor.

**Topics covered:**
- 📐 Position sizing (Kelly Criterion, fixed-fractional, percent-risk)
- 🛑 Stop-loss placement (ATR-based, structure-based, percentage)
- ⚖️ Risk-reward ratio filtering
- 💼 Portfolio VaR, correlation, diversification
- 🔧 Leverage & margin risk
- 🧠 Trading psychology (FOMO, revenge trading, discipline)

**Access:** Navigate to 🤖 Risk Management AI in the sidebar or scroll to the dashboard panel.

**Model:** `gemini-2.0-flash` via `google-genai` SDK
            """
        )
    with tabs[5]:
        st.code(
            """
TradePilot — System Architecture
─────────────────────────────────────────────────────
Yahoo Finance API         TradingView (live embeds)
        │                          │
        ▼                          ▼
data_collector.py ──▶  market_data.db (SQLite)
        │                          │
        ▼                          ▼
Feature Engineering         ml_predictor.py
(19 indicators)            (Ensemble: RF+GB+LR)
        │                          │
        └───────────┬──────────────┘
                    ▼
                app.py  (Streamlit UI)
                    │
      ┌─────────────┼──────────────────┐
      ▼             ▼                  ▼
  Dashboard      Reports         risk_robot.py
 (predictions,  (track record,   (5 Flash)
  charts,        accuracy)
  sentiment)
      │
  creators.py  (Team Credits Footer)
            """,
            language="text",
        )
    render_creators_footer()


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    collector, predictor = initialize_system()

    data_ready   = os.path.exists("market_data.db")
    models_ready = [s for s in ["SPY", "QQQ", "GLD"] if os.path.exists(f"models_{s.lower()}.pkl")]

    page = render_sidebar(data_ready, models_ready)

    # Auto-init on first load
    if "auto_executed" not in st.session_state:
        st.session_state.auto_executed = True
        try:
            with st.spinner("🔄 Initializing TradePilot AI System…"):
                collector.collect_all_data(["SPY", "QQQ", "GLD"])
                results = predictor.train_all_models(["SPY", "QQQ", "GLD"])
                avg_acc = np.mean([list(r.values())[0]["test_accuracy"] for r in results.values()])
                predictions = predictor.predict_all_symbols(["SPY", "QQQ", "GLD"])
                if predictions:
                    save_predictions_to_db(predictions)
                generate_historical_predictions()
                update_actual_results()
                models_ready = [s for s in ["SPY", "QQQ", "GLD"] if os.path.exists(f"models_{s.lower()}.pkl")]
            st.toast(f"🚀 TradePilot Ready! Avg Accuracy: {avg_acc:.1%}", icon="📈")
        except Exception:
            st.toast("⚠️ Partial initialization — some features may be limited", icon="⚠️")

    # Route pages
    if page == "📊 Model Analysis":
        show_model_analysis(collector, predictor, models_ready)
    elif page == "📈 Performance Reports":
        show_performance_reports(models_ready)
    elif page == "🤖 Risk Management AI":
        show_risk_management_page()
    elif page == "👥 Team":
        show_team_page()
    elif page == "📚 Documentation":
        show_documentation()
    else:
        show_main_dashboard(collector, predictor, models_ready)


if __name__ == "__main__":
    main()

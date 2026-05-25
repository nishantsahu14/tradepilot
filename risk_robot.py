import requests
import streamlit as st
from datetime import datetime
import re

GEMINI_API_KEY = "AIzaSyACN3Cl-z3EZd4So_Z6q7Ud61c6oGu1e44"
GEMINI_MODEL = "gemini-2.5-flash"

RISK_SYSTEM_PROMPT = """You are RiskGuard AI — an elite risk management assistant built for active traders and investors.
Your expertise covers:
• Position sizing: Kelly Criterion, fixed-fractional, percent-risk methods
• Stop-loss & take-profit placement (ATR-based, support/resistance, percentage)
• Risk-reward ratio analysis and trade filtering
• Portfolio-level risk: VaR, max drawdown, correlation, diversification
• Leverage and margin risk management
• Trading psychology: discipline, FOMO, revenge-trading prevention

Style rules:
- Be concise, sharp, and data-driven. No fluff.
- Use bullet points. Give concrete numbers and formulas where possible.
- Keep responses under 220 words.
- End every response with a KEY TAKEAWAY line.
- Never give financial advice — frame as educational risk principles."""

QUICK_PROMPTS = [
    "What's the 2% rule for position sizing?",
    "How do I set an ATR-based stop-loss?",
    "What risk-reward ratio should I target?",
    "How much leverage is safe for beginners?",
    "How to calculate portfolio VaR?",
    "How do I limit max drawdown?",
]


def call_gemini(user_message, history):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + GEMINI_MODEL
        + ":generateContent?key="
        + GEMINI_API_KEY
    )
    messages = []
    for turn in history[-8:]:
        role = "user" if turn["role"] == "user" else "model"
        messages.append({"role": role, "parts": [{"text": turn["content"]}]})
    messages.append({"role": "user", "parts": [{"text": user_message}]})
    payload = {
        "system_instruction": {"parts": [{"text": RISK_SYSTEM_PROMPT}]},
        "contents": messages,
        "generationConfig": {"temperature": 0.65, "maxOutputTokens": 512},
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text, True
    except requests.exceptions.HTTPError:
        try:
            err = resp.json().get("error", {}).get("message", "HTTP error")
        except Exception:
            err = str(resp.status_code)
        return "API Error: " + err, False
    except requests.exceptions.Timeout:
        return "Request timed out. Please try again.", False
    except Exception as e:
        return "Error: " + str(e), False


def check_api_online():
    if "rg_api_online" in st.session_state:
        return st.session_state.rg_api_online
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + GEMINI_MODEL
        + ":generateContent?key="
        + GEMINI_API_KEY
    )
    payload = {
        "contents": [{"role": "user", "parts": [{"text": "hi"}]}],
        "generationConfig": {"maxOutputTokens": 5},
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        online = resp.status_code == 200
    except Exception:
        online = False
    st.session_state.rg_api_online = online
    return online


def fmt(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    lines = text.split("\n")
    out = []
    for line in lines:
        line = line.strip()
        if line.startswith("*") or line.startswith("-"):
            out.append("<span style='display:block;padding-left:1em;'>" + line + "</span>")
        elif line == "":
            out.append("<br>")
        else:
            out.append("<span style='display:block;'>" + line + "</span>")
    return "".join(out)


def render_risk_robot(compact=False):
    if "risk_history" not in st.session_state:
        st.session_state.risk_history = [
            {
                "role": "model",
                "content": (
                    "Hello! I am RiskGuard AI, your personal risk management advisor.\n\n"
                    "I can help you with:\n"
                    "- Position sizing — How much to risk per trade\n"
                    "- Stop-loss strategies — Where to cut losses\n"
                    "- Risk-reward ratios — Is this trade worth taking?\n"
                    "- Portfolio risk — Diversification and drawdown limits\n"
                    "- Leverage and margin — Staying safe with borrowed capital\n\n"
                    "Ask me anything!"
                ),
                "timestamp": datetime.now().strftime("%H:%M"),
            }
        ]

    api_online = check_api_online()
    status_color = "#38ef7d" if api_online else "#f87171"
    status_text = "ONLINE" if api_online else "OFFLINE"

    st.markdown(
        """
        <style>
        .rg-header {
            background: linear-gradient(135deg, #1e1b4b, #312e81);
            border: 1px solid rgba(99,179,237,0.25);
            border-radius: 18px 18px 0 0;
            padding: 1rem 1.4rem;
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }
        .rg-chat {
            background: rgba(0,0,0,0.28);
            border-left: 1px solid rgba(99,179,237,0.12);
            border-right: 1px solid rgba(99,179,237,0.12);
            padding: 1.1rem 1.3rem;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 0.85rem;
        }
        .rg-bubble-ai {
            background: rgba(99,179,237,0.07);
            border: 1px solid rgba(99,179,237,0.16);
            border-radius: 4px 14px 14px 14px;
            padding: 0.85rem 1rem;
            color: rgba(255,255,255,0.88);
            font-size: 0.84rem;
            line-height: 1.6;
            max-width: 94%;
        }
        .rg-bubble-user {
            background: linear-gradient(135deg, rgba(37,99,235,0.2), rgba(124,58,237,0.2));
            border: 1px solid rgba(124,58,237,0.25);
            border-radius: 14px 4px 14px 14px;
            padding: 0.85rem 1rem;
            color: white;
            font-size: 0.84rem;
            line-height: 1.6;
            max-width: 82%;
        }
        .rg-label {
            font-size: 0.61rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            margin-bottom: 3px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="rg-header">
          <div style="font-size:1.9rem;">🤖</div>
          <div style="flex:1;">
            <div style="font-size:1.05rem; font-weight:800; color:white;">RiskGuard AI</div>
            <div style="font-size:0.7rem; color:rgba(255,255,255,0.4);">
              Gemini 1.5 Flash &nbsp;·&nbsp; Risk Management Expert
            </div>
          </div>
          <div style="border:1px solid {status_color}88; border-radius:20px; padding:3px 14px;
                      font-size:0.68rem; color:{status_color}; font-weight:700;
                      background:rgba(0,0,0,0.2);">
            ● {status_text}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    max_h = "300px" if compact else "420px"
    chat_html = '<div class="rg-chat" style="max-height:' + max_h + ';">'
    for msg in st.session_state.risk_history:
        content = fmt(msg["content"])
        ts = msg.get("timestamp", "")
        if msg["role"] == "model":
            chat_html += (
                '<div>'
                '<div class="rg-label" style="color:rgba(99,179,237,0.7);">🤖 RISKGUARD &nbsp;' + ts + '</div>'
                '<div class="rg-bubble-ai">' + content + '</div>'
                '</div>'
            )
        else:
            chat_html += (
                '<div style="display:flex;flex-direction:column;align-items:flex-end;">'
                '<div class="rg-label" style="color:rgba(168,85,247,0.8);">YOU &nbsp;' + ts + ' 👤</div>'
                '<div class="rg-bubble-user">' + content + '</div>'
                '</div>'
            )
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

    st.markdown(
        "<p style='font-size:0.72rem; color:rgba(255,255,255,0.35); font-weight:700;"
        " margin:0.7rem 0 0.3rem; letter-spacing:0.08em;'>⚡ QUICK QUESTIONS</p>",
        unsafe_allow_html=True,
    )
    cols = st.columns(3)
    for idx, prompt in enumerate(QUICK_PROMPTS):
        with cols[idx % 3]:
            if st.button(prompt, key="rg_quick_" + str(idx), use_container_width=True):
                st.session_state["_rg_prefill"] = prompt
                st.rerun()

    prefill = st.session_state.pop("_rg_prefill", "")
    col_in, col_btn = st.columns([5, 1])
    with col_in:
        user_input = st.text_input(
            "msg",
            value=prefill,
            key="rg_input",
            placeholder="e.g. I have $15,000. How much should I risk per trade?",
            label_visibility="collapsed",
        )
    with col_btn:
        send = st.button("Send", key="rg_send", use_container_width=True, type="primary")

    if len(st.session_state.risk_history) > 1:
        if st.button("Clear Chat", key="rg_clear"):
            st.session_state.risk_history = st.session_state.risk_history[:1]
            st.session_state.pop("rg_api_online", None)
            st.rerun()

    if send and user_input.strip():
        user_msg = user_input.strip()
        st.session_state.risk_history.append(
            {"role": "user", "content": user_msg, "timestamp": datetime.now().strftime("%H:%M")}
        )
        with st.spinner("Analyzing risk parameters..."):
            history_for_api = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.risk_history[1:-1]
            ]
            reply, success = call_gemini(user_msg, history_for_api)
            if success:
                st.session_state.rg_api_online = True
        st.session_state.risk_history.append(
            {"role": "model", "content": reply, "timestamp": datetime.now().strftime("%H:%M")}
        )
        st.rerun()

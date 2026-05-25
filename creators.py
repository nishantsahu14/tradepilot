"""
creators.py — TradePilot Team Credits
Renders the professional team footer.
"""

import streamlit as st

TEAM = [
    {"name": "Aditya Sharma",    "role": "ML Engineer",         "emoji": "🧠"},
    {"name": "Aditya Pandey",    "role": "Backend Developer",        "emoji": "📊"},
    {"name": "Anuj Pathak",      "role": "ML Engineer",    "emoji": "⚙️"},
    {"name": "Adarsh Sondhiya",  "role": "Frontend Developer",   "emoji": "🎨"},
    {"name": "Mohneesh Jangde", "role": "Quant Analyst",        "emoji": "📈"},
    {"name": "Nishant Sahu",     "role": "Frontend Developer",   "emoji": "🤖"},
]


def render_creators_footer():
    chips_html = ""
    for member in TEAM:
        chips_html += f"""
        <div style="background:rgba(99,179,237,0.08); border:1px solid rgba(99,179,237,0.22);
                    border-radius:12px; padding:0.75rem 1rem; text-align:center;">
          <div style="font-size:1.4rem;">{member['emoji']}</div>
          <div style="font-size:0.88rem; font-weight:700; color:white; margin-top:4px;">{member['name']}</div>
          <div style="font-size:0.7rem; color:rgba(255,255,255,0.4); margin-top:2px;">{member['role']}</div>
        </div>"""

    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#0a0a1a,#111827);
                    border:1px solid rgba(99,179,237,0.2); border-radius:20px;
                    padding:2rem 2.5rem; margin-top:2.5rem; color:white;
                    position:relative; overflow:hidden;">
          <!-- top gradient line -->
          <div style="position:absolute; top:0; left:0; right:0; height:2px;
                      background:linear-gradient(90deg,transparent,#63b3ed,#a855f7,#63b3ed,transparent);"></div>

          <div style="font-size:0.68rem; text-transform:uppercase; letter-spacing:3px;
                      color:#63b3ed; text-align:center; margin-bottom:1.2rem;">✨ Developed By</div>

          <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:0.8rem; margin-bottom:1rem;">
            {chips_html}
          </div>

          <div style="text-align:center; font-size:0.72rem; color:rgba(255,255,255,0.28);
                      margin-top:0.8rem; padding-top:0.8rem;
                      border-top:1px solid rgba(255,255,255,0.07);">
            B.Tech 4th Year &nbsp;|&nbsp; Major Project &nbsp;|&nbsp;
            Computer Science &amp; Engineering &nbsp;|&nbsp; © 2025 TradePilot Team
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

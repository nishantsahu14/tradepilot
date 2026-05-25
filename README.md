# ✈️ TradePilot — AI Market Intelligence

**B.Tech 4th Year Major Project — Computer Science & Engineering**

A professional AI-powered market intelligence dashboard for predicting daily directional movement of SPY, NASDAQ (QQQ), and GLD using ensemble machine learning, with real-time TradingView charts and a Gemini-powered risk management chatbot.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

The system auto-initializes on first run — it downloads 3 years of market data, trains models, and generates predictions automatically.

---

## 📁 Project Structure

```
TradePilot/
├── app.py                  # Main Streamlit application (UI + routing)
├── data_collector.py       # Yahoo Finance data pipeline + 19 indicators
├── ml_predictor.py         # Ensemble ML (Random Forest, Gradient Boost, Logistic)
├── risk_robot.py           # RiskGuard AI — Gemini 2.0 Flash chatbot
├── creators.py             # Team credits footer component
├── requirements.txt        # Python dependencies
├── market_data.db          # SQLite database (auto-created)
├── models_spy.pkl          # Trained models for SPY
├── models_qqq.pkl          # Trained models for NASDAQ (QQQ)
└── models_gld.pkl          # Trained models for GLD
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔮 AI Predictions | Ensemble UP/DOWN signals with confidence % for SPY, NASDAQ, GLD |
| 📈 Live Charts | Embedded TradingView charts with direct links to interactive charts |
| 🤖 RiskGuard AI | Google Gemini 2.0 Flash chatbot for risk management questions |
| 📊 Performance | 10-day accuracy tracking with per-symbol breakdown |
| 🧠 Model Analysis | RSI, MACD, Bollinger Bands visualizations |
| 👥 Team Page | Dedicated team credits page |

---

## 🧠 ML Pipeline

1. **Data Collection** — `yfinance` downloads 3 years OHLCV for SPY, QQQ, GLD
2. **Feature Engineering** — 19 technical indicators (SMA, EMA, RSI, MACD, BB, ATR, OBV…)
3. **Ensemble Training** — Random Forest + Gradient Boosting + Logistic Regression (80/20 temporal split)
4. **Prediction** — Majority probability vote → UP/DOWN + confidence %

---

## 🤖 RiskGuard AI

Powered by **Google Gemini 2.0 Flash** via the `google-genai` SDK.

Topics:
- Position sizing (Kelly Criterion, 2% rule)
- Stop-loss placement (ATR-based, structure-based)
- Risk-reward ratios
- Portfolio VaR and max drawdown
- Leverage and margin management
- Trading psychology

---

## 👥 Team

| Name | Role |
|------|------|
| Aditya Sharma | ML Engineer |
| Aditya Pandey | Data Engineer |
| Anuj Pathak | Backend Developer |
| Adarsh Sondhiya | Frontend Developer |
| Moohneesh Jangde | Quant Analyst |
| Nishant Shau | AI / NLP Developer |

---

*© 2025 TradePilot Team — B.Tech CSE Major Project*

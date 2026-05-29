```python
import streamlit as st
import yfinance as yf
import pandas as pd
from scipy.signal import argrelextrema
import numpy as np

st.set_page_config(
    page_title="Golden Alpha",
    page_icon="📈",
    layout="wide",
)

# -----------------------------
# PREMIUM DARK THEME
# -----------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #000000;
    color: #d4af37;
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #000000;
}

h1, h2, h3, h4 {
    color: #d4af37;
}

.stTextInput > div > div > input {
    background-color: #111111;
    color: #d4af37;
    border: 1px solid #d4af37;
    border-radius: 10px;
}

.stButton > button {
    background-color: #d4af37;
    color: black;
    border-radius: 12px;
    font-weight: 700;
    border: none;
    padding: 0.6rem 1.5rem;
}

.stock-card {
    background: #111111;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #d4af37;
    margin-bottom: 20px;
    box-shadow: 0 0 20px rgba(212,175,55,0.15);
}

.green {
    color: #22c55e;
    font-weight: 700;
}

.red {
    color: #ef4444;
    font-weight: 700;
}

.metric {
    font-size: 18px;
    margin-top: 8px;
}

.section-title {
    font-size: 28px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)


def analyze_local_minima(ticker: str):

    df = yf.Ticker(ticker).history(period="60d")

    if df.empty:
        return None

    df = df[["Close"]].copy()
    df.index = pd.to_datetime(df.index).tz_localize(None)

    local_min_indices = argrelextrema(
        df["Close"].values,
        np.less_equal,
        order=2
    )[0]

    local_min_dates = df.index[local_min_indices]

    today = df.index[-1]

    windows = {
        "1 day": 1,
        "3 days": 3,
        "5 days": 5
    }

    results = {}

    for label, days in windows.items():

        cutoff = today - pd.Timedelta(days=days)

        minima_in_window = [
            d for d in local_min_dates if d >= cutoff
        ]

        if minima_in_window:

            most_recent = max(minima_in_window)
            price_at_min = df.loc[most_recent, "Close"]

            results[label] = {
                "found": True,
                "date": most_recent.strftime("%Y-%m-%d"),
                "price": round(price_at_min, 2),
                "current_price": round(df["Close"].iloc[-1], 2),
                "change_pct": round(
                    (
                        df["Close"].iloc[-1] - price_at_min
                    ) / price_at_min * 100,
                    2,
                ),
            }

        else:
            results[label] = {
                "found": False
            }

    results["_meta"] = {
        "current_price": round(df["Close"].iloc[-1], 2)
    }

    return results


# -----------------------------
# UI
# -----------------------------

st.title("📈 Golden Alpha")
st.markdown(
    "<div class='section-title'>Luxury Quant Scanner</div>",
    unsafe_allow_html=True
)

default_tickers = (
    "FIX, AVGO, CEG, AGX, SNDK, VRT, CLS, CCJ,"
    " POWL, NVT, RMBS, FN, EOSE, OKLO, JOBY,"
    " INOD, STRL, XOM, CAT, ANET, LMT, PWR, SMR"
)

ticker_input = st.text_input(
    "Enter stock tickers separated by commas",
    value=default_tickers
)

if st.button("Analyze Stocks"):

    tickers = [
        t.strip().upper()
        for t in ticker_input.split(",")
        if t.strip()
    ]

    for ticker in tickers:

        results = analyze_local_minima(ticker)

        if not results:
            continue

        hit = any(
            results[w]["found"]
            for w in ["1 day", "3 days", "5 days"]
        )

        if not hit:
            continue

        current_price = results["_meta"]["current_price"]

        st.markdown(
            f"""
            <div class='stock-card'>
                <h2>{ticker}</h2>
                <div class='metric'>
                    Current Price:
                    <span class='green'>
                        ${current_price}
                    </span>
                </div>
            """,
            unsafe_allow_html=True
        )

        for window in ["1 day", "3 days", "5 days"]:

            r = results[window]

            if r["found"]:

                color = "green" if r["change_pct"] >= 0 else "red"

                st.markdown(
                    f"""
                    <div class='metric'>
                        ✅ Local minimum in last {window}
                        at ${r['price']}
                        on {r['date']}
                        —
                        <span class='{color}'>
                            {r['change_pct']}%
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("</div>", unsafe_allow_html=True)
```

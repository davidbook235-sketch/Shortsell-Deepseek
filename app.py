import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scanner.auth import login_angelone
from scanner.data_fetcher import get_intraday_data
from scanner.indicators import calculate_indicators
from scanner.short_scanner import scan_short_candidates

st.set_page_config(page_title="Angel One Intraday Short Scanner", page_icon="📉", layout="wide")

st.title("📉 Angel One Intraday Short Selling Scanner")
st.markdown("**⚠️ नोट:** सभी पोज़िशन 3:15 PM से पहले स्क्वायर ऑफ करें। केवल F&O स्टॉक्स में शॉर्ट सेलिंग की अनुमति है।")

# F&O स्टॉक्स की लिस्ट (आप इसे NSE से डायनामिकली लोड कर सकते हैं)
FNO_STOCKS = [
    {"symbol": "RELIANCE", "token": "2885"},
    {"symbol": "TATAMOTORS", "token": "3456"},
    {"symbol": "SBIN", "token": "3045"},
    {"symbol": "HINDALCO", "token": "1363"},
    {"symbol": "TATASTEEL", "token": "3499"},
    {"symbol": "JSWSTEEL", "token": "11723"},
    {"symbol": "VEDL", "token": "3063"},
    {"symbol": "PNB", "token": "10666"},
    {"symbol": "BANKBARODA", "token": "4668"},
    {"symbol": "CANBK", "token": "10794"},
]

with st.sidebar:
    st.header("🔑 Angel One Login")
    api_key = st.text_input("API Key", type="password")
    client_code = st.text_input("Client Code")
    password = st.text_input("Password", type="password")
    totp_secret = st.text_input("TOTP Secret", type="password")

    st.markdown("---")
    st.header("⚙️ Settings")
    min_score = st.slider("Minimum Score", 3, 5, 3)
    interval = st.selectbox("Timeframe", ["FIVE_MINUTE", "FIFTEEN_MINUTE"], index=0)

    run_scan = st.button("🚀 Run Scanner", type="primary")

if run_scan:
    if not all([api_key, client_code, password, totp_secret]):
        st.error("कृपया सभी लॉगिन क्रेडेंशियल भरें।")
        st.stop()

    try:
        with st.spinner("Angel One में लॉगिन हो रहा है..."):
            obj = login_angelone(api_key, client_code, password, totp_secret)
        st.success("✅ लॉगिन सफल!")

        with st.spinner("इंट्राडे शॉर्ट कैंडिडेट्स स्कैन हो रहे हैं..."):
            results = scan_short_candidates(obj, FNO_STOCKS, interval=interval)

        if results.empty:
            st.warning("वर्तमान मानदंडों के साथ कोई शॉर्ट कैंडिडेट नहीं मिला।")
        else:
            filtered = results[results["Score"] >= min_score]
            st.subheader("🎯 इंट्राडे शॉर्ट कैंडिडेट्स")
            st.dataframe(
                filtered.sort_values("Score", ascending=False),
                use_container_width=True,
                hide_index=True
            )

            if not filtered.empty:
                top_symbol = filtered.iloc[0]["Symbol"]
                top_token = next((s["token"] for s in FNO_STOCKS if s["symbol"] == top_symbol), None)

                if top_token:
                    st.subheader(f"📈 चार्ट: {top_symbol}")
                    df = get_intraday_data(obj, top_token, interval=interval, days=3)
                    df = calculate_indicators(df)

                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=df.index, open=df["open"], high=df["high"],
                        low=df["low"], close=df["close"], name="Price"
                    ))
                    fig.add_trace(go.Scatter(x=df.index, y=df["VWAP"], name="VWAP", line=dict(color="orange")))
                    fig.add_trace(go.Scatter(x=df.index, y=df["EMA_9"], name="EMA 9", line=dict(color="blue")))
                    fig.add_trace(go.Scatter(x=df.index, y=df["EMA_21"], name="EMA 21", line=dict(color="purple")))
                    st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"त्रुटि: {e}")
else:
    st.info("👈 कृपया साइडबार में Angel One लॉगिन क्रेडेंशियल भरें और **Run Scanner** पर क्लिक करें।")

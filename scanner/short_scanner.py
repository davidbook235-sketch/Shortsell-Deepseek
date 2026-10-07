import pandas as pd
from scanner.data_fetcher import get_intraday_data
from scanner.indicators import calculate_indicators

def scan_short_candidates(obj, stock_list: list, interval: str = "FIVE_MINUTE"):
    """इंट्राडे शॉर्ट सेलिंग कैंडिडेट्स स्कैन करें"""
    results = []

    for stock in stock_list:
        symbol = stock["symbol"]
        token = stock["token"]

        df = get_intraday_data(obj, token, interval=interval, days=3)
        if df.empty:
            continue

        df = calculate_indicators(df)
        if df.empty or len(df) < 30:
            continue

        latest = df.iloc[-1]

        conditions = {
            "RSI_below_30": latest["RSI_9"] < 30,
            "Price_below_VWAP": latest["close"] < latest["VWAP"],
            "EMA9_below_EMA21": latest["EMA_9"] < latest["EMA_21"],
            "SuperTrend_Bearish": latest["SuperTrend_Dir"] == "Bearish",
            "Volume_Spike": latest["volume"] > latest["Volume_SMA"] * 1.5
        }

        score = sum(conditions.values())

        if score >= 3:
            results.append({
                "Symbol": symbol,
                "LTP": round(latest["close"], 2),
                "RSI_9": round(latest["RSI_9"], 2),
                "VWAP": round(latest["VWAP"], 2),
                "Score": score,
                "Signal": "SHORT" if score >= 4 else "WATCH",
                "Conditions": ", ".join([k for k, v in conditions.items() if v])
            })

    return pd.DataFrame(results)

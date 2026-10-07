import pandas as pd
import numpy as np
import ta

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """इंट्राडे शॉर्ट सेलिंग के लिए तकनीकी संकेतकों की गणना करें"""
    if df.empty or len(df) < 30:
        return df

    # RSI (9) - इंट्राडे के लिए बेहतर
    df["RSI_9"] = ta.momentum.RSIIndicator(df["close"], window=9).rsi()

    # VWAP (Volume Weighted Average Price)
    df["VWAP"] = (df["volume"] * (df["high"] + df["low"] + df["close"]) / 3).cumsum() / df["volume"].cumsum()

    # EMA 9 और EMA 21
    df["EMA_9"] = ta.trend.EMAIndicator(df["close"], window=9).ema_indicator()
    df["EMA_21"] = ta.trend.EMAIndicator(df["close"], window=21).ema_indicator()

    # SuperTrend (10, 3)
    st = ta.trend.SuperTrendIndicator(df["high"], df["low"], df["close"], window=10, multiplier=3)
    df["SuperTrend"] = st.super_trend()
    df["SuperTrend_Dir"] = np.where(df["close"] < df["SuperTrend"], "Bearish", "Bullish")

    # Volume SMA
    df["Volume_SMA"] = df["volume"].rolling(window=20).mean()

    return df

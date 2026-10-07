import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# प्रमुख Nifty सेक्टोरल इंडेक्स के टिकर
SECTOR_TICKERS = {
    "Nifty Auto": "^CNXAUTO",
    "Nifty Bank": "^NSEBANK",
    "Nifty IT": "^CNXIT",
    "Nifty Metal": "^CNXMETAL",
    "Nifty Pharma": "^CNXPHARMA",
    "Nifty PSU Bank": "^CNXPSUBANK",
    "Nifty Realty": "^CNXREALTY",
    "Nifty Energy": "^CNXENERGY",
    "Nifty FMCG": "^CNXFMCG",
    "Nifty Financial Services": "NIFTY_FIN_SERVICE.NS"
}

def get_sector_data(period="3mo"):
    """सेक्टर इंडेक्स का डेटा प्राप्त करें और रिटर्न की गणना करें"""
    end = datetime.now()
    start = end - timedelta(days=90)  # 3 महीने का डेटा
    
    sector_returns = {}
    for name, ticker in SECTOR_TICKERS.items():
        try:
            df = yf.download(ticker, start=start, end=end, progress=False)
            if not df.empty:
                # 1 महीने का रिटर्न
                if len(df) >= 20:
                    ret_1m = (df['Close'].iloc[-1] / df['Close'].iloc[-20] - 1) * 100
                else:
                    ret_1m = 0
                # 3 महीने का रिटर्न
                ret_3m = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
                sector_returns[name] = {
                    'return_1m': ret_1m,
                    'return_3m': ret_3m,
                    'current_price': df['Close'].iloc[-1]
                }
        except Exception as e:
            print(f"Error fetching {name}: {e}")
    
    return pd.DataFrame(sector_returns).T

def get_weak_sectors(sector_df, top_n=3):
    """सबसे कमजोर सेक्टर की पहचान करें (सबसे कम रिटर्न)"""
    if sector_df.empty:
        return []
    
    # 3 महीने के रिटर्न के आधार पर सॉर्ट करें
    sorted_sectors = sector_df.sort_values('return_3m', ascending=True)
    weak_sectors = sorted_sectors.head(top_n).index.tolist()
    return weak_sectors

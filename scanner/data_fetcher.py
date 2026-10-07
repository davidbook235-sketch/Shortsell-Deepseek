import pandas as pd
from datetime import datetime, timedelta

def get_intraday_data(obj, symbol_token: str, exchange: str = "NSE", interval: str = "FIVE_MINUTE", days: int = 5):
    """Angel One से इंट्राडे कैंडल डेटा प्राप्त करें"""
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)

    params = {
        "exchange": exchange,
        "symboltoken": symbol_token,
        "interval": interval,
        "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
        "todate": to_date.strftime("%Y-%m-%d %H:%M")
    }

    try:
        response = obj.getCandleData(params)
        if response and response.get("status") and response.get("data"):
            df = pd.DataFrame(
                response["data"],
                columns=["datetime", "open", "high", "low", "close", "volume"]
            )
            df["datetime"] = pd.to_datetime(df["datetime"])
            df.set_index("datetime", inplace=True)
            df = df.astype(float)
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching {symbol_token}: {e}")
        return pd.DataFrame()

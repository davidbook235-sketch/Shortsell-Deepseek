import pandas as pd
import numpy as np
import ta
from nselib import capital_market

def get_stock_data(symbol, period="3mo"):
    """NSE से स्टॉक डेटा प्राप्त करें"""
    try:
        df = capital_market.price_volume_data(symbol=symbol, period=period)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        # कॉलम नाम को स्टैंडर्डाइज़ करें
        df.columns = [col.strip().title() for col in df.columns]
        return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return pd.DataFrame()

def calculate_indicators(df):
    """तकनीकी इंडिकेटर्स की गणना करें"""
    if df.empty or len(df) < 50:
        return df
    
    # RSI
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    
    # MACD
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['MACD_diff'] = macd.macd_diff()
    
    # Moving Averages
    df['SMA_20'] = ta.trend.SMAIndicator(df['Close'], window=20).sma_indicator()
    df['SMA_50'] = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
    
    # Bollinger Bands
    bb = ta.volatility.BollingerBands(df['Close'])
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    
    # Volume
    df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
    
    return df

def scan_short_candidates(stock_list, weak_sectors):
    """वीक सेक्टर के स्टॉक्स में शॉर्ट सेलिंग कैंडिडेट्स स्कैन करें"""
    results = []
    
    for symbol in stock_list:
        try:
            df = get_stock_data(symbol)
            if df.empty:
                continue
            
            df = calculate_indicators(df)
            if df.empty or len(df) < 50:
                continue
            
            latest = df.iloc[-1]
            
            # शॉर्ट सेलिंग कंडीशन्स
            conditions = {
                'RSI_oversold': latest['RSI'] < 30,
                'MACD_bearish': latest['MACD'] < latest['MACD_signal'],
                'Below_SMA20': latest['Close'] < latest['SMA_20'],
                'Below_SMA50': latest['Close'] < latest['SMA_50'],
                'Near_BB_lower': latest['Close'] <= latest['BB_lower'] * 1.02,
                'Volume_spike': latest['Volume'] > latest['Volume_SMA'] * 1.5
            }
            
            # स्कोर की गणना (प्रत्येक कंडीशन के लिए 1 पॉइंट)
            score = sum(conditions.values())
            
            # अगर कम से कम 3 कंडीशन पूरी होती हैं
            if score >= 3:
                results.append({
                    'Symbol': symbol,
                    'Sector': 'Weak Sector',  # यह वीक सेक्टर लिस्ट से मैप किया जाएगा
                    'Price': round(latest['Close'], 2),
                    'RSI': round(latest['RSI'], 2),
                    'MACD': round(latest['MACD'], 2),
                    'Score': score,
                    'Signal': 'SHORT' if score >= 4 else 'WATCH',
                    'Conditions': ', '.join([k for k, v in conditions.items() if v])
                })
        except Exception as e:
            print(f"Error scanning {symbol}: {e}")
    
    return pd.DataFrame(results)

import pandas as pd
import numpy as np

def backtest_short_strategy(df, initial_capital=100000, stop_loss_pct=5, target_pct=10):
    """
    सिंपल शॉर्ट सेलिंग बैकटेस्ट
    - जब RSI < 30 और MACD bearish हो तो शॉर्ट एंट्री
    - स्टॉप लॉस: एंट्री प्राइस से 5% ऊपर
    - टारगेट: एंट्री प्राइस से 10% नीचे
    """
    if df.empty or len(df) < 50:
        return None
    
    capital = initial_capital
    position = None
    trades = []
    
    for i in range(1, len(df)):
        current = df.iloc[i]
        prev = df.iloc[i-1]
        
        # एंट्री कंडीशन
        if position is None:
            if (current['RSI'] < 30 and 
                current['MACD'] < current['MACD_signal'] and
                current['Close'] < current['SMA_20']):
                position = {
                    'entry_price': current['Close'],
                    'entry_date': df.index[i],
                    'stop_loss': current['Close'] * (1 + stop_loss_pct/100),
                    'target': current['Close'] * (1 - target_pct/100),
                    'quantity': capital // current['Close']  # पूरा कैपिटल इस्तेमाल करें
                }
        
        # एग्ज़िट कंडीशन
        elif position is not None:
            exit_price = None
            exit_reason = None
            
            # स्टॉप लॉस हिट
            if current['High'] >= position['stop_loss']:
                exit_price = position['stop_loss']
                exit_reason = 'Stop Loss'
            # टारगेट हिट
            elif current['Low'] <= position['target']:
                exit_price = position['target']
                exit_reason = 'Target'
            # अगर RSI 50 से ऊपर हो जाए तो एग्ज़िट
            elif current['RSI'] > 50:
                exit_price = current['Close']
                exit_reason = 'RSI Exit'
            
            if exit_price:
                # शॉर्ट सेलिंग में प्रॉफिट = (एंट्री - एग्ज़िट) * क्वांटिटी
                pnl = (position['entry_price'] - exit_price) * position['quantity']
                capital += pnl
                
                trades.append({
                    'entry_date': position['entry_date'],
                    'exit_date': df.index[i],
                    'entry_price': position['entry_price'],
                    'exit_price': exit_price,
                    'quantity': position['quantity'],
                    'pnl': round(pnl, 2),
                    'return_pct': round((pnl / (position['entry_price'] * position['quantity'])) * 100, 2),
                    'exit_reason': exit_reason
                })
                position = None
    
    if not trades:
        return None
    
    trades_df = pd.DataFrame(trades)
    
    # परफॉर्मेंस मेट्रिक्स
    total_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['pnl'] > 0])
    losing_trades = len(trades_df[trades_df['pnl'] <= 0])
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
    total_pnl = trades_df['pnl'].sum()
    avg_return = trades_df['return_pct'].mean()
    
    # मैक्स ड्रॉडाउन
    cumulative = trades_df['pnl'].cumsum() + initial_capital
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max * 100
    max_drawdown = drawdown.min()
    
    metrics = {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': round(win_rate, 2),
        'total_pnl': round(total_pnl, 2),
        'avg_return_per_trade': round(avg_return, 2),
        'max_drawdown': round(max_drawdown, 2),
        'final_capital': round(capital, 2),
        'total_return_pct': round((capital - initial_capital) / initial_capital * 100, 2)
    }
    
    return metrics, trades_df

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scanner.sector_analysis import get_sector_data, get_weak_sectors, SECTOR_TICKERS
from scanner.short_scanner import scan_short_candidates, get_stock_data, calculate_indicators
from scanner.backtest import backtest_short_strategy
from nselib import capital_market

# पेज कॉन्फ़िगरेशन
st.set_page_config(
    page_title="Short Selling Scanner - India",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# मोबाइल-फ्रेंडली CSS
st.markdown("""
<style>
    .main { padding: 1rem; }
    .stButton>button { width: 100%; }
    @media (max-width: 768px) {
        .stColumn { padding: 0.5rem !important; }
    }
</style>
""", unsafe_allow_html=True)

st.title("📉 Indian Stock Market Short Selling Scanner")
st.markdown("---")

# साइडबार
with st.sidebar:
    st.header("⚙️ Settings")
    top_n_sectors = st.slider("Number of Weak Sectors", 1, 5, 3)
    min_score = st.slider("Minimum Short Score", 3, 6, 3)
    period = st.selectbox("Data Period", ["1mo", "3mo", "6mo"], index=1)
    
    st.markdown("---")
    st.header("📊 Backtest Settings")
    initial_capital = st.number_input("Initial Capital (₹)", value=100000, step=10000)
    stop_loss = st.slider("Stop Loss %", 2, 10, 5)
    target = st.slider("Target %", 5, 20, 10)
    
    run_scan = st.button("🚀 Run Scanner", type="primary")

# मुख्य कंटेंट
if run_scan:
    with st.spinner("Fetching sector data..."):
        # 1. वीक सेक्टर एनालिसिस
        sector_df = get_sector_data(period)
        
        if sector_df.empty:
            st.error("Unable to fetch sector data. Please try again.")
            st.stop()
        
        st.subheader("📊 Sector Performance Analysis")
        
        # सेक्टर परफॉर्मेंस चार्ट
        fig_sector = px.bar(
            sector_df.sort_values('return_3m'),
            x=sector_df.sort_values('return_3m').index,
            y='return_3m',
            color='return_3m',
            color_continuous_scale=['red', 'yellow', 'green'],
            title="Sector Returns (3 Months)",
            labels={'x': 'Sector', 'y': 'Return (%)'}
        )
        fig_sector.update_layout(height=400)
        st.plotly_chart(fig_sector, use_container_width=True)
        
        # वीक सेक्टर की पहचान
        weak_sectors = get_weak_sectors(sector_df, top_n_sectors)
        st.success(f"🔴 Weak Sectors: {', '.join(weak_sectors)}")
        
        # 2. शॉर्ट सेलिंग स्कैनर
        with st.spinner("Scanning for short selling candidates..."):
            # Nifty 50 स्टॉक्स की लिस्ट
            try:
                nifty50_stocks = capital_market.nifty50_equity_list()
                stock_symbols = nifty50_stocks['Symbol'].tolist()
            except:
                # फॉलबैक: कुछ कॉमन स्टॉक्स
                stock_symbols = ['SBIN', 'TATAMOTORS', 'HINDALCO', 'TATASTEEL', 
                                 'JSWSTEEL', 'VEDL', 'PNB', 'BANKBARODA', 'CANBK']
            
            # स्कैन करें
            scan_results = scan_short_candidates(stock_symbols, weak_sectors)
            
            if scan_results.empty:
                st.warning("No short selling candidates found with current criteria.")
            else:
                # फ़िल्टर करें
                filtered = scan_results[scan_results['Score'] >= min_score]
                
                st.subheader("🎯 Short Selling Candidates")
                st.dataframe(
                    filtered.sort_values('Score', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
                
                # 3. बैकटेस्टिंग
                st.subheader("📈 Backtest Results")
                
                # पहले कैंडिडेट का बैकटेस्ट
                if not filtered.empty:
                    top_symbol = filtered.iloc[0]['Symbol']
                    st.info(f"Backtesting strategy on **{top_symbol}**")
                    
                    stock_df = get_stock_data(top_symbol, period="1y")
                    if not stock_df.empty:
                        stock_df = calculate_indicators(stock_df)
                        backtest_result = backtest_short_strategy(
                            stock_df, 
                            initial_capital=initial_capital,
                            stop_loss_pct=stop_loss,
                            target_pct=target
                        )
                        
                        if backtest_result:
                            metrics, trades_df = backtest_result
                            
                            # मेट्रिक्स डिस्प्ले
                            col1, col2, col3, col4 = st.columns(4)
                            col1.metric("Total Trades", metrics['total_trades'])
                            col2.metric("Win Rate", f"{metrics['win_rate']}%")
                            col3.metric("Total P&L", f"₹{metrics['total_pnl']:,}")
                            col4.metric("Max Drawdown", f"{metrics['max_drawdown']}%")
                            
                            # ट्रेड्स टेबल
                            st.dataframe(trades_df, use_container_width=True, hide_index=True)
                            
                            # इक्विटी कर्व
                            trades_df['cumulative_pnl'] = trades_df['pnl'].cumsum() + initial_capital
                            fig_equity = px.line(
                                trades_df, 
                                x='exit_date', 
                                y='cumulative_pnl',
                                title="Equity Curve",
                                labels={'exit_date': 'Date', 'cumulative_pnl': 'Capital (₹)'}
                            )
                            st.plotly_chart(fig_equity, use_container_width=True)
                        else:
                            st.warning("Not enough trades to backtest.")
else:
    st.info("👈 Settings adjust करें और **Run Scanner** पर क्लिक करें")
    
    # इंस्ट्रक्शन्स
    with st.expander("📖 How to Use"):
        st.markdown("""
        1. **Weak Sectors**: सबसे कमजोर सेक्टर की पहचान करें
        2. **Short Candidates**: उन स्टॉक्स की लिस्ट देखें जो शॉर्ट सेलिंग के लिए अच्छे हैं
        3. **Backtest**: अपनी रणनीति का ऐतिहासिक परिणाम देखें
        4. **Score**: जितना ज़्यादा स्कोर, उतना मजबूत शॉर्ट सिग्नल
        """)

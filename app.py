import streamlit as st
import pandas as pd

st.set_page_config(page_title="ATH Track System", page_icon="📈", layout="wide")
st.title("ATH Track system")
st.write("**Automated Execution Tracking System**")
st.info("Disclaimer: EDUCATIONAL PURPOSES ONLY. I am NOT a SEBI Registered Analyst. This dashboard strictly tracks my personal algorithmic logic. Do not consider this as buy/sell advice.")

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1qKxpIIoGd4skNllbua6U0AeeFt-WQjeYPMvBzS5_Qn4/export?format=csv"

@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        df.columns = ["symbol", "company_name", "ath", "live_price", "day_change", "status", "entry_price", "sl_price", "target_price", "pnl_perc", "entry_date", "exit_date"]
        return df
    except Exception as e:
        st.error(f"Google Sheet se connect karne me dikkat aayi: {e}")
        return pd.DataFrame()

df = load_data()

def safe_float(val):
    try:
        return float(val)
    except:
        return 0.0

def draw_cards(dataframe):
    # 4 columns taaki Cards chhote banein aur scrolling kam ho
    cols = st.columns(4) 
    
    for i, (index, row) in enumerate(dataframe.iterrows()):
        with cols[i % 4]:
            with st.container(border=True):
                sym = str(row['symbol']).strip()
                status = str(row['status'])
                live_price = safe_float(row['live_price'])
                ath = safe_float(row['ath'])
                
                # Calculate % Below ATH
                below_ath = round(((ath - live_price) / ath) * 100, 2) if ath > 0 else 0
                
                # Status Icon Logic
                icon = "🟢" if "ENTERED" in status else "🔴" if "SL" in status else "🎯" if "TARGET" in status else "🟡"
                
                # Compact Header
                st.markdown(f"#### {sym} {icon}")
                
                # Smart Links (TradingView, Screener, Google News)
                chart = f"https://in.tradingview.com/chart/?symbol=NSE:{sym}"
                screener = f"https://www.screener.in/company/{sym}/"
                news = f"https://www.google.com/search?q={sym}+share+news"
                
                st.markdown(f"<small>[📈 Chart]({chart}) | [📊 Data]({screener}) | [📰 News]({news})</small>", unsafe_allow_html=True)
                
                # Compact Metrics
                st.markdown(f"**LTP:** ₹{live_price} ({row['day_change']})")
                
                if "WAITING" in status:
                    st.markdown(f"**ATH:** ₹{ath} (`-{below_ath}%`)")
                    st.caption(f"Breakout: ₹{round(ath * 1.01, 2)}")
                else:
                    pnl = safe_float(row['pnl_perc'])
                    st.markdown(f"**P&L:** `{pnl}%`")
                    st.caption(f"Tgt: ₹{safe_float(row['target_price'])} | SL: ₹{safe_float(row['sl_price'])}")

if not df.empty:
    tab1, tab2 = st.tabs(["📊 Active Trades", "📜 Trade History"])

    with tab1:
        st.markdown("### Live & Ongoing Trades")
        active_df = df[df['status'].isin(["🟡 WAITING", "🟢 ENTERED"])]
        if active_df.empty:
            st.info("Abhi koi active trade ya waiting list me stock nahi hai.")
        else:
            draw_cards(active_df)

    with tab2:
        st.markdown("### Closed Trades History")
        history_df = df[df['status'].isin(["🔴 SL HIT", "🎯 TARGET HIT"])]
        if history_df.empty:
            st.info("Abhi tak koi bhi trade close nahi hui hai.")
        else:
            draw_cards(history_df)
else:
    st.warning("⚠️ Google Sheet ekdum khali hai ya URL block ho raha hai.")

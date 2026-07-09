import streamlit as st
import pandas as pd

# Page layout ko wide rakha h taaki cards acche dikhein
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

# --- CARDS DRAW KARNE KA FUNCTION ---
def draw_cards(dataframe):
    # Screen ko 3 hisso me baant rahe hain taaki grid ban sake
    cols = st.columns(3)
    
    for i, (index, row) in enumerate(dataframe.iterrows()):
        with cols[i % 3]: # Har 3 card ke baad nayi line me aayega
            with st.container(border=True): # Yeh Card ka border banayega
                
                # 1. Title & Company Name
                st.subheader(f"{row['symbol']}")
                st.caption(f"{row['company_name']}")
                
                status = str(row['status'])
                live_price = safe_float(row['live_price'])
                day_change = str(row['day_change'])
                if day_change == "nan" or day_change == "None": 
                    day_change = "0%"

                # 2. Status Badge Colors
                if "🟢" in status:
                    st.success(f"**{status}**")
                elif "🔴" in status:
                    st.error(f"**{status}**")
                elif "🎯" in status:
                    st.info(f"**{status}**")
                else:
                    st.warning(f"**{status}**")
                
                # 3. Live Price & PnL Metrics
                mc1, mc2 = st.columns(2)
                mc1.metric("Live Price", f"₹{live_price}", day_change)
                
                if "WAITING" in status:
                    mc2.metric("ATH Level", f"₹{safe_float(row['ath'])}")
                else:
                    pnl = safe_float(row['pnl_perc'])
                    # PnL ko color me dikhane ke liye delta ka use kiya h
                    mc2.metric("P&L %", f"{pnl}%", f"{pnl}%")
                
                st.divider() # Line separator
                
                # 4. Entry, SL, Target Details
                if "WAITING" not in status:
                    entry = safe_float(row['entry_price'])
                    tgt = safe_float(row['target_price'])
                    sl = safe_float(row['sl_price'])
                    
                    st.markdown(f"**Entry:** ₹{entry} | **Target:** ₹{tgt} | **SL:** ₹{sl}")
                    
                    if "ENTERED" in status:
                        st.caption(f"Entry Date: {row['entry_date']}")
                    else:
                        st.caption(f"Exit Date: {row['exit_date']}")
                else:
                    breakout_lvl = round(safe_float(row['ath']) * 1.01, 2)
                    st.markdown(f"**Breakout Level:** ₹{breakout_lvl}")
                    st.caption("Waiting for price to cross ATH...")

# --- MAIN DASHBOARD LOGIC ---
if not df.empty:
    tab1, tab2 = st.tabs(["📊 Active Trades", "📜 Trade History"])

    with tab1:
        st.markdown("### Live & Ongoing Trades")
        active_df = df[df['status'].isin(["🟡 WAITING", "🟢 ENTERED"])]
        if active_df.empty:
            st.info("Abhi koi active trade ya waiting list me stock nahi hai.")
        else:
            draw_cards(active_df) # Table ki jagah Cards call kar rahe hain

    with tab2:
        st.markdown("### Closed Trades History")
        history_df = df[df['status'].isin(["🔴 SL HIT", "🎯 TARGET HIT"])]
        if history_df.empty:
            st.info("Abhi tak koi bhi trade close nahi hui hai.")
        else:
            draw_cards(history_df) # Yahan bhi Cards dikhenge
else:
    st.warning("⚠️ Google Sheet ekdum khali hai ya URL block ho raha hai.")

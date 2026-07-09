import streamlit as st
import pandas as pd

# Page layout aur config set kar rahe hain
st.set_page_config(page_title="ATH Track System", page_icon="📈", layout="wide")

# Dashboard ka Title aur Subtitle (Jaise aapke screen par tha)
st.title("ATH Track system")
st.write("**Automated Execution Tracking System**")

# SEBI Disclaimer Box
st.info("Disclaimer: EDUCATIONAL PURPOSES ONLY. I am NOT a SEBI Registered Analyst. This dashboard strictly tracks my personal algorithmic logic. Do not consider this as buy/sell advice.")

# Aapki Google Sheet ka CSV Data URL
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1qKxpIIoGd4skNllbua6U0AeeFt-WQjeYPMvBzS5_Qn4/export?format=csv"

@st.cache_data(ttl=30)  # Har 30 second me data auto-refresh hoga
def load_data():
    try:
        # Google Sheet se live CSV download karke pandas dataframe me load karega
        data = pd.read_csv(SHEET_CSV_URL)
        # Columns ke aas-paas ki extra spaces hatane ke liye
        data.columns = [str(c).strip() for c in data.columns]
        return data
    except Exception as e:
        st.error(f"Google Sheet se connect karne me dikkat aayi: {e}")
        return pd.DataFrame()

# Data loading indicator
df = load_data()

if not df.empty:
    # --- YAHAN 2 TABS BANAYENGE ---
    tab1, tab2 = st.tabs(["📊 Active Trades", "📜 Trade History"])

    # --- TAB 1: ACTIVE TRADES (WAITING AUR ENTERED WALE STOCKS) ---
    with tab1:
        st.markdown("### Live & Ongoing Trades")
        
        # Sirf WAITING aur ENTERED status wale stocks filter honge
        active_df = df[df['status'].isin(["🟡 WAITING", "🟢 ENTERED"])]
        
        if active_df.empty:
            st.info("Abhi koi active trade ya waiting list me stock nahi hai.")
        else:
            # Table ko bade screen par sundar dikhane ke liye
            st.dataframe(active_df, use_container_width=True, hide_index=True)

    # --- TAB 2: TRADE HISTORY (SL HIT AUR TARGET HIT WALE STOCKS) ---
    with tab2:
        st.markdown("### Closed Trades History")
        
        # Sirf SL HIT aur TARGET HIT status wale stocks filter honge
        history_df = df[df['status'].isin(["🔴 SL HIT", "🎯 TARGET HIT"])]
        
        if history_df.empty:
            st.info("Abhi tak koi bhi trade close nahi hui hai (History khali hai).")
        else:
            st.dataframe(history_df, use_container_width=True, hide_index=True)

else:
    st.warning("⚠️ Google Sheet ekdum khali hai ya URL block ho raha hai. Pehle main.py ko chalu kijiye taaki data sheet me bhar sake.")

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
        # 🚀 YAHAN HAI ASALI MAGIC: 
        # Sheet me header kuch bhi ho, yeh code usko automatically sahi format me convert kar dega
        df.columns = ["symbol", "company_name", "ath", "live_price", "day_change", "status", "entry_price", "sl_price", "target_price", "pnl_perc", "entry_date", "exit_date"]
        return df
    except Exception as e:
        st.error(f"Google Sheet se connect karne me dikkat aayi: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    tab1, tab2 = st.tabs(["📊 Active Trades", "📜 Trade History"])

    with tab1:
        st.markdown("### Live & Ongoing Trades")
        active_df = df[df['status'].isin(["🟡 WAITING", "🟢 ENTERED"])]
        if active_df.empty:
            st.info("Abhi koi active trade ya waiting list me stock nahi hai.")
        else:
            st.dataframe(active_df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### Closed Trades History")
        history_df = df[df['status'].isin(["🔴 SL HIT", "🎯 TARGET HIT"])]
        if history_df.empty:
            st.info("Abhi tak koi bhi trade close nahi hui hai (History khali hai).")
        else:
            st.dataframe(history_df, use_container_width=True, hide_index=True)
else:
    st.warning("⚠️ Google Sheet ekdum khali hai ya URL block ho raha hai. Pehle main.py ko chalu kijiye taaki data sheet me bhar sake.")

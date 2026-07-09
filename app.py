import streamlit as st
import pandas as pd

# --- PAGE CONFIG & CUSTOM CSS ---
st.set_page_config(page_title="ATH Track System", page_icon="📈", layout="wide")

# Custom CSS for Buttons, Badges, and Ticker
st.markdown("""
    <style>
    .custom-btn {
        background-color: #1E88E5;
        color: white !important;
        padding: 5px 12px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 13px;
        font-weight: 600;
        margin: 4px 2px;
        border-radius: 6px;
        border: 1px solid #1565C0;
        transition: 0.3s;
    }
    .custom-btn:hover {
        background-color: #1565C0;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    }
    .badge {
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 900;
        color: black !important;
        float: right;
        margin-top: 2px;
    }
    .badge-waiting { background-color: #FFC107; }
    .badge-entered { background-color: #00E676; }
    .badge-sl { background-color: #FF5252; color: white !important; }
    .badge-tgt { background-color: #40C4FF; }
    
    .ticker-container {
        width: 100%;
        background-color: #1E1E1E;
        color: white;
        padding: 8px;
        border-radius: 8px;
        border: 1px solid #444;
        margin-bottom: 25px;
        font-size: 14px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }
    .ticker-link {
        color: #40C4FF !important;
        text-decoration: none;
        font-weight: bold;
    }
    .ticker-link:hover { text-decoration: underline; }
    </style>
""", unsafe_allow_html=True)

st.title("ATH Track system")
st.markdown("**Automated Execution Tracking System** 🚀")
st.info("Disclaimer: EDUCATIONAL PURPOSES ONLY. I am NOT a SEBI Registered Analyst.")

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

# --- HORIZONTAL RUNNING NEWS TICKER ---
if not df.empty:
    unique_symbols = df['symbol'].dropna().unique()
    news_items = []
    for sym in unique_symbols:
        news_link = f"https://www.google.com/search?q={sym}+share+latest+news+today"
        news_items.append(f"📰 <b>{sym}</b>: <a class='ticker-link' href='{news_link}' target='_blank'>Latest News</a>")
    
    ticker_text = " &nbsp;&nbsp; | &nbsp;&nbsp; ".join(news_items)
    # Marquee tag se news scroll hogi
    st.markdown(f"<div class='ticker-container'><marquee behavior='scroll' direction='left' scrollamount='5'>{ticker_text}</marquee></div>", unsafe_allow_html=True)

# --- ADVANCED CARDS FUNCTION ---
def draw_cards(dataframe):
    cols = st.columns(4) 
    
    for i, (index, row) in enumerate(dataframe.iterrows()):
        with cols[i % 4]:
            with st.container(border=True):
                sym = str(row['symbol']).strip()
                status = str(row['status']).upper()
                live_price = safe_float(row['live_price'])
                ath = safe_float(row['ath'])
                
                below_ath = round(((ath - live_price) / ath) * 100, 2) if ath > 0 else 0
                
                # Assigning Badge Color
                if "WAITING" in status:
                    badge_class, display_status = "badge-waiting", "🟡 WAITING"
                elif "ENTERED" in status:
                    badge_class, display_status = "badge-entered", "🟢 ENTERED"
                elif "SL" in status:
                    badge_class, display_status = "badge-sl", "🔴 SL HIT"
                else:
                    badge_class, display_status = "badge-tgt", "🎯 TARGET HIT"
                
                # 1. Card Header & Badge
                st.markdown(f"#### {sym} <span class='badge {badge_class}'>{display_status}</span>", unsafe_allow_html=True)
                
                # 2. Beautiful Buttons (Chart & Data)
                chart = f"https://in.tradingview.com/chart/?symbol=NSE:{sym}"
                screener = f"https://www.screener.in/company/{sym}/"
                
                st.markdown(f"""
                    <a href="{chart}" target="_blank" class="custom-btn">📈 Chart</a>
                    <a href="{screener}" target="_blank" class="custom-btn">📊 Data</a>
                """, unsafe_allow_html=True)
                
                st.divider() # Line separator
                
                # 3. Clean & Explicit Metrics
                st.markdown(f"**LTP:** ₹{live_price}  *( {row['day_change']} )*")
                
                if "WAITING" in status:
                    st.markdown(f"**ATH Level:** ₹{ath}")
                    st.markdown(f"<b style='color:#FFB300;'>% Below ATH:</b> <b>{below_ath}%</b> down", unsafe_allow_html=True)
                    st.caption(f"🚀 Breakout Trigger: ₹{round(ath * 1.01, 2)}")
                else:
                    pnl = safe_float(row['pnl_perc'])
                    pnl_color = "#00E676" if pnl >= 0 else "#FF5252" # Green if profit, Red if loss
                    st.markdown(f"**Current P&L:** <b style='color:{pnl_color};'>{pnl}%</b>", unsafe_allow_html=True)
                    st.markdown(f"**Target:** ₹{safe_float(row['target_price'])}")
                    st.markdown(f"**SL:** ₹{safe_float(row['sl_price'])}")

# --- MAIN DASHBOARD LOGIC ---
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

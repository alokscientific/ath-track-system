import streamlit as st
import pandas as pd
import yfinance as yf

# --- PAGE CONFIG & CUSTOM CSS ---
st.set_page_config(page_title="ATH Track System", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    /* Super Ziddi Blue Outline for Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 3px solid #1E88E5 !important; /* Thick Blue Border */
        border-radius: 12px !important;
        box-shadow: 0px 5px 15px rgba(30, 136, 229, 0.3) !important; /* Blue glow shadow */
        padding: 8px !important;
        background-color: #121212 !important; /* Dark background to make blue pop */
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border: 3px solid #40C4FF !important; /* Hover pe light blue */
        box-shadow: 0px 8px 20px rgba(64, 196, 255, 0.5) !important;
    }

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
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #444;
        margin-bottom: 25px;
        font-size: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }
    .ticker-link {
        color: #FFD700 !important;
        text-decoration: none;
        font-weight: 500;
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

@st.cache_data(ttl=600)
def get_live_news(symbols_tuple):
    news_items = []
    for sym in symbols_tuple:
        try:
            ticker = yf.Ticker(f"{sym}.NS")
            news = ticker.news
            if news and len(news) > 0:
                headline = news[0]['title']
                link = news[0]['link']
                news_items.append(f"📰 <b>{sym}</b>: <a class='ticker-link' href='{link}' target='_blank'>{headline}</a>")
        except Exception:
            pass
    return news_items

df = load_data()

def safe_float(val):
    try:
        return float(val)
    except:
        return 0.0

# --- HORIZONTAL RUNNING LIVE NEWS TICKER ---
if not df.empty:
    unique_symbols = tuple(df['symbol'].dropna().unique())
    news_list = get_live_news(unique_symbols)
    
    if news_list:
        ticker_text = " &nbsp;&nbsp;&nbsp; 🔴 &nbsp;&nbsp;&nbsp; ".join(news_list)
        st.markdown(f"<div class='ticker-container'><marquee behavior='scroll' direction='left' scrollamount='5'>{ticker_text}</marquee></div>", unsafe_allow_html=True)

# --- ADVANCED CARDS FUNCTION ---
def draw_cards(dataframe):
    cols = st.columns(4) 
    
    for i, (index, row) in enumerate(dataframe.iterrows()):
        with cols[i % 4]:
            with st.container(border=True):
                sym = str(row['symbol']).strip()
                comp_name = str(row['company_name']).strip()
                status = str(row['status']).upper()
                live_price = safe_float(row['live_price'])
                ath = safe_float(row['ath'])
                day_change_str = str(row['day_change'])
                
                below_ath = round(((ath - live_price) / ath) * 100, 2) if ath > 0 else 0
                
                if "WAITING" in status:
                    badge_class, display_status = "badge-waiting", "🟡 WAITING"
                elif "ENTERED" in status:
                    badge_class, display_status = "badge-entered", "🟢 ENTERED"
                elif "SL" in status:
                    badge_class, display_status = "badge-sl", "🔴 SL HIT"
                else:
                    badge_class, display_status = "badge-tgt", "🎯 TARGET HIT"
                
                if "-" in day_change_str:
                    change_color = "#FF5252"
                elif "+" in day_change_str:
                    change_color = "#00E676"
                else:
                    change_color = "#FFFFFF"
                
                st.markdown(f"#### {sym} <span class='badge {badge_class}'>{display_status}</span>", unsafe_allow_html=True)
                st.markdown(f"<div style='color: #FFFFFF; font-size: 12px; margin-top: -12px; margin-bottom: 12px; opacity: 0.8;'>{comp_name}</div>", unsafe_allow_html=True)
                
                chart = f"https://in.tradingview.com/chart/?symbol=NSE:{sym}"
                screener = f"https://www.screener.in/company/{sym}/"
                
                st.markdown(f"""
                    <a href="{chart}" target="_blank" class="custom-btn">📈 Chart</a>
                    <a href="{screener}" target="_blank" class="custom-btn">📊 Data</a>
                """, unsafe_allow_html=True)
                
                st.divider()
                
                st.markdown(f"**LTP:** ₹{live_price} <span style='color:{change_color}; font-weight:bold;'>({day_change_str})</span>", unsafe_allow_html=True)
                
                if "WAITING" in status:
                    st.markdown(f"**ATH Level:** ₹{ath}")
                    st.markdown(f"<b style='color:#FFB300;'>% Below ATH:</b> <b>{below_ath}%</b> down", unsafe_allow_html=True)
                    st.caption(f"🚀 Breakout Trigger: ₹{round(ath * 1.01, 2)}")
                else:
                    pnl = safe_float(row['pnl_perc'])
                    pnl_color = "#00E676" if pnl >= 0 else "#FF5252"
                    st.markdown(f"**Current P&L:** <b style='color:{pnl_color};'>{pnl}%</b>", unsafe_allow_html=True)
                    st.markdown(f"**Target:** ₹{safe_float(row['target_price'])}")
                    st.markdown(f"**SL:** ₹{safe_float(row['sl_price'])}")

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

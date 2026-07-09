import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="ATH Track System", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    /* Asali Blue Border Smart Card */
    .pro-card {
        border: 2px solid #1E88E5 !important;
        border-radius: 12px;
        padding: 16px;
        background-color: #121212;
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease, border 0.3s ease;
        margin-bottom: 1rem;
    }
    .pro-card:hover {
        border: 2px solid #40C4FF !important;
        box-shadow: 0 6px 18px rgba(64, 196, 255, 0.4);
        transform: translateY(-3px);
    }
    .pro-card h4 {
        margin-top: 0px;
        margin-bottom: 5px;
        font-size: 1.2rem;
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
        margin: 4px 4px 0 0;
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
    .card-divider {
        border: 0;
        height: 1px;
        background: #333;
        margin: 15px 0;
    }
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

if not df.empty:
    unique_symbols = tuple(df['symbol'].dropna().unique())
    news_list = get_live_news(unique_symbols)
    
    if news_list:
        ticker_text = " &nbsp;&nbsp;&nbsp; 🔴 &nbsp;&nbsp;&nbsp; ".join(news_list)
        st.markdown(f"<div class='ticker-container'><marquee behavior='scroll' direction='left' scrollamount='5'>{ticker_text}</marquee></div>", unsafe_allow_html=True)

def draw_cards(dataframe):
    cols = st.columns(4) 
    
    for i, (index, row) in enumerate(dataframe.iterrows()):
        with cols[i % 4]:
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
            
            chart = f"https://in.tradingview.com/chart/?symbol=NSE:{sym}"
            screener = f"https://www.screener.in/company/{sym}/"

            # 🚀 Magic Fix: Yahan se leading spaces (indentation) hata di hai taaki Code Block na bane
            card_html = f"""<div class="pro-card">
<h4>{sym} <span class='badge {badge_class}'>{display_status}</span></h4>
<div style='color: #FFFFFF; font-size: 11px; margin-bottom: 12px; opacity: 0.7;'>{comp_name}</div>
<a href="{chart}" target="_blank" class="custom-btn">📈 Chart</a>
<a href="{screener}" target="_blank" class="custom-btn">📊 Data</a>
<hr class="card-divider">
<p style="margin:0 0 6px 0; font-size: 14px;"><b>LTP:</b> ₹{live_price} <span style='color:{change_color}; font-weight:bold;'>({day_change_str})</span></p>"""

            if "WAITING" in status:
                card_html += f"""<p style="margin:0 0 6px 0; font-size: 14px;"><b>ATH Level:</b> ₹{ath}</p>
<p style="margin:0 0 6px 0; font-size: 14px;"><b style='color:#FFB300;'>% Below ATH:</b> <b>{below_ath}%</b> down</p>
<div style="font-size: 12px; color: #aaa; margin-top: 12px;">🚀 Breakout Trigger: ₹{round(ath * 1.01, 2)}</div>"""
            else:
                pnl = safe_float(row['pnl_perc'])
                pnl_color = "#00E676" if pnl >= 0 else "#FF5252"
                card_html += f"""<p style="margin:0 0 6px 0; font-size: 14px;"><b>Current P&L:</b> <b style='color:{pnl_color};'>{pnl}%</b></p>
<p style="margin:0 0 6px 0; font-size: 14px;"><b>Target:</b> ₹{safe_float(row['target_price'])}</p>
<p style="margin:0; font-size: 14px;"><b>SL:</b> ₹{safe_float(row['sl_price'])}</p>"""

            card_html += "</div>"
            
            st.markdown(card_html, unsafe_allow_html=True)

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

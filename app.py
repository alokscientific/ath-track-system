import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import urllib.request
import xml.etree.ElementTree as ET

# 1. Page Configuration
st.set_page_config(page_title="ATH Track system", page_icon="📈", layout="wide")
st_autorefresh(interval=60000, limit=10000, key="data_refresh")

# 2. Modern Compact UI CSS
st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1 { color: #0F172A; font-weight: 800; letter-spacing: -1px; margin-bottom: 5px;}
.subtitle { color: #64748B; font-weight: 600; font-size: 1.0rem; letter-spacing: 1px; margin-bottom: 15px; }

/* Subtle Disclaimer Box */
.disclaimer { background-color: #F8FAFC; border: 1px solid #E2E8F0; color: #64748B; padding: 8px 12px; border-radius: 6px; font-size: 0.75rem; margin-bottom: 25px; text-align: left; }

/* Metrics Cards System */
.metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px; }
.metric-card { background: #ffffff; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: transform 0.2s; }
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.metric-title { font-size: 0.85rem; color: #64748B; font-weight: 600; margin-bottom: 5px; }
.metric-value { font-size: 1.8rem; font-weight: 800; color: #0F172A; }

/* News Ticker */
.news-ticker { background-color: #0F172A; color: #F8FAFC; padding: 10px 15px; border-radius: 6px; font-size: 0.85rem; font-weight: 500; margin-bottom: 25px; display: flex; align-items: center;}
.news-ticker a { color: #38BDF8; text-decoration: none; margin-right: 35px; }

/* Compact List View (Table) */
.table-container { overflow-x: auto; background: #ffffff; border: 1px solid #E2E8F0; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);}
.trade-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; text-align: left; }
.trade-table th { background-color: #F8FAFC; color: #475569; font-weight: 600; padding: 12px 15px; border-bottom: 2px solid #E2E8F0; white-space: nowrap;}
.trade-table td { padding: 12px 15px; border-bottom: 1px solid #E2E8F0; vertical-align: middle; }
.trade-table tr:hover { background-color: #F1F5F9; }
.sym-text { font-weight: 700; color: #0F172A; font-size: 0.95rem; }
.comp-text { color: #64748B; font-size: 0.75rem; display: block; margin-top: 2px;}
.price-bold { font-weight: 700; color: #0F172A; font-size: 0.95rem;}
.sub-data { font-size: 0.75rem; color: #64748B; display: block; margin-top: 3px;}
.green { color: #16A34A; font-weight: 600; }
.red { color: #DC2626; font-weight: 600; }
.badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; display: inline-block; white-space: nowrap;}
.badge-WAITING { background-color: #FEF9C3; color: #A16207; }
.badge-ENTERED { background-color: #DCFCE7; color: #15803D; }
.badge-TARGET { background-color: #E0F2FE; color: #0369A1; }
.badge-SL { background-color: #FEE2E2; color: #B91C1C; }
.action-link { font-weight: 600; text-decoration: none; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 5px; background: #F1F5F9; color: #0F172A;}
.action-link:hover { background: #E2E8F0; }
.away-badge { font-size: 0.7rem; background: #F1F5F9; padding: 2px 6px; border-radius: 4px; color: #475569; margin-top: 4px; display: inline-block;}
</style>
""")


# 3. News Dictionary Fetcher
@st.cache_data(ttl=600)
def get_news_dict(symbols):
    news_dict = {}
    for sym in symbols:
        try:
            url = f"https://news.google.com/rss/search?q={sym}+stock+india&hl=en-IN&gl=IN&ceid=IN:en"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                root = ET.fromstring(response.read())
                item = root.find('./channel/item')
                if item is not None:
                    title = item.find('title').text
                    if len(title) > 60: title = title[:57] + "..."
                    news_dict[sym] = f"<a href='{item.find('link').text}' target='_blank'>{title}</a>"
        except:
            pass
    return news_dict


# 4. Load Data
SHEET_ID = "1qKxpIIoGd4skNllbua6U0AeeFt-WQjeYPMvBzS5_Qn4"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"


@st.cache_data(ttl=30)
def load_data():
    try:
        return pd.read_csv(CSV_URL)
    except:
        return pd.DataFrame()


# 5. Header & SEBI Disclaimer (Subtle Version)
st.markdown("<h1>ATH Track system</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Automated Execution Tracking System</div>", unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer">
    Disclaimer: EDUCATIONAL PURPOSES ONLY. I am NOT a SEBI Registered Analyst. This dashboard strictly tracks my personal algorithmic logic. Do not consider this as buy/sell advice.
</div>
""", unsafe_allow_html=True)

df = load_data()

if not df.empty:
    active_symbols = df.sort_values(by="Status").head(5)['Symbol'].tolist()
    news_data = get_news_dict(active_symbols)

    news_items = [f"🔥 <b>{sym}</b>: {news_data[sym]}" for sym in news_data if sym in news_data]
    if news_items:
        marquee_html = " &nbsp; • &nbsp; ".join(news_items)
        st.markdown(
            f'<div class="news-ticker"><marquee behavior="scroll" direction="left" scrollamount="5">{marquee_html}</marquee></div>',
            unsafe_allow_html=True)

    # Calculate Metrics
    total_tracking = len(df)
    active_trades = len(df[df['Status'].astype(str).str.contains('ENTERED', na=False)])
    sl_hits = len(df[df['Status'].astype(str).str.contains('SL HIT', na=False)])
    target_hits = len(df[df['Status'].astype(str).str.contains('TARGET', na=False)])

    # Generate Metrics HTML (Cards Look)
    metrics_html = f"""
    <div class="metrics-grid">
        <div class="metric-card"><div class="metric-title">🔍 Tracking (Total)</div><div class="metric-value">{total_tracking}</div></div>
        <div class="metric-card"><div class="metric-title">🟢 Active Trades</div><div class="metric-value">{active_trades}</div></div>
        <div class="metric-card"><div class="metric-title">🔴 SL Triggered</div><div class="metric-value">{sl_hits}</div></div>
        <div class="metric-card"><div class="metric-title">🎯 Target Achieved</div><div class="metric-value">{target_hits}</div></div>
    </div>
    """
    st.html(metrics_html)

    # Setup Table HTML
    table_html = """
    <div class="table-container">
        <table class="trade-table">
            <thead>
                <tr>
                    <th>Stock Name</th>
                    <th>Live Price</th>
                    <th>Algo Status</th>
                    <th>Trigger Info</th>
                    <th>Exit / Risk Info</th>
                    <th>Current P&L</th>
                    <th>Links</th>
                </tr>
            </thead>
            <tbody>
    """

    status_order = {'🟢 ENTERED': 1, '🎯 TARGET HIT': 2, '🔴 SL HIT': 3, '🟡 WAITING': 4}
    df['sort_order'] = df['Status'].map(status_order).fillna(5)
    df = df.sort_values('sort_order')

    for _, row in df.iterrows():
        sym = str(row.get('Symbol', ''))
        comp = str(row.get('Company Name', ''))[:30]
        live_val = float(str(row.get('Live Price', 0)).replace('nan', '0'))
        ath_val = float(str(row.get('ATH Price', 0)).replace('nan', '0'))

        live = f"₹{live_val:.2f}"
        change = str(row.get('Day Change', '0%'))
        status = str(row.get('Status', ''))
        ath = f"₹{ath_val:.2f}"

        # Calculate % Away from ATH
        away_perc = 0
        if ath_val > 0:
            away_perc = ((ath_val - live_val) / ath_val) * 100

        if away_perc > 0:
            away_text = f"<span class='away-badge'>📉 {away_perc:.1f}% below ATH</span>"
        elif away_perc < 0:
            away_text = f"<span class='away-badge' style='color:#16A34A;'>🚀 {abs(away_perc):.1f}% above ATH</span>"
        else:
            away_text = "<span class='away-badge'>⚡ At ATH</span>"

        change_color = "green" if "+" in change else "red" if "-" in change else ""

        badge_class = "badge-WAITING"
        if "ENTERED" in status:
            badge_class = "badge-ENTERED"
        elif "TARGET" in status:
            badge_class = "badge-TARGET"
        elif "SL" in status:
            badge_class = "badge-SL"
        status_text = status.replace('🟢', '').replace('🟡', '').replace('🔴', '').replace('🎯', '').strip()

        # Set Trigger Date and Info
        entry_info = f"<span class='sub-data'>Breakout Lvl: {ath}</span>"
        exit_info = "-"
        pnl_info = "-"

        if "ENTERED" in status or "HIT" in status:
            e_price = f"₹{row.get('Entry Price', 0):.2f}"
            e_date = str(row.get('Entry Date', '-'))
            entry_info = f"<span class='price-bold'>{e_price}</span><span class='sub-data'>Trigger Date: {e_date}</span>"

            sl = f"₹{row.get('SL Price', 0):.2f}"
            tgt = f"₹{row.get('Target Price', 0):.2f}"

            if "ENTERED" in status:
                exit_info = f"<span class='sub-data'>SL: {sl}</span><span class='sub-data'>Tgt: {tgt}</span>"
            else:
                x_date = str(row.get('Exit Date', '-'))
                exit_info = f"<span class='price-bold'>Closed</span><span class='sub-data'>Date: {x_date}</span>"

            try:
                pnl_val = float(str(row.get('P&L %', '0')).replace('nan', '0'))
                pnl_color = "green" if pnl_val > 0 else "red"
                pnl_info = f"<span class='price-bold {pnl_color}'>{pnl_val:.2f}%</span>"
            except:
                pnl_info = "-"

        chart_url = f"https://in.tradingview.com/chart/?symbol=NSE:{sym}"
        screener_url = f"https://www.screener.in/company/{sym}/consolidated/"

        row_html = f"""
        <tr>
            <td>
                <span class="sym-text">{sym}</span>
                <span class="comp-text">{comp}</span>
            </td>
            <td>
                <span class="price-bold">{live}</span>
                <span class="sub-data {change_color}">{change}</span>
                {away_text}
            </td>
            <td><span class="badge {badge_class}">{status_text}</span></td>
            <td>{entry_info}</td>
            <td>{exit_info}</td>
            <td>{pnl_info}</td>
            <td>
                <a href="{chart_url}" target="_blank" class="action-link">Chart</a>
                <a href="{screener_url}" target="_blank" class="action-link">Data</a>
            </td>
        </tr>
        """
        table_html += row_html

    table_html += "</tbody></table></div>"
    st.html(table_html)

else:
    st.info("🔄 Connecting to Market Data... Please wait.")
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
import sys
import os
from streamlit_autorefresh import st_autorefresh

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Stock App", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
    }
    .metric-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #1c1f26;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- AUTO REFRESH ----------------
st_autorefresh(interval=120000)

# ---------------- PATH ----------------
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from indicators import add_indicators
from model import train_model

# ---------------- UI HEADER ----------------
st.title("📈 AI Stock Market Prediction Dashboard")

# ---------------- STOCK LIST ----------------
USA_list = ["AAPL","MSFT","GOOGL","AMZN","TSLA","NVDA","META"]
india_list = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS"]

# ---------------- LAYOUT ----------------
col1, col2 = st.columns([1,2])

with col1:
    st.subheader("📊 Input Panel")
    
    market = st.selectbox("Select Market", ["USA", "India"])
    
    if market == "USA":
        symbol = st.selectbox("Stock", USA_list)
    else:
        symbol = st.selectbox("Stock", india_list)
    
    symbol_input = st.text_input("Custom Symbol")

    if symbol_input:
        symbol = symbol_input.upper()

# ---------------- DATA ----------------
@st.cache_data
def load_data(symbol):
    stock = yf.Ticker(symbol)
    df = stock.history(period="6mo")
    live_df = stock.history(period="1d", interval="5m")
    return df, live_df

df, live_df = load_data(symbol)

if df.empty or live_df.empty:
    st.error("Invalid Symbol")
    st.stop()

# ---------------- INDICATORS ----------------
df = add_indicators(df)
df["SMA50"] = df["Close"].rolling(50).mean()
df.dropna(inplace=True)

# ---------------- MODEL ----------------
@st.cache_resource
def load_model(data):
    return train_model(data)

model = load_model(df)

# ---------------- PREDICTION ----------------
latest = df[["SMA", "RSI"]].tail(1)
prediction = model.predict(latest)[0]

live_price = round(live_df["Close"].iloc[-1], 2)

# ---------------- RIGHT PANEL ----------------
with col2:
    st.subheader("📈 Results")

    c1, c2, c3 = st.columns(3)

    c1.metric("Live Price", f"${live_price}")
    c2.metric("Predicted", f"${round(prediction,2)}")

    # SIGNAL
    sma = df["SMA"].iloc[-1]
    rsi = df["RSI"].iloc[-1]

    if live_price > sma and rsi < 70:
        signal = "BUY"
        c3.success("BUY 📈")
    elif live_price < sma and rsi > 30:
        signal = "SELL"
        c3.error("SELL 📉")
    else:
        signal = "HOLD"
        c3.info("HOLD ⚖")

    # ---------------- CHART ----------------
    st.subheader("📊 Price Chart")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        name="Close"
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["SMA50"],
        name="SMA50"
    ))

    st.plotly_chart(fig, use_container_width=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Risk Management")

sl = st.sidebar.slider("Stop Loss (%)", 1, 20, 3)
target = st.sidebar.slider("Target (%)", 1, 30, 5)

if signal == "BUY":
    stop_loss = live_price * (1 - sl/100)
    target_price = live_price * (1 + target/100)
elif signal == "SELL":
    stop_loss = live_price * (1 + sl/100)
    target_price = live_price * (1 - target/100)
else:
    stop_loss = None
    target_price = None

if stop_loss:
    st.sidebar.write(f"Stop Loss: {round(stop_loss,2)}")
    st.sidebar.write(f"Target: {round(target_price,2)}")
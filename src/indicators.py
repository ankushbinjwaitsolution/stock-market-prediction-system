import pandas as pd
import ta

def add_indicators(df):
    df["SMA"] = ta.trend.sma_indicator(df["Close"], window=3)
    df["RSI"] = ta.momentum.rsi(df["Close"], window=3)

    df.dropna(inplace=True)
    return df

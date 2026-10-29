import yfinance as yf
import pandas as pd
import requests
import time
import os
from flask import Flask
import threading

# Render varun ghetle jatil
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Tujhe Stocks List - tu badlu shaktos
SYMBOLS = ["BTC-USD","ETH-USD","SOL-USD","RELIANCE.NS","TCS.NS","IDEA.NS","EURUSD=X","XAUUSD=X"]

def send_msg(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except: pass

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot Running - RSI Div 1-9 Gap"

def check_div(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="15m", progress=False, auto_adjust=True)
        if len(df) < 60: return
        
        # RSI Calculate
        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        df = df.dropna()

        # Pivot Logic - 5 left 5 right
        lows = []
        for i in range(5, len(df)-5):
            if df['Low'].iloc[i] == min(df['Low'].iloc[i-5:i+6]):
                lows.append(i)
        
        # Gap 1 to 9 check
        for k in range(len(lows)-1, 0, -1):
            curr = lows[k]
            prev = lows[k-1]
            gap = curr - prev - 1
            
            if 1 <= gap <= 9:
                price_ll = df['Low'].iloc[curr] < df['Low'].iloc[prev]
                rsi_hl = df['RSI'].iloc[curr] > df['RSI'].iloc[prev]
                rsi_ok = 20 <= df['RSI'].iloc[curr] <= 80 and 20 <= df['RSI'].iloc[prev] <= 80
                
                if price_ll and rsi_hl and rsi_ok:
                    msg = f"🟢 *BULLISH DIV*\n\nSymbol: {symbol}\nGap: {gap} candle\nPrice: {float(df['Close'].iloc[-1]):.2f}\nRSI: {float(df['RSI'].iloc[curr]):.1f}"
                    send_msg(msg)
                    return

    except Exception as e:
        print(e)

def loop():
    send_msg("✅ बॉट चालू झाला - आता १५ मिनिटांनी चेक होईल")
    while True:
        for s in SYMBOLS:
            check_div(s)
        time.sleep(900) # 15 min

threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

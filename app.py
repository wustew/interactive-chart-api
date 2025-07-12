from flask import Flask, request, Response
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

app = Flask(__name__)

@app.route("/")
def home():
    return "Backend is up! Go to /chart?ticker=SPY&ma=200&interval=1d"

@app.route("/chart")
def generate_chart():
    # --- Get query parameters ---
    ticker = request.args.get("ticker", default="SPY").upper()
    ma_period = int(request.args.get("ma", default=200))
    interval = request.args.get("interval", default="1d")

    start_date = "1990-01-01"

    # --- Fetch data ---
    try:
        data = yf.download(ticker, start=start_date, interval=interval)
        data = data[['Close']].dropna()
        if data.empty:
            return f"No data for {ticker}."
    except Exception as e:
        return f"Error downloading data: {e}"

    # --- Calculate momentum ---
    data['MA'] = data['Close'].rolling(window=ma_period).mean()
    data['Momentum'] = (data['Close'] - data['MA']) / data['MA']
    data = data.dropna()

    # --- Create plot ---
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        subplot_titles=("Price", "Normalized Momentum"),
        vertical_spacing=0.1
    )

    fig.add_trace(
        go.Scatter(x=data.index, y=data['Close'], name="Price", line=dict(color='black')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=data.index, y=data['MA'], name=f"{ma_period}-MA", line=dict(color='blue', dash='dash')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=data.index, y=data['Momentum'], name="Momentum", line=dict(color='darkred')),
        row=2, col=1
    )
    fig.add_hline(y=0, line=dict(color='gray', dash='dash'), row=2, col=1)
    fig.add_hline(y=-0.05, line=dict(color='red', dash='dash'), row=2, col=1)
    fig.add_hline(y=-0.15, line=dict(color='darkred', dash='dash'), row=2, col=1)

    fig.update_layout(
        title=f"{ticker} Price & Structural Momentum",
        height=800,
        template="plotly_white",
        hovermode='x unified'
    )
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Momentum", row=2, col=1)

    # --- Return HTML version of chart ---
    html = pio.to_html(fig, full_html=True)
    return Response(html, mimetype='text/html')
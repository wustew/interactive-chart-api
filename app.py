from flask import Flask, request, Response
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

app = Flask(__name__)

@app.route("/")
def home():
    return "Backend is working! Visit /chart?ticker=SPY&ma=200&interval=1d"

@app.route("/chart")
def chart():
    try:
        # --- Get query parameters ---
        ticker = request.args.get("ticker", default="SPY").upper()
        ma_period = int(request.args.get("ma", default=200))
        interval = request.args.get("interval", default="1d")
        #start_date = "1900-01-01"

        # --- Fetch data ---
        try:
            #data = yf.download(ticker, start=start_date, interval=interval, auto_adjust=False)
            data = yf.download(ticker, period='max', auto_adjust=False)
            # Drop multi-level column index
            data.columns = data.columns.get_level_values(0)
            data = data.dropna()
            if data.empty:
                return f"No data found for {ticker}."
        except Exception as e:
            return f"Error downloading data for {ticker}: {e}"

        # --- Calculate momentum structure ---
        data['MA'] = data['Close'].rolling(window=ma_period).mean()
        data['Momentum'] = (data['Close'] - data['MA']) / data['MA']
        data = data.dropna()

        # --- Create Plotly chart ---
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            row_heights=[0.7, 0.3],
            subplot_titles=("Price", "Normalized Momentum"),
            vertical_spacing=0.1
        )

        # Price chart
        fig.add_trace(
            go.Scatter(x=data.index, y=data['Close'], name="S&P 500 Price", line=dict(color='black', width=2)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=data.index, y=data['MA'], name=f"{ma_period}-Period MA", line=dict(color='blue', width=2, dash='dash')),
            row=1, col=1
        )

        # Momentum chart
        fig.add_trace(
            go.Scatter(x=data.index, y=data['Momentum'], name="Normalized Momentum", line=dict(color='darkred', width=2)),
            row=2, col=1
        )

        fig.update_layout(
            title=f"{ticker} Price and Structural Momentum (Michael Oliver Style)",
            height=800,
            showlegend=True,
            template="plotly_white",
            hovermode='x unified'
        )
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Normalized Momentum", row=2, col=1)

        print(f"Processing ticker={ticker}, ma={ma_period}, interval={interval}")

        # Return the figure as a full HTML page
        html = pio.to_html(fig, full_html=True)
        return Response(html, mimetype='text/html')
    except Exception as e:
        print(f"Error in /chart: {e}")
        return f"Error: {e}"

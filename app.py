'''
Structural Momentum (ChatGPT interpretation of Michael Oliver's approach)
Updated on 2025-07-22
'''

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

        # --- Fetch data ---
        data = yf.download(ticker, period='max', interval=interval, auto_adjust=False)
        tickername = yf.Ticker(ticker).info['shortName']
        data.columns = data.columns.get_level_values(0)
        data = data.dropna()
        if data.empty:
            return f"No data found for {ticker}."

        # --- Calculate Momentum ---
        data['MA'] = data['Close'].rolling(window=ma_period).mean()
        data['Momentum'] = (data['Close'] - data['MA']) / data['MA']

        # --- Calculate RSI (14-period) ---
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))

        data = data.dropna()

        # --- Create Plotly chart with 3 rows ---
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            row_heights=[0.6, 0.2, 0.2],
            vertical_spacing=0.05,
            subplot_titles=("", "Normalized Momentum", "RSI (14-period)")
        )
        
        # Update subplot title formatting
        fig.update_annotations(
            font_size=24,  # Increase font size
            font_weight="bold"  # Make bold (or use font_weight="bold" in newer versions)
        )
        
        # --- Row 1: Price & MA ---
        fig.add_trace(
            go.Scatter(x=data.index, y=data['Close'], name=f"{ticker} Close", line=dict(color='black', width=2)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=data.index, y=data['MA'], name=f"{ma_period}-Period MA", line=dict(color='blue', width=2, dash='dash')),
            row=1, col=1
        )

        # --- Row 2: Momentum ---
        fig.add_trace(
            go.Scatter(x=data.index, y=data['Momentum'], name="Normalized Momentum", line=dict(color='darkred', width=2)),
            row=2, col=1
        )

        # --- Row 3: RSI ---
        fig.add_trace(
            go.Scatter(x=data.index, y=data['RSI'], name="14-period RSI", line=dict(color='green', width=2)),
            row=3, col=1
        )

        # --- Layout settings ---
        fig.update_layout(
            title={
                'text': f"<b>{ticker} ({tickername})</b>",
                'font': {
                    'size': 36,
                    'color': 'black'
                },
                'x': 0.5,
                'xanchor': 'center',
                'y': 0.95,
                'yanchor': 'top'
            },
            autosize=True,
            height=None,
            showlegend=True,
            template="plotly_white",
            hovermode='x unified'
        )

        fig.update_xaxes(title_text="Date", row=3, col=1)
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Momentum", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])

        print(f"Processing ticker={ticker}, ma={ma_period}, interval={interval}")

        # --- Inject custom CSS to enlarge modebar buttons ---
        custom_css = """
        <style>
            html, body {
                margin: 0;
                padding: 0;
                height: 100%;
            }
            .modebar {
                transform: scale(1.8);
                transform-origin: top right;
            }
            .modebar-btn {
                padding: 12px !important;
                margin: 4px !important;
            }
            .plot-container {
                height: 100vh !important;
            }
        </style>
        """

        # Inject CSS into HTML head
        html = pio.to_html(fig, include_plotlyjs='cdn', full_html=True, default_height='100%', default_width='100%')
        html = html.replace('</head>', custom_css + '</head>')

        return Response(html, mimetype='text/html')
    except Exception as e:
        print(f"Error in /chart: {e}")
        return f"Error: {e}"

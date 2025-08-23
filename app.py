'''
Structural Momentum (ChatGPT interpretation of Michael Oliver's approach)
Updated on 2025-08-22
'''

from flask import Flask, request, Response, render_template_string
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

app = Flask(__name__)

# HTML template for the form
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Chart Analyzer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            width: 100%;
            text-align: center;
            transition: transform 0.3s ease;
        }

        .container:hover {
            transform: translateY(-5px);
        }

        h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .subtitle {
            color: #666;
            font-size: 1.1em;
            margin-bottom: 30px;
            font-weight: 300;
        }

        .form-group {
            margin-bottom: 25px;
            text-align: left;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #444;
            font-size: 1.1em;
        }

        input[type="text"], input[type="number"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1.1em;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.8);
        }

        input[type="text"]:focus, input[type="number"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);
            transform: translateY(-2px);
        }

        .interval-group {
            display: flex;
            gap: 15px;
            justify-content: space-between;
        }

        .interval-option {
            flex: 1;
            position: relative;
        }

        .interval-option input[type="radio"] {
            position: absolute;
            opacity: 0;
        }

        .interval-option label {
            display: block;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            font-weight: 600;
            background: rgba(255, 255, 255, 0.8);
        }

        .interval-option input[type="radio"]:checked + label {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .interval-option label:hover {
            border-color: #667eea;
            transform: translateY(-1px);
        }

        .submit-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.2em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 10px;
        }

        .submit-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
            background: linear-gradient(135deg, #5a67d8, #6b46a3);
        }

        .submit-btn:active {
            transform: translateY(-1px);
        }

        .loading {
            display: none;
            margin-top: 20px;
            color: #667eea;
            font-weight: 600;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .chart-container {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: white;
            z-index: 1000;
        }

        .chart-header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .back-btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .back-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }

        .chart-frame {
            width: 100%;
            height: calc(100% - 60px);
            border: none;
        }

        @media (max-width: 600px) {
            .container {
                padding: 30px 20px;
            }

            h1 {
                font-size: 2em;
            }

            .interval-group {
                flex-direction: column;
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 Stock Analyzer</h1>
        <p class="subtitle">Structural Momentum & Technical Analysis</p>
        
        <form id="chartForm">
            <div class="form-group">
                <label for="ticker">Stock Ticker Symbol</label>
                <input type="text" id="ticker" name="ticker" placeholder="e.g., SPY, AAPL, TSLA" required>
            </div>

            <div class="form-group">
                <label for="ma">Moving Average Period</label>
                <input type="number" id="ma" name="ma" value="36" min="1" max="500" required>
            </div>

            <div class="form-group">
                <label>Time Interval</label>
                <div class="interval-group">
                    <div class="interval-option">
                        <input type="radio" id="interval_1d" name="interval" value="1d">
                        <label for="interval_1d">Daily</label>
                    </div>
                    <div class="interval-option">
                        <input type="radio" id="interval_1wk" name="interval" value="1wk" checked>
                        <label for="interval_1wk">Weekly</label>
                    </div>
                    <div class="interval-option">
                        <input type="radio" id="interval_1mo" name="interval" value="1mo">
                        <label for="interval_1mo">Monthly</label>
                    </div>
                </div>
            </div>

            <button type="submit" class="submit-btn">Generate Chart</button>
        </form>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Generating your chart...</p>
        </div>
    </div>

    <div class="chart-container" id="chartContainer">
        <div class="chart-header">
            <h2 id="chartTitle">Stock Chart</h2>
            <button class="back-btn" onclick="hideChart()">← Back to Form</button>
        </div>
        <iframe id="chartFrame" class="chart-frame"></iframe>
    </div>

    <script>
        let isChartVisible = false;
        
        document.getElementById('chartForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form values
            const ticker = document.getElementById('ticker').value.trim().toUpperCase();
            const ma = document.getElementById('ma').value;
            const interval = document.querySelector('input[name="interval"]:checked').value;
            
            // Validate inputs
            if (!ticker) {
                alert('Please enter a ticker symbol');
                return;
            }
            
            if (!ma || ma < 1) {
                alert('Please enter a valid moving average period');
                return;
            }

            // Update ticker input to show uppercase
            document.getElementById('ticker').value = ticker;
            
            // Show loading
            document.querySelector('.container').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
            
            // Build URL for your Flask backend
            const baseUrl = window.location.origin;
            const chartUrl = `${baseUrl}/chart?ticker=${encodeURIComponent(ticker)}&ma=${encodeURIComponent(ma)}&interval=${encodeURIComponent(interval)}`;
            
            // Update chart title
            document.getElementById('chartTitle').textContent = `${ticker} - ${ma}MA - ${interval.toUpperCase()}`;
            
            // Load chart in iframe
            const iframe = document.getElementById('chartFrame');
            
            // Safari-compatible iframe loading
            iframe.onload = function() {
                if (!isChartVisible && iframe.src && iframe.src.includes('/chart')) {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('chartContainer').style.display = 'block';
                    isChartVisible = true;
                }
            };
            
            // Handle iframe load errors
            iframe.onerror = function() {
                if (!isChartVisible) {
                    document.getElementById('loading').style.display = 'none';
                    document.querySelector('.container').style.display = 'block';
                    alert('Error loading chart. Please check the ticker symbol and try again.');
                }
            };
            
            // Set the src after setting up event handlers
            iframe.src = chartUrl;
        });
        
        function hideChart() {
            // Set flag to prevent chart from showing again
            isChartVisible = false;
            
            // Clear event handlers
            const iframe = document.getElementById('chartFrame');
            iframe.onload = null;
            iframe.onerror = null;
            
            // Hide chart and show form immediately
            document.getElementById('chartContainer').style.display = 'none';
            document.querySelector('.container').style.display = 'block';
            
            // Clear iframe after state change to prevent Safari issues
            setTimeout(() => {
                if (!isChartVisible) {
                    iframe.src = '';
                }
            }, 50);
        }
        
        // Auto-convert ticker to uppercase as user types
        document.getElementById('ticker').addEventListener('input', function(e) {
            e.target.value = e.target.value.toUpperCase();
        });
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

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

        # Detect if it's a mobile request and set font sizes
        user_agent = request.headers.get('User-Agent', '').lower()
        is_mobile = any(x in user_agent for x in ['mobile', 'iphone', 'ipad', 'android'])
        
        # Adjust font sizes for mobile
        title_size = 24 if is_mobile else 36
        subtitle_size = 16 if is_mobile else 24
        legend_size = 12 if is_mobile else 16

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
            font=dict(
                size=subtitle_size,
                color='black',
                weight='bold'
            )
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
                    'size': title_size,
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
            hovermode='x unified',
            legend=dict(
                x=1.02 if not is_mobile else 0.5,
                y=0.75 if not is_mobile else -0.15,
                xanchor='left' if not is_mobile else 'center',
                yanchor='middle' if not is_mobile else 'top',
                font=dict(size=legend_size),
                bgcolor='rgba(255,255,255,0)',
                bordercolor='black',
                borderwidth=0,
                orientation='v' if not is_mobile else 'h'
            )
        )

        fig.update_xaxes(title_text="Date", row=3, col=1, title_font_size=12 if is_mobile else 14)
        fig.update_yaxes(title_text="Price", row=1, col=1, title_font_size=12 if is_mobile else 14)
        fig.update_yaxes(title_text="Momentum", row=2, col=1, title_font_size=12 if is_mobile else 14)
        fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100], title_font_size=12 if is_mobile else 14)

        print(f"Processing ticker={ticker}, ma={ma_period}, interval={interval}")

        # --- Inject custom CSS to enlarge modebar buttons and optimize for mobile ---
        mobile_css = """
        <style>
            html, body {
                margin: 0;
                padding: 0;
                height: 100%;
                overflow-x: hidden;
            }
            .modebar {
                transform: scale(1.4);
                transform-origin: top right;
            }
            .modebar-btn {
                padding: 8px !important;
                margin: 2px !important;
            }
            .plot-container {
                height: 100vh !important;
            }
            @media (max-width: 768px) {
                .modebar {
                    transform: scale(1.2);
                }
                .js-plotly-plot .plotly .modebar {
                    left: 10px !important;
                    right: auto !important;
                }
                .main-svg {
                    overflow: visible !important;
                }
            }
        </style>
        """ if is_mobile else """
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
        html = html.replace('</head>', mobile_css + '</head>')

        return Response(html, mimetype='text/html')
    except Exception as e:
        print(f"Error in /chart: {e}")
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(debug=True)

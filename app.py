from flask import Flask, jsonify
import plotly.graph_objects as go
import plotly.io as pio

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Render!"

@app.route("/chart")
def chart():
    fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[3, 1, 6]))
    return jsonify(chart=pio.to_json(fig))
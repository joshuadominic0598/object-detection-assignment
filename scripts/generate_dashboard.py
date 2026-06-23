import os
import webbrowser

import pandas as pd
import mysql.connector

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = "tmp/dashboard"

os.makedirs(OUTPUT_DIR,exist_ok=True)

# MYSQL
conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    port=os.getenv("MYSQL_PORT"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB")
)

requests_df = pd.read_sql("SELECT * FROM api_request_log ORDER BY id", conn)

predictions_df = pd.read_sql("SELECT * FROM prediction_log ORDER BY id", conn)

counts_df = pd.read_sql("SELECT * FROM object_counts ORDER BY count DESC", conn)

conn.close()

# KPIs
total_requests = len(requests_df)

successful_requests = int(requests_df["success"].sum()) if len(requests_df) else 0

failed_requests = (total_requests - successful_requests)

avg_response_time = round(requests_df["response_time_ms"].mean(),2) if len(requests_df) else 0

detection_failure_pct = round((requests_df["detected_classes"].fillna("").eq("").mean()) * 100,2) if len(requests_df) else 0

# CHARTS
success_fig = px.pie(
    names=["Success", "Failed"],
    values=[successful_requests,failed_requests],
    hole=0.35,
    title="Request Success Rate")

endpoint_fig = px.pie(requests_df,
    names="endpoint",
    title="Requests by Endpoint") if len(requests_df) else go.Figure()

response_fig = px.histogram(requests_df,
    x="response_time_ms",
    nbins=20,
    title="Response Time Distribution (ms)") if len(requests_df) else go.Figure()

confidence_fig = px.histogram(predictions_df,
    x="confidence",
    nbins=20,
    title="Prediction Confidence Distribution") if len(predictions_df) else go.Figure()

failure_fig = px.pie(
    names=["No Detection","Detected"],
    values=[detection_failure_pct,max(0,100 - detection_failure_pct)],
    hole=0.55,
    title="Detection Failure Rate")

# OBJECT DISTRIBUTION
if len(predictions_df):
    object_distribution = (predictions_df["object_class"].value_counts().reset_index())
    object_distribution.columns = ["object_class","count"]
    object_distribution = (object_distribution.sort_values("count",ascending=False).head(20))
else:
    object_distribution = pd.DataFrame(columns=["object_class","count"])

# TABLES
latest_requests = (requests_df.sort_values("request_timestamp",ascending=False).head(20))

latest_predictions = (predictions_df.sort_values("request_timestamp",ascending=False).head(20))

# HTML
html = f"""
<html>

<head>

<title>
Object Counter Dashboard
</title>

<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 30px;
    background: #f5f6fa;
}}

h1 {{
    margin-bottom: 30px;
}}

.grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}}

.card {{
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}}

.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 15px;
    margin-bottom: 25px;
}}

.kpi {{
    background: white;
    padding: 20px;
    text-align: center;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}}

.kpi-value {{
    font-size: 30px;
    font-weight: bold;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th, td {{
    border: 1px solid #ddd;
    padding: 8px;
}}

th {{
    background: #efefef;
}}

.section {{
    margin-top: 25px;
}}

</style>

</head>

<body>

<h1>
Object Counter Monitoring Dashboard
</h1>

<div class="kpi-grid">

<div class="kpi">
<div>Total Requests</div>
<div class="kpi-value">{total_requests}</div>
</div>

<div class="kpi">
<div>Successful</div>
<div class="kpi-value">{successful_requests}</div>
</div>

<div class="kpi">
<div>Failed</div>
<div class="kpi-value">{failed_requests}</div>
</div>

<div class="kpi">
<div>No Detection %</div>
<div class="kpi-value">{detection_failure_pct}%</div>
</div>

<div class="kpi">
<div>Avg Response</div>
<div class="kpi-value">{avg_response_time}ms</div>
</div>

</div>

<div class="grid">

<div class="card">
{success_fig.to_html(full_html=False, include_plotlyjs=False)}
</div>

<div class="card">
{endpoint_fig.to_html(full_html=False, include_plotlyjs=False)}
</div>

</div>

<div class="card section">
{response_fig.to_html(full_html=False, include_plotlyjs=False)}
</div>

<div class="card section">
{confidence_fig.to_html(full_html=False, include_plotlyjs=False)}
</div>

<div class="grid section">

<div class="card">
{failure_fig.to_html(full_html=False, include_plotlyjs=False)}
</div>

<div class="card">

<h2>
Object Distribution (Top 20)
</h2>

{object_distribution.to_html(index=False)}

</div>

</div>

<div class="card section">

<h2>
Current Persisted Object Counts
</h2>

{counts_df.to_html(index=False)}

</div>

<div class="card section">

<h2>
Latest 20 API Requests
</h2>

{latest_requests.to_html(index=False)}

</div>

<div class="card section">

<h2>
Latest 20 Predictions
</h2>

{latest_predictions.to_html(index=False)}

</div>

</body>

</html>
"""

dashboard_path = (
    f"{OUTPUT_DIR}/dashboard.html"
)

with open(
    dashboard_path,
    "w",
    encoding="utf-8"
) as f:
    f.write(html)

print(
    f"Dashboard generated: {dashboard_path}"
)

webbrowser.open(
    os.path.abspath(
        dashboard_path
    )
)
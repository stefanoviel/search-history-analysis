import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

df = pd.read_csv('data/gemini_topics.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

df['Date'] = pd.to_datetime(df['timestamp'])

df_monthly_counts = df.groupby([
    pd.Grouper(key='Date', freq='M'),  # Group by month
    'Topic_Name'                       # Group by topic name
]).size().reset_index(name='Topic_Count')

df_monthly_counts = df_monthly_counts.rename(columns={'Date': 'Month_Ending_Date'})

print("Generating interactive Plotly chart...")
fig = px.line(
    df_monthly_counts,
    x='Month_Ending_Date',
    y='Topic_Count',
    color='Topic_Name',
    title='Monthly Trend of Topic Queries Over Time',
    labels={
        "Month_Ending_Date": "Month Ending Date",
        "Topic_Count": "Count of Queries",
        "Topic_Name": "Topic"
    }
)

for trace in fig.data:
    trace.visible = 'legendonly'

fig.update_layout(
    xaxis_title="Month Ending Date",
    yaxis_title="Count of Queries (Monthly)", # Updated label
    hovermode="x unified",
    legend_title="Click to Toggle Topic Visibility",
    font=dict(family="Inter, sans-serif", size=12)
)

fig.update_xaxes(
    dtick="M1",  # Tick every month
    tickformat="%b %Y", # Display date clearly (e.g., Oct 2025)
    rangeslider_visible=True # Add a slider for zooming in on the time range
)

fig.show()
print("\nProcessing complete. The interactive plot should now be displayed.")



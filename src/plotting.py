import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

df = pd.read_csv('google_search_topics.csv')


# IMPORTANT: Ensure the 'Date' column is a proper datetime object
df['Date'] = pd.to_datetime(df['Date'])

# --- 2. Data Aggregation (Weekly) ---

# Aggregate data weekly ('W' frequency) by counting Topic_Name occurrences.
# pd.Grouper is used to group the data based on the time frequency.
df_monthly_counts = df.groupby([
    pd.Grouper(key='Date', freq='M'),  # Group by week (The output date is the end of the week)
    'Topic_Name'                       # Group by topic name
]).size().reset_index(name='Topic_Count')


# Rename the date column for clarity (after reset_index, the date index becomes a column named 'Date')
df_monthly_counts = df_monthly_counts.rename(columns={'Date': 'Month_Ending_Date'})

# --- 3. Interactive Plotly Visualization ---

print("Generating interactive Plotly chart...")

# Create the base Plotly figure using Plotly Express
# Use the new monthly aggregated data
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

# Modify the traces to start hidden (legendonly)
for trace in fig.data:
    trace.visible = 'legendonly'

# Update layout for aesthetics and clarity
fig.update_layout(
    xaxis_title="Month Ending Date",
    yaxis_title="Count of Queries (Monthly)", # Updated label
    hovermode="x unified",
    legend_title="Click to Toggle Topic Visibility",
    font=dict(family="Inter, sans-serif", size=12)
)

# Customize the X-axis to show monthly ticks and format
fig.update_xaxes(
    dtick="M1",  # Tick every month
    tickformat="%b %Y", # Display date clearly (e.g., Oct 2025)
    rangeslider_visible=True # Add a slider for zooming in on the time range
)

# Display the figure
# When you run this, it will open an interactive HTML plot in your browser
fig.show()

# If running in an environment that requires HTML output (like a Jupyter notebook),
# you can use fig.to_html()
# print(fig.to_html())

print("\nProcessing complete. The interactive plot should now be displayed.")



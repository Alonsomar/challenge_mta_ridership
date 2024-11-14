# Contains functions to generate Plotly figures used in the app.

import plotly.express as px

def generate_overview_chart(df):
    fig = px.line(
        df,
        x='Date',
        y='Daily Ridership/Traffic Volume',
        title='Overall Ridership Over Time'
    )
    return fig

def generate_mode_comparison_chart(df):
    fig = px.bar(
        df,
        x='Date',
        y='Daily Ridership/Traffic Volume',
        color='Mode of Transportation',
        title='Ridership by Transportation Mode'
    )
    return fig

def generate_recovery_heatmap(df):
    # Example of creating a heatmap
    pivot_table = df.pivot_table(
        values='Percentage of Pre-Pandemic Baseline',
        index='Mode of Transportation',
        columns='Date'
    )
    fig = px.imshow(
        pivot_table,
        aspect='auto',
        title='Recovery Trends Heatmap'
    )
    return fig

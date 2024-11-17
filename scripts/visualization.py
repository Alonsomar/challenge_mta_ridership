# Contains functions to generate Plotly figures used in the app.

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def generate_overview_chart(df):
    """Generate overview line chart with options for daily, weekly, and bi-weekly smoothing"""
    # Calculate moving averages for each mode
    df_smooth_7 = df.copy()
    df_smooth_14 = df.copy()
    
    # Calculate both 7-day and 14-day moving averages
    df_smooth_7['Ridership'] = df.groupby('Mode')['Ridership'].transform(
        lambda x: x.rolling(window=7, center=True).mean()
    )
    df_smooth_14['Ridership'] = df.groupby('Mode')['Ridership'].transform(
        lambda x: x.rolling(window=14, center=True).mean()
    )

    custom_colors = {
        'Subways': '#345995',
        'Buses': '#03cea4',
        'LIRR': '#e40066',
        'Metro-North': '#eac435',
        'Access-A-Ride': '#fb4d3d',
        'Bridges and Tunnels': '#234985',
        'Staten Island Railway': '#02a87d'
    }
    
    # Create figure
    fig = go.Figure()
    
    # Add traces for each mode - daily, 7-day, and 14-day averages
    for mode in df['Mode'].unique():
        mode_data = df[df['Mode'] == mode]
        mode_smooth_7 = df_smooth_7[df_smooth_7['Mode'] == mode]
        mode_smooth_14 = df_smooth_14[df_smooth_14['Mode'] == mode]
        
        # Daily data (initially hidden)
        fig.add_trace(
            go.Scatter(
                x=mode_data['Date'],
                y=mode_data['Ridership'],
                name=f"{mode} (Daily)",
                line=dict(color=custom_colors[mode], width=1),
                visible='legendonly'
            )
        )
        
        # 7-day average (shown by default)
        fig.add_trace(
            go.Scatter(
                x=mode_smooth_7['Date'],
                y=mode_smooth_7['Ridership'],
                name=f"{mode} (7-Day Avg)",
                line=dict(color=custom_colors[mode], width=2.5),
                visible=True
            )
        )
        
        # 14-day average (initially hidden)
        fig.add_trace(
            go.Scatter(
                x=mode_smooth_14['Date'],
                y=mode_smooth_14['Ridership'],
                name=f"{mode} (14-Day Avg)",
                line=dict(color=custom_colors[mode], width=3),
                visible=False
            )
        )
    
    # Update layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title={
            'text': 'Overall Ridership Trends',
            'font': {'size': 24, 'color': '#2c3e50'},
            'x': 0.02,
            'y': 0.95
        },
        font={'color': '#2c3e50'},
        legend=dict(
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1,
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        hovermode='x unified',
        autosize=True,
        height=450,
        margin=dict(l=40, r=40, t=120, b=100),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.1)',
            title="Date"
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.1)',
            title="Ridership"
        )
    )
    
    # Update buttons position and styling
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.02,
                y=1.15,  # Moved up
                xanchor='left',
                yanchor='top',
                showactive=True,
                buttons=list([
                    dict(
                        label="7-Day Average",
                        method="update",
                        args=[{"visible": [False, True, False] * len(df['Mode'].unique())},
                              {"title": {"text": "Overall Ridership Trends (7-Day Average)",
                                       "y": 0.95}}]  # Adjusted title position
                    ),
                    dict(
                        label="14-Day Average",
                        method="update",
                        args=[{"visible": [False, False, True] * len(df['Mode'].unique())},
                              {"title": {"text": "Overall Ridership Trends (14-Day Average)",
                                       "y": 0.95}}]
                    ),
                    dict(
                        label="Daily Values",
                        method="update",
                        args=[{"visible": [True, False, False] * len(df['Mode'].unique())},
                              {"title": {"text": "Overall Ridership Trends (Daily Values)",
                                       "y": 0.95}}]
                    ),
                ]),
                pad={"r": 10, "t": 10, "b": 10, "l": 10},  # Added padding
                bgcolor="white",
                bordercolor="#dee2e6",
                borderwidth=1,
                active=0,  # Set first button as active by default
                font={"size": 12, "color": "#2c3e50"}
            )
        ]
    )
    
    return fig

def generate_mode_comparison_chart(df):
    """Generate a comparative bar chart with animation capabilities."""
    fig = px.bar(
        df,
        x='Mode',
        y='Ridership',
        color='Mode',
        animation_frame=df['Date'].dt.strftime('%Y-%m'),
        range_y=[0, df['Ridership'].max() * 1.1],
        title='Monthly Ridership by Mode'
    )
    
    fig.update_layout(
        autosize=True,
        height=400,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig

def generate_recovery_heatmap(df):
    """Generate a heatmap showing recovery patterns."""
    pivot_df = df.pivot_table(
        values='Recovery_Percentage',
        index=df['Date'].dt.dayofweek,
        columns='Mode',
        aggfunc='mean'
    )
    
    fig = px.imshow(
        pivot_df,
        title='Recovery Patterns by Day of Week',
        labels=dict(
            x='Mode of Transportation',
            y='Day of Week',
            color='% of Pre-Pandemic'
        ),
        aspect='auto'
    )
    
    fig.update_layout(
        autosize=True,
        height=400,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig

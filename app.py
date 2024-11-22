import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

from scripts.data_processing import MTARidershipData
from scripts.visualization import (
    generate_overview_chart,
    generate_mode_comparison_chart,
    generate_recovery_timeline,
    generate_weekday_weekend_comparison,
    generate_monthly_recovery_heatmap,
    generate_yearly_comparison_chart,
    filter_data
)

# Import the sidebar component and styles
from components.sidebar import sidebar, SIDEBAR_STYLE, SIDEBAR_HIDDEN

# Initialize and load data
mta_data = MTARidershipData('data/MTA_Daily_Ridership.csv')
mta_data.load_raw_data()
mta_data.process_data()

# Add this helper function at the top of the file
def create_tooltip(target_id, tooltip_text):
    """Create a tooltip for a given element"""
    return dbc.Tooltip(
        tooltip_text,
        target=target_id,
        placement="auto",  # Changed from "top" to "auto"
        delay={"show": 200, "hide": 50},
        style={
            "maxWidth": "300px",
            "fontSize": "0.875rem",
            "textAlign": "left",
            "backgroundColor": "rgba(0, 0, 0, 0.8)",
            "color": "white",
            "padding": "8px 12px",
            "borderRadius": "4px",
            "zIndex": 1000
        }
    )

# Initialize the app
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.FLATLY,
        'https://use.fontawesome.com/releases/v5.15.4/css/all.css'
    ],
    external_scripts=[
        'https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.min.js'
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

app.title = "MTA Challenge"

# Filters and controls
controls = dbc.Card([
    dbc.CardBody([
        html.H4("Filters", className="card-title"),
        html.Div([
            html.Div([
                html.Label("Select Transportation Mode", className="mb-2"),
                html.I(className="fas fa-info-circle ms-2", id="mode-selector-info"),
            ], className="d-flex align-items-center mb-2"),
            dcc.Dropdown(
                id='mode-selector',
                options=[
                    {'label': html.Div([
                        html.I(className="fas fa-subway me-2"),
                        "Subways"
                    ], style={'display': 'flex', 'alignItems': 'center'}), 'value': 'Subways'},
                    {'label': html.Div([
                        html.I(className="fas fa-bus me-2"),
                        "Buses"
                    ], style={'display': 'flex', 'alignItems': 'center'}), 'value': 'Buses'},
                    {'label': html.Div([
                        html.I(className="fas fa-train me-2"),
                        "LIRR"
                    ], style={'display': 'flex', 'alignItems': 'center'}), 'value': 'LIRR'},
                    {'label': html.Div([
                        html.I(className="fas fa-train me-2"),
                        "Metro-North"
                    ], style={'display': 'flex', 'alignItems': 'center'}), 'value': 'Metro-North'},
                    {'label': html.Div([
                        html.I(className="fas fa-wheelchair me-2"),
                        "Access-A-Ride"
                    ], style={'display': 'flex', 'alignItems': 'center'}), 'value': 'Access-A-Ride'},
                    {'label': html.Div([
                        html.I(className="fas fa-road me-2"),
                        "Bridges and Tunnels"
                    ], style={'display': 'flex', 'alignItems': 'center'}), 'value': 'Bridges and Tunnels'},
                    {'label': html.Div([
                        html.I(className="fas fa-subway me-2"),
                        "Staten Island Railway"
                    ], style={'display': 'flex', 'alignItems': 'center'}), 'value': 'Staten Island Railway'}
                ],
                value=['Subways', 'Buses', 'LIRR', 'Metro-North', 'Access-A-Ride', 'Bridges and Tunnels', 'Staten Island Railway'],
                multi=True,
                className="mode-selector-dropdown"
            ),
        ], className="mb-4"),
    ])
], className="filters-card shadow-sm")

# Enhanced summary cards
summary_cards = dbc.Row([
    # Total Ridership Card
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.H4("Total Ridership", className="card-title text-center mb-1"),
                    html.I(className="fas fa-info-circle ms-2", id="ridership-info"),
                ], className="d-flex justify-content-center align-items-center"),
                html.H2(id="total-ridership", className="text-center text-primary my-3"),
                html.P(id="ridership-trend", className="text-center mb-0"),
                html.P("vs previous 30-day period", className="text-muted text-center small"),
                dbc.Progress(id="trend-progress", className="my-2"),
            ], className="position-relative")
        ], className="h-100 shadow-sm border-primary")
    ], width=4),
    
    # Recovery Progress Card
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.H4("Recovery Progress", className="card-title text-center mb-1"),
                    html.I(className="fas fa-info-circle ms-2", id="recovery-info"),
                ], className="d-flex justify-content-center align-items-center"),
                dcc.Graph(
                    id="recovery-gauge", 
                    config={'displayModeBar': False},
                    className="my-2"
                ),
                html.P("Compared to pre-pandemic baseline", className="text-muted text-center small mb-0")
            ])
        ], className="h-100 shadow-sm border-success")
    ], width=4),
    
    # Mode Rankings Card
    dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.H4("Mode Rankings", className="card-title text-center mb-1"),
                    html.I(className="fas fa-info-circle ms-2", id="rankings-info"),
                ], className="d-flex justify-content-center align-items-center"),
                dash_table.DataTable(
                    id='mode-rankings',
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px',
                        'fontFamily': '"Segoe UI", sans-serif'
                    },
                    style_header={
                        'fontWeight': 'bold',
                        'backgroundColor': '#f8f9fa',
                        'borderBottom': '2px solid #dee2e6'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f8f9fa'
                        }
                    ],
                    page_size=5
                )
            ])
        ], className="h-100 shadow-sm border-info")
    ], width=4),
])

# Update the tooltips collection
tooltips = html.Div([
    # Existing tooltips
    create_tooltip(
        "ridership-info",
        """Total ridership across selected modes for the chosen period. 
        The trend shows the percentage change compared to the previous 30-day period, 
        helping identify short-term ridership patterns."""
    ),
    create_tooltip(
        "recovery-info",
        """Recovery progress measures current ridership as a percentage of pre-pandemic (2019) baseline. 
        Baseline values are calculated using corresponding day types (weekday/weekend) from 2019. 
        100% indicates full recovery to pre-pandemic levels."""
    ),
    create_tooltip(
        "rankings-info",
        """Comparative performance of different transportation modes showing:
        • Total ridership volume
        • Recovery percentage vs 2019 baseline
        Updated based on selected date range."""
    ),
    
    # New tooltips for filters
    create_tooltip(
        "mode-selector-info",
        """Select one or multiple transportation modes to analyze:
        • Subways: MetroCard and OMNY swipes/taps
        • Buses: MetroCard and OMNY swipes/taps
        • LIRR: Ticket sales data
        • Metro-North: Ticket sales data
        • Access-A-Ride: Scheduled trips
        • Bridges and Tunnels: Toll collection data"""
    ),
    
    # New tooltips for charts
    create_tooltip(
        "overview-chart-info",
        """Daily ridership trends across all selected modes.
        • Toggle between daily, weekly, and bi-weekly averages
        • Shows seasonal patterns and long-term trends
        • Helps identify recovery patterns post-pandemic"""
    ),
    create_tooltip(
        "mode-comparison-info",
        """Compare ridership patterns between different modes:
        • Relative recovery rates
        • Seasonal variations
        • Peak vs. off-peak patterns
        • Modal shift trends"""
    ),
    create_tooltip(
        "recovery-heatmap-info",
        """Visualize recovery patterns by day and mode:
        • Darker colors indicate higher recovery rates
        • Weekday vs. weekend patterns
        • Seasonal variations in recovery
        • Mode-specific recovery trends"""
    ),
    create_tooltip(
        "yearly-comparison-info",
        """Compare ridership patterns across different years:
        • 7-day moving average for smoother visualization
        • Year-over-year seasonal patterns
        • Recovery progression across years
        • Monthly ridership trends"""
    ),
    create_tooltip(
        "recovery-timeline-info",
        """Visualize recovery patterns over time:
        • Shows recovery progression across different modes
        • Helps identify recovery patterns post-pandemic"""
    ),
    create_tooltip(
        "weekday-weekend-info",
        """Compare ridership patterns between weekdays and weekends:
        • Shows seasonal variations in ridership
        • Helps identify peak vs. off-peak patterns"""
    ),
    create_tooltip(
        "monthly-recovery-info",
        """Visualize monthly recovery patterns:
        • Shows recovery progression across different modes
        • Helps identify seasonal variations in recovery"""
    )
])

# Update the chart sections to include info icons
def create_chart_section(title, chart_id, info_id, info_icon=True, additional_controls=None):
    """Helper function to create consistent chart sections with tooltips"""
    return html.Section([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2(title, className="section-header"),
                    html.I(className="fas fa-info-circle ms-2", id=info_id) if info_icon else None,
                ], className="d-flex align-items-center mb-3"),
                additional_controls if additional_controls else None,
                html.Div([
                    dcc.Graph(
                        id=chart_id,
                        config={'displayModeBar': False, 'responsive': True}
                    )
                ], className="chart-container")
            ], width=12)
        ], className="mb-4")
    ], id=f"section-{chart_id}")

# Layout actualizado
app.layout = html.Div([
    dcc.Location(id='url'),
    # Barra superior con toggle y enlaces
    html.Div([
        # Lado izquierdo con toggle y título
        html.Div([
            dbc.Button(
                html.I(className="fas fa-bars"),
                id="btn_sidebar",
                n_clicks=0,
            ),
            html.H1([
                html.I(className="fas fa-subway me-2", 
                      style={"color": "var(--saffron)"}),
                "MTA Dashboard"
            ], className="top-bar-title"),
        ], className="top-bar-left"),
        
        # Lado derecho con enlaces
        html.Div([
            html.A(
                html.I(className="fas fa-globe"),
                href="https://alonsovaldes.com",
                target="_blank",
                className="top-bar-link",
                title="Visit Alonso's Website"
            ),
            html.A(
                html.I(className="fab fa-github"),
                href="https://github.com/Alonsomar/challenge_mta_ridership",
                target="_blank",
                className="top-bar-link",
                title="View on GitHub"
            ),
        ], className="top-bar-right"),
    ], className="top-bar"),
    
    # Sidebar sin el toggle
    sidebar,
    
    # Contenido principal
    html.Div(
        [
            tooltips,
            dbc.Container([
                dbc.Row([dbc.Col([controls], md=12)], className="mb-4"),
                dbc.Row([dbc.Col([summary_cards], md=12)], className="summary-cards"),
                create_chart_section("Ridership Trends", "overview-chart", "overview-chart-info"),
                create_chart_section("Mode Comparison", "mode-comparison-chart", "mode-comparison-info"),
                create_chart_section(
                    "Year-over-Year Comparison", 
                    "yearly-comparison-chart", 
                    "yearly-comparison-info",
                    additional_controls=html.Div([
                        html.Label("Select Mode for Comparison", className="mb-2"),
                        dcc.Dropdown(
                            id='yearly-comparison-mode',
                            options=[{'label': mode, 'value': mode} 
                                    for mode in mta_data.processed_data['Mode'].unique()],
                            value='Subways',
                            clearable=False,
                            className="mb-4"
                        )
                    ])
                ),
                html.Div([
                    create_chart_section(
                        "Recovery Timeline Analysis", 
                        "recovery-timeline", 
                        "recovery-timeline-info"
                    ),
                    create_chart_section(
                        "Weekday vs Weekend Patterns", 
                        "weekday-weekend-comparison", 
                        "weekday-weekend-info"
                    ),
                    create_chart_section(
                        "Monthly Recovery Patterns", 
                        "monthly-recovery-heatmap", 
                        "monthly-recovery-info"
                    )
                ], className="recovery-analysis-container")
            ], fluid=True)
        ],
        id="page-content",
        style={
            "marginTop": "60px",  # Ajustar para la barra superior
            "marginLeft": "16rem",  # Ajustar al ancho del sidebar
            "transition": "all 0.2s"
        }
    )
])


# Callback to toggle the sidebar
@app.callback(
    [Output("sidebar", "style"), Output("page-content", "style")],
    [Input("btn_sidebar", "n_clicks")],
    [State("sidebar", "style"), State("page-content", "style")]
)
def toggle_sidebar(n_clicks, sidebar_style, content_style):
    """Toggle the sidebar visibility and adjust the page content margin."""
    if n_clicks and n_clicks % 2 == 1:
        # Hide sidebar
        sidebar_style = SIDEBAR_HIDDEN
        content_style = {**content_style, "margin-left": "0rem"}
    else:
        # Show sidebar
        sidebar_style = SIDEBAR_STYLE
        content_style = {**content_style, "margin-left": "16rem"}
    return sidebar_style, content_style


# Callbacks
@app.callback(
    [Output('overview-chart', 'figure'),
     Output('mode-comparison-chart', 'figure')],
    [Input('mode-selector', 'value')]
)
def update_charts(selected_modes):
    # Filter data based on selections
    filtered_data = mta_data.processed_data[
        mta_data.processed_data['Mode'].isin(selected_modes)
    ]
    
    # Get timeline events
    timeline_events = mta_data.timeline_events
    
    # Generate figures
    overview_fig = generate_overview_chart(filtered_data, timeline_events)
    comparison_fig = generate_mode_comparison_chart(filtered_data)
    
    return overview_fig, comparison_fig

@app.callback(
    [Output('total-ridership', 'children'),
     Output('ridership-trend', 'children'),
     Output('trend-progress', 'value'),
     Output('trend-progress', 'color'),
     Output('recovery-gauge', 'figure'),
     Output('mode-rankings', 'data'),
     Output('mode-rankings', 'columns')],
    [Input('mode-selector', 'value')]
)
def update_summary_stats(selected_modes):
    filtered_data = mta_data.processed_data[
        mta_data.processed_data['Mode'].isin(selected_modes)
    ]
    
    # Enhanced total ridership calculation
    total_ridership = filtered_data['Ridership'].sum()
    formatted_ridership = f"{total_ridership:,.0f}"
    
    # Improved trend calculation using rolling averages
    end_date_dt = filtered_data['Date'].max()
    
    current_period = filtered_data[
        filtered_data['Date'] >= (end_date_dt - timedelta(days=30))
    ]['Ridership'].mean()
    
    previous_period = filtered_data[
        (filtered_data['Date'] < (end_date_dt - timedelta(days=30))) &
        (filtered_data['Date'] >= (end_date_dt - timedelta(days=60)))
    ]['Ridership'].mean()
    
    trend_pct = ((current_period / previous_period) - 1) * 100 if previous_period > 0 else 0
    
    # Enhanced trend formatting
    trend_icon = "↑" if trend_pct > 0 else "↓"
    trend_color = "success" if trend_pct > 0 else "danger"
    trend_text = f"{trend_icon} {abs(trend_pct):.1f}% ({current_period:,.0f} avg. daily riders)"
    progress_value = min(abs(trend_pct), 100)
    
    # Enhanced recovery calculation
    avg_recovery = filtered_data.groupby('Date')['Recovery_Percentage'].mean().mean()
    peak_recovery = filtered_data.groupby('Date')['Recovery_Percentage'].mean().max()
    
    # Update gauge figure with peak recovery annotation
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=avg_recovery * 100,
        delta={'reference': peak_recovery * 100, 'relative': False},
        title={'text': "Recovery Rate", 'font': {'size': 24, 'color': '#345995'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': '#2c3e50'},
            'bar': {'color': '#345995'},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': '#f8f9fa',
            'steps': [
                {'range': [0, 50], 'color': 'rgba(251, 77, 61, 0.1)'},
                {'range': [50, 75], 'color': 'rgba(234, 196, 53, 0.1)'},
                {'range': [75, 100], 'color': 'rgba(3, 206, 164, 0.1)'}
            ],
            'threshold': {
                'line': {'color': '#e40066', 'width': 4},
                'thickness': 0.75,
                'value': peak_recovery * 100
            }
        }
    ))
    
    gauge_fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor='white',
        font={'family': "Arial"}
    )
    
    # Enhanced rankings table
    rankings_df = filtered_data.groupby('Mode').agg({
        'Ridership': 'sum',
        'Recovery_Percentage': 'mean'
    }).round(2)
    
    # Format the values before converting to records
    rankings_df['Ridership'] = rankings_df['Ridership'].apply(lambda x: f"{x:,.0f}")
    rankings_df['Recovery_Percentage'] = rankings_df['Recovery_Percentage'].apply(lambda x: f"{x:.1f}%")
    rankings_df = rankings_df.sort_values('Ridership', ascending=False)
    
    rankings_data = rankings_df.reset_index().to_dict('records')
    rankings_columns = [
        {'name': 'Mode', 'id': 'Mode'},
        {'name': 'Total Ridership', 'id': 'Ridership'},
        {'name': 'Recovery %', 'id': 'Recovery_Percentage'}
    ]
    
    return (
        formatted_ridership,
        trend_text,
        progress_value,
        trend_color,
        gauge_fig,
        rankings_data,
        rankings_columns
    )

@app.callback(
    Output('yearly-comparison-chart', 'figure'),
    Input('yearly-comparison-mode', 'value')
)
def update_yearly_comparison(selected_mode):
    return generate_yearly_comparison_chart(
        mta_data.processed_data,  # Use full dataset
        selected_mode
    )

@app.callback(
    [Output("recovery-timeline", "figure"),
     Output("weekday-weekend-comparison", "figure"),
     Output("monthly-recovery-heatmap", "figure")],
    [Input("mode-selector", "value")]
)
def update_recovery_analysis(selected_modes):
    filtered_data = filter_data(mta_data, selected_modes)
    
    return (
        generate_recovery_timeline(filtered_data),
        generate_weekday_weekend_comparison(filtered_data),
        generate_monthly_recovery_heatmap(filtered_data)
    )

app.clientside_callback(
    """
    function(url) {
        if (url && url.includes('#')) {
            var element_id = url.split('#')[1];
            var element = document.getElementById(element_id);
            if (element) {
                element.scrollIntoView({behavior: 'smooth', block: 'start'});
            }
        }
    }
    """,
    Output('url', 'pathname'),  # Este Output no se usará realmente
    Input('url', 'href')
)

if __name__ == '__main__':
    app.run_server(debug=True)
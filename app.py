import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd

from scripts.data_processing import load_data
from scripts.visualization import (
    generate_overview_chart,
    generate_mode_comparison_chart,
    generate_recovery_heatmap
)

# Load and preprocess data
df = load_data('data/mta_ridership.csv')

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server  # For deployment with services like Heroku

# App layout
app.layout = html.Div([
    # Background Animation
    html.Script(src="/assets/background_animation.js"),
    # Navigation Bar
    dbc.NavbarSimple(
        brand="MTA Ridership Dashboard",
        brand_href="#",
        color="dark",
        dark=True,
        fixed="top",
        children=[
            dbc.NavItem(dbc.NavLink("Overview", href="#section-1")),
            dbc.NavItem(dbc.NavLink("Mode Comparison", href="#section-2")),
            dbc.NavItem(dbc.NavLink("Recovery Trends", href="#section-3")),
        ]
    ),
    # Content Sections
    html.Div([
        # Section 1: Overview
        html.Section(id='section-1', className='section', children=[
            html.H2("General Ridership Trends Over Time"),
            dcc.Graph(figure=generate_overview_chart(df))
        ]),
        # Section 2: Mode Comparison
        html.Section(id='section-2', className='section', children=[
            html.H2("Comparative Ridership by Transportation Mode"),
            dcc.Graph(figure=generate_mode_comparison_chart(df))
        ]),
        # Section 3: Recovery Trends
        html.Section(id='section-3', className='section', children=[
            html.H2("Pre-Pandemic vs Post-Pandemic Recovery Trends"),
            dcc.Graph(figure=generate_recovery_heatmap(df))
        ]),
    ], className='content')
])

# Callbacks can be added here for interactivity

if __name__ == '__main__':
    app.run_server(debug=True)

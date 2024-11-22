# sidebar.py

import dash_bootstrap_components as dbc
from dash import html

# Updated color palette using CSS variables
COLORS = {
    'background': '#f5f7fa',
    'primary': '#345995',
    'secondary': '#eac435',
    'accent': '#03cea4',
    'text': '#2c3e50',
    'hover_bg': 'rgba(3, 206, 164, 0.1)'
}

# Enhanced sidebar styles with better contrast and positioning
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": "60px",
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "1rem",
    "background": "linear-gradient(135deg, #345995, #2c3e50)",
    "transition": "all 0.2s",
    "overflow": "auto",
    "boxShadow": "2px 0 10px rgba(0,0,0,0.1)",
    "zIndex": 900,
}

# Updated hidden sidebar style
SIDEBAR_HIDDEN = {
    **SIDEBAR_STYLE,
    "left": "-16rem",
}

# Create the sidebar with enhanced styling
sidebar = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavLink([
                    html.I(className="fas fa-chart-line me-2"),
                    "Ridership Trends"
                ], href="#section-overview-chart", id="link-overview", active="exact"),
                dbc.NavLink([
                    html.I(className="fas fa-exchange-alt me-2"),
                    "Mode Comparison"
                ], href="#section-mode-comparison-chart", id="link-mode-comparison", active="exact"),
                dbc.NavLink([
                    html.I(className="fas fa-chart-area me-2"),
                    "Year-over-Year"
                ], href="#section-yearly-comparison-chart", id="link-yearly-comparison", active="exact"),
                dbc.NavLink([
                    html.I(className="fas fa-chart-line me-2"),
                    "Recovery Timeline"
                ], href="#section-recovery-timeline", id="link-recovery-timeline", active="exact"),
                dbc.NavLink([
                    html.I(className="fas fa-calendar-alt me-2"),
                    "Weekday vs Weekend"
                ], href="#section-weekday-weekend-comparison", id="link-weekday-weekend", active="exact"),
                dbc.NavLink([
                    html.I(className="fas fa-th me-2"),
                    "Monthly Patterns"
                ], href="#section-monthly-recovery-heatmap", id="link-monthly-recovery", active="exact"),
            ],
            vertical=True,
            pills=True,
            className="sidebar-nav"
        ),
    ],
    id="sidebar",
    style=SIDEBAR_STYLE
)

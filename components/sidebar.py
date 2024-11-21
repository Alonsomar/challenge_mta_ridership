from dash import html
import dash_bootstrap_components as dbc

def sidebar():
    return html.Div(
        [
            html.H2("Dashboard", className="sidebar-title"),
            html.Hr(),
            dbc.Nav(
                [
                    dbc.NavLink("Overview", href="/overview", id="overview-link"),
                    dbc.NavLink("Mode Comparison", href="/mode-comparison", id="mode-comparison-link"),
                    dbc.NavLink("Recovery Trends", href="/recovery-trends", id="recovery-trends-link"),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        className="sidebar",
    )

from dash import dcc, html
import dash_bootstrap_components as dbc

def filters(data):
    return dbc.Card(
        dbc.CardBody(
            [
                html.H4("Filters", className="card-title"),
                dcc.Dropdown(
                    id="mode-selector",
                    options=[{"label": mode, "value": mode} for mode in data['Mode'].unique()],
                    value=data['Mode'].unique().tolist(),
                    multi=True,
                ),
                dcc.DatePickerRange(
                    id="date-range",
                    min_date_allowed=data['Date'].min(),
                    max_date_allowed=data['Date'].max(),
                    start_date=data['Date'].min(),
                    end_date=data['Date'].max(),
                ),
            ]
        ),
        className="filters-card",
    )

# Contains functions to generate Plotly figures used in the app.

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta
import pandas as pd
from functools import lru_cache
import numpy as np

# Global variables for caching
RIDERSHIP_ARRAY = None
MODE_INDICES = None

def initialize_cache_arrays(data):
    """Initialize global cache arrays for faster filtering"""
    global RIDERSHIP_ARRAY, MODE_INDICES
    RIDERSHIP_ARRAY = data.processed_data.to_records(index=False)
    unique_modes = data.processed_data['Mode'].unique()
    MODE_INDICES = {mode: idx for idx, mode in enumerate(unique_modes)}

def _prepare_modes_for_cache(modes):
    """Helper function to prepare modes for caching"""
    if modes is None:
        return ('Subways',)
    if isinstance(modes, str):
        return (modes,)
    return tuple(sorted(modes))  # Sort to ensure consistent caching

@lru_cache(maxsize=128)
def _cached_filter(modes_tuple, start_date=None, end_date=None):
    """Internal cached function that works with tuples"""
    mode_mask = np.isin(RIDERSHIP_ARRAY['Mode'], modes_tuple)
    filtered_array = RIDERSHIP_ARRAY[mode_mask]
    
    if start_date and end_date:
        date_mask = (filtered_array['Date'] >= start_date) & (filtered_array['Date'] <= end_date)
        filtered_array = filtered_array[date_mask]
    
    return pd.DataFrame.from_records(filtered_array)

def filter_data(data, modes):
    """Public interface for filtering data"""
    modes_tuple = _prepare_modes_for_cache(modes)
    return _cached_filter(modes_tuple)

def apply_chart_template(fig, title=None, height=500):
    """Apply consistent styling to all charts"""
    fig.update_layout(
        height=height,
        title=dict(
            text=title if title else "",
            font=dict(size=24, color='#2c3e50'),
            x=0.5,
            y=0.95
        ),
        template='plotly_white',
        margin=dict(l=60, r=150, t=100, b=60),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.05,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Roboto')
    )
    return fig

def generate_overview_chart(df, timeline_events=None):
    """Enhanced overview chart with improved timeline annotations and context"""
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
                line=dict(
                    color=custom_colors[mode],
                    width=1,
                    dash='solid'
                ),
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

    # Update layout without buttons, keeping right-side legend
    fig.update_layout(
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.05,  # Position legend to the right of the chart
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1,
            font=dict(size=11, family='Arial')
        ),
        margin=dict(
            l=60,
            r=150,  # Right margin for legend
            t=150,  # Increased top margin for staggered annotations
            b=60
        )
    )

    # Enhanced timeline annotations with impact levels and phases
    if timeline_events is not None:
        annotations = []
        
        # Sort events chronologically
        timeline_events = timeline_events.sort_values('date', ascending=True)
        
        # Enhanced color scheme for events
        colors = {
            'health': {
                'critical': '#DC3545',
                'major': '#DE6B48',
                'moderate': '#E19578'
            },
            'policy': {
                'critical': '#28A745',
                'major': '#43AA8B',
                'moderate': '#90BE6D'
            }
        }

        aditional_offset = 0.02
        # Phase markers
        phase_positions = {
            'initial': 0.45,
            'lockdown': 0.50 + aditional_offset*1,
            'early_recovery': 0.55+ aditional_offset*2,
            'adaptation': 0.60+ aditional_offset*3,
            'recovery': 0.65+ aditional_offset*4,
            'late_recovery': 0.70+ aditional_offset*5,
            'new_normal': 0.75+ aditional_offset*6
        }

        for i, (_, event) in enumerate(timeline_events.iterrows()):
            color = colors[event['category']][event['impact_level']]
            y_position = phase_positions[event['phase']]
            
            # Add vertical reference line
            fig.add_shape(
                type="line",
                x0=event['date'],
                x1=event['date'],
                y0=0,
                y1=y_position - 0.02,
                yref="paper",
                line=dict(
                    color=color,
                    width=1,
                    dash="dot"
                ),
                opacity=0.6
            )
            
            # Add enhanced annotation with hover text
            annotations.append(dict(
                x=event['date'],
                y=y_position,
                xref='x',
                yref='paper',
                text=f"<b>{event['event']}</b>",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1.5,
                arrowcolor=color,
                ax=0,
                ay=-20,
                bordercolor=color,
                borderwidth=1,
                borderpad=4,
                bgcolor='rgba(255, 255, 255, 0.95)',
                opacity=1,
                font=dict(
                    size=11,
                    color='#2c3e50',
                    family='Arial'
                ),
                hovertext=(
                    f"<b><span style='font-size:14px;color:#2c3e50'>{event['description']}</span></b><br><br>"
                    f"<span style='color:#1f77b4'><b>Impact:</b></span> {event['ridership_impact']}<br>"
                    f"<span style='color:#2ca02c'><b>Phase:</b></span> {event['phase']}<br>" 
                    f"<span style='color:#d62728'><b>Impact Level:</b></span> {event['impact_level']}"
                )
            ))

        fig.update_layout(annotations=annotations)

    return apply_chart_template(fig, title="Overview", height=550)

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
    
    
    return apply_chart_template(
        fig,
        title="Monthly Ridership by Mode",
        height=550
    )

def generate_recovery_timeline(filtered_data):
    """Generate the recovery timeline visualization"""
    fig = go.Figure()
    
    # Custom colors (keep the same color dictionary)
    colors = {
        'Subways': '#345995',
        'Buses': '#03cea4',
        'LIRR': '#e40066',
        'Metro-North': '#eac435',
        'Access-A-Ride': '#fb4d3d',
        'Bridges and Tunnels': '#234985',
        'Staten Island Railway': '#02a87d'
    }
    
    for mode in filtered_data['Mode'].unique():
        mode_data = filtered_data[filtered_data['Mode'] == mode]
        recovery_ma = mode_data.sort_values('Date').set_index('Date')['Recovery_Percentage'].rolling(30).mean()
        
        fig.add_trace(
            go.Scatter(
                x=recovery_ma.index,
                y=recovery_ma * 100,
                name=mode,
                line=dict(color=colors[mode], width=2),
                hovertemplate="<b>%{x}</b><br>" +
                            f"{mode}<br>" +
                            "Recovery: %{y:.1f}%<extra></extra>"
            )
        )
        
    return apply_chart_template(fig, title="Recovery Timeline: Different Paths to Normal", height=550)

def generate_weekday_weekend_comparison(filtered_data):
    """Generate an enhanced weekday vs weekend violin plot with split violins"""
    fig = go.Figure()
    
    # Base colors
    base_colors = {
        'Subways': '#345995',
        'Buses': '#03cea4',
        'LIRR': '#e40066',
        'Metro-North': '#eac435',
        'Access-A-Ride': '#fb4d3d',
        'Bridges and Tunnels': '#234985',
        'Staten Island Railway': '#02a87d'
    }
    
    # Create lighter and darker versions of each color
    colors = {
        mode: {
            'weekday': f'rgba{tuple(max(0, int(c * 255 - 25)) for c in rgb_to_rgba(color)[:3] + (0.6,))}',  # Más claro
            'weekend': f'rgba{tuple(int(c * 255 + 25) for c in rgb_to_rgba(color)[:3] + (1,))}'      # Más oscuro
        }
        for mode, color in base_colors.items()
    }
    
    for mode in filtered_data['Mode'].unique():
        # Weekday violin
        weekday_data = filtered_data[
            (filtered_data['Mode'] == mode) & 
            (filtered_data['IsWeekend'] == False)
        ]['Recovery_Percentage'] * 100
        
        fig.add_trace(go.Violin(
            x=[mode] * len(weekday_data),
            y=weekday_data,
            legendgroup='Weekday',
            scalegroup=mode,
            name='Weekday',
            side='negative',
            line_color=colors[mode]['weekday'],
            meanline_visible=True,
            showlegend=True if mode == list(filtered_data['Mode'].unique())[0] else False,
            hovertemplate=(
                f"<b>{mode}</b><br>" +
                "Type: Weekday<br>" +
                "Recovery: %{y:.1f}%<br>" +
                f"Mean: {weekday_data.mean():.1f}%<extra></extra>"
            )
        ))
        
        # Weekend violin
        weekend_data = filtered_data[
            (filtered_data['Mode'] == mode) & 
            (filtered_data['IsWeekend'] == True)
        ]['Recovery_Percentage'] * 100
        
        fig.add_trace(go.Violin(
            x=[mode] * len(weekend_data),
            y=weekend_data,
            legendgroup='Weekend',
            scalegroup=mode,
            name='Weekend',
            side='positive',
            line_color=colors[mode]['weekend'],
            meanline_visible=True,
            showlegend=True if mode == list(filtered_data['Mode'].unique())[0] else False,
            hovertemplate=(
                f"<b>{mode}</b><br>" +
                "Type: Weekend<br>" +
                "Recovery: %{y:.1f}%<br>" +
                f"Mean: {weekend_data.mean():.1f}%<extra></extra>"
            )
        ))
    
    # Rest of the layout configuration remains the same
    fig.update_layout(
        xaxis=dict(
            title_text="Transportation Mode",
            title_font=dict(size=14),
        ),
        yaxis=dict(
            title_text="Recovery Rate (%)",
            zeroline=False,
            title_font=dict(size=14)
        ),
    )
    
    return apply_chart_template(fig, title="Weekday vs Weekend Recovery Patterns", height=550)

# Función auxiliar para convertir colores hex a rgba
def rgb_to_rgba(hex_color):
    """Convert hex color to rgba values"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

def generate_monthly_recovery_heatmap(filtered_data):
    """Generate the monthly recovery heatmap with custom colormap"""
    monthly_recovery = filtered_data.groupby(
        ['Mode', 'Year', 'Month']
    )['Recovery_Percentage'].mean().reset_index()
    
    heatmap_data = monthly_recovery.pivot_table(
        values='Recovery_Percentage',
        index='Mode',
        columns=['Year', 'Month'],
        aggfunc='mean'
    )
    
    # Custom colorscale using app's color palette
    colorscale = [
        [0, '#fb4d3d'],      # Rojo para valores bajos (del Access-A-Ride)
        [0.3, '#eac435'],    # Amarillo (del Metro-North)
        [0.6, '#03cea4'],    # Verde azulado (del Buses)
        [0.8, '#345995'],    # Azul (del Subways)
        [1, '#234985']       # Azul oscuro (del Bridges and Tunnels)
    ]
    
    fig = go.Figure(data=[
        go.Heatmap(
            z=heatmap_data.values * 100,
            x=[f"{year}-{month:02d}" for year, month in heatmap_data.columns],
            y=heatmap_data.index,
            colorscale=colorscale,
            zmin=0,
            zmax=100,
            showscale=True,
            colorbar=dict(
                title="Recovery %",
                titleside="right",
                thickness=15,
                outlinewidth=1,
                outlinecolor='rgba(0,0,0,0.1)',
                len=0.9,
                tickfont=dict(size=12),
                titlefont=dict(size=14)
            ),
            hovertemplate="<b>%{y}</b><br>" +
                        "Date: %{x}<br>" +
                        "Recovery: %{z:.1f}%<extra></extra>"
        )
    ])
    
    fig.update_layout(
        xaxis=dict(
            title_text="Month-Year",
            title_font=dict(size=14),
            tickangle=-45,
        ),
        yaxis=dict(
            title_text="Transportation Mode",
            title_font=dict(size=14),
            type='category'
        ),
    )
    
    return apply_chart_template(fig, title="Monthly Recovery Evolution", height=550)

def generate_yearly_comparison_chart(df, selected_mode):
    """Generate a year-over-year comparison chart for a selected mode."""
    # Filter for selected mode
    mode_data = df[df['Mode'] == selected_mode].copy()
    
    # Calculate 7-day moving average for the entire series first
    mode_data['Smooth_Ridership'] = mode_data['Ridership'].rolling(
        window=7, 
        center=True,
        min_periods=1
    ).mean()
    
    # Create a date index with just month and day for all years
    mode_data['month_day'] = pd.to_datetime(
        '2000-' + mode_data['Date'].dt.strftime('%m-%d')
    )
    
    # Create figure
    fig = go.Figure()
    
    # Color scale for years (light to dark blue)
    years = sorted(mode_data['Year'].unique())
    n_years = len(years)
    colors = [f'rgba(52, 89, 149, {0.3 + (i * 0.7/n_years)})' for i in range(n_years)]
    
    # Add a trace for each year
    for year, color in zip(years, colors):
        year_data = mode_data[mode_data['Year'] == year].copy()
        year_data = year_data.sort_values('month_day')
        
        fig.add_trace(
            go.Scatter(
                x=year_data['month_day'],
                y=year_data['Smooth_Ridership'],
                name=str(year),
                line=dict(
                    color=color,
                    width=3,
                    shape='spline',  # Suaviza las líneas
                ),
                hovertemplate=(
                    "<b>%{x|%B %d}</b><br>"
                    "Ridership: %{y:,.0f}<br>"
                    f"Year: {year}"
                    "<extra></extra>"
                )
            )
        )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Daily Ridership (7-day moving average)',
        showlegend=True,
        margin=dict(l=60, r=150, t=100, b=60),
        xaxis=dict(
            tickformat='%B',  # Nombre completo del mes
            dtick='M1',
            range=['2000-01-01', '2000-12-31'],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
            tickfont=dict(size=12),
            title_font=dict(size=14)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
            tickformat=',d',  # Formato con separadores de miles
            tickfont=dict(size=12),
            title_font=dict(size=14)
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Arial'),
        hoverlabel=dict(
            bgcolor='white',
            font_size=14,
            font_family='Arial'
        )
    )
    
    # Definir períodos estacionales
    seasonal_periods = [
        {
            'name': 'New Year',
            'start': '12-24',
            'end': '01-02',
            'color': 'rgba(169, 169, 169, 0.15)',
            'text': 'New Year<br>Holiday Period',
            'y_position': 0.95
        },
        {
            'name': 'Independence Day',
            'start': '07-01',
            'end': '07-07',
            'color': 'rgba(169, 169, 169, 0.15)',
            'text': 'Independence Day<br>Week',
            'y_position': 0.85
        },
        {
            'name': 'Labor Day',
            'start': '09-01',
            'end': '09-07',
            'color': 'rgba(169, 169, 169, 0.15)',
            'text': 'Labor Day<br>Week',
            'y_position': 0.75
        },
        {
            'name': 'Memorial Day',
            'start': '05-25',
            'end': '05-31',
            'color': 'rgba(169, 169, 169, 0.15)',
            'text': 'Memorial Day<br>Week',
            'y_position': 0.65
        },
        {
            'name': 'Thanksgiving',
            'start': '11-22',
            'end': '11-28',
            'color': 'rgba(169, 169, 169, 0.15)',
            'text': 'Thanksgiving<br>Week',
            'y_position': 0.55
        }
    ]
    
    # Agregar zonas sombreadas y anotaciones
    shapes = []
    annotations = []
    
    for period in seasonal_periods:
        # Manejar el caso especial de Año Nuevo que cruza el cambio de año
        if period['name'] == 'New Year':
            # Agregar zona de fin de año
            shapes.append(dict(
                type="rect",
                xref="x",
                yref="paper",
                x0=f"2000-{period['start']}",
                x1=f"2000-12-31",
                y0=0,
                y1=1,
                fillcolor=period['color'],
                layer="below",
                line_width=0,
            ))
            # Agregar zona de inicio de año
            shapes.append(dict(
                type="rect",
                xref="x",
                yref="paper",
                x0=f"2000-01-01",
                x1=f"2000-{period['end']}",
                y0=0,
                y1=1,
                fillcolor=period['color'],
                layer="below",
                line_width=0,
            ))
        else:
            shapes.append(dict(
                type="rect",
                xref="x",
                yref="paper",
                x0=f"2000-{period['start']}",
                x1=f"2000-{period['end']}",
                y0=0,
                y1=1,
                fillcolor=period['color'],
                layer="below",
                line_width=0,
            ))
        
        # Agregar anotación
        annotations.append(dict(
            x=pd.to_datetime(f"2000-{period['start']}"),
            y=period['y_position'],
            xref="x",
            yref="paper",
            text=period['text'],
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor="#636363",
            ax=0,
            ay=-30,
            font=dict(
                size=10,
                color='#636363'
            ),
            align="center",
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="#636363",
            borderwidth=1,
            borderpad=4
        ))
    
    # Actualizar el layout con las formas y anotaciones
    fig.update_layout(
        shapes=shapes + [
            # Borde del gráfico (del código anterior)
            dict(
                type='rect',
                xref='paper',
                yref='paper',
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                line=dict(
                    color='rgba(0,0,0,0.1)',
                    width=1
                ),
                fillcolor='rgba(0,0,0,0)'
            )
        ],
        annotations=annotations
    )
    
    return apply_chart_template(fig, title=f"{selected_mode} Ridership Patterns by Year", height=550)

@lru_cache(maxsize=32)
def calculate_statistics(df_records, mode):
    df = pd.DataFrame.from_records(df_records)
    stats = {
        'total_ridership': df['Ridership'].sum(),
        'daily_avg': df['Ridership'].mean(),
        'peak_day': df.loc[df['Ridership'].idxmax()]['Date'],
        'peak_value': df['Ridership'].max()
    }
    return stats


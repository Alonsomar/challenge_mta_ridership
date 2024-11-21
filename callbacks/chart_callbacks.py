from dash.dependencies import Input, Output

def register_summary_callbacks(app, data):
    @app.callback(
        [Output("total-ridership", "children"), Output("recovery-gauge", "figure")],
        [Input("mode-selector", "value"), Input("date-range", "start_date"), Input("date-range", "end_date")],
    )
    def update_summary(selected_modes, start_date, end_date):
        filtered_data = data[
            (data["Mode"].isin(selected_modes)) &
            (data["Date"] >= start_date) &
            (data["Date"] <= end_date)
        ]
        total_ridership = filtered_data["Ridership"].sum()
        recovery_rate = filtered_data["Recovery_Percentage"].mean()
        # Build recovery gauge figure...
        return f"{total_ridership:,.0f}", recovery_gauge_figure

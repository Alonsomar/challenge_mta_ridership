# Contains functions to load, clean, and preprocess the dataset.



import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MTARidershipData:
    """Class to handle MTA ridership data processing and transformations."""
    
    def __init__(self, filepath):
        """Initialize with filepath to CSV data."""
        self.filepath = filepath
        self.raw_data = None
        self.processed_data = None
        self.timeline_events = None
        
    def load_raw_data(self):
        """Load raw data from CSV file."""
        try:
            self.raw_data = pd.read_csv(self.filepath, parse_dates=['Date'])
            logger.info(f"Successfully loaded data with {len(self.raw_data)} rows")
            return True
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False
    
    def process_data(self):
        """Main data processing pipeline."""
        if self.raw_data is None:
            logger.error("No raw data loaded. Call load_raw_data() first.")
            return False
        
        try:
            df = self.raw_data.copy()
            
            # 1. Reshape data from wide to long format
            id_vars = ['Date']
            value_vars = [
                ('Subways: Total Estimated Ridership', 'Subways: % of Comparable Pre-Pandemic Day'),
                ('Buses: Total Estimated Ridership', 'Buses: % of Comparable Pre-Pandemic Day'),
                ('LIRR: Total Estimated Ridership', 'LIRR: % of Comparable Pre-Pandemic Day'),
                ('Metro-North: Total Estimated Ridership', 'Metro-North: % of Comparable Pre-Pandemic Day'),
                ('Access-A-Ride: Total Scheduled Trips', 'Access-A-Ride: % of Comparable Pre-Pandemic Day'),
                ('Bridges and Tunnels: Total Traffic', 'Bridges and Tunnels: % of Comparable Pre-Pandemic Day'),
                ('Staten Island Railway: Total Estimated Ridership', 'Staten Island Railway: % of Comparable Pre-Pandemic Day')
            ]
            
            # Create empty lists to store transformed data
            transformed_data = []
            
            # Process each pair of columns
            for ridership_col, percentage_col in value_vars:
                mode = ridership_col.split(':')[0].strip()
                mode_data = pd.DataFrame({
                    'Date': df['Date'],
                    'Mode': mode,
                    'Ridership': df[ridership_col],
                    'Recovery_Percentage': df[percentage_col]
                })
                transformed_data.append(mode_data)
            
            # Combine all transformed data
            processed_df = pd.concat(transformed_data, ignore_index=True)
            
            # 2. Add temporal features
            processed_df['Year'] = processed_df['Date'].dt.year
            processed_df['Month'] = processed_df['Date'].dt.month
            processed_df['DayOfWeek'] = processed_df['Date'].dt.dayofweek
            processed_df['IsWeekend'] = processed_df['DayOfWeek'].isin([5, 6])
            
            # 3. Clean and validate data
            # Convert percentages to proper decimals
            processed_df['Recovery_Percentage'] = processed_df['Recovery_Percentage'].astype(float) / 100
            
            # Handle missing values
            processed_df['Ridership'] = processed_df['Ridership'].ffill()
            processed_df['Recovery_Percentage'] = processed_df['Recovery_Percentage'].ffill()
            
            # 4. Add derived metrics
            processed_df['Pre_Pandemic_Baseline'] = (processed_df['Ridership'] / 
                                                   processed_df['Recovery_Percentage'])
            
            # 5. Add rolling averages
            processed_df['Ridership_7day_MA'] = (processed_df.groupby('Mode')['Ridership']
                                               .transform(lambda x: x.rolling(7, min_periods=1).mean()))
            
            # Add timeline events after processing
            self.add_timeline_events()
            
            self.processed_data = processed_df
            logger.info("Data processing completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return False
    
    def get_mode_data(self, mode):
        """Get data for a specific transportation mode."""
        if self.processed_data is None:
            logger.error("No processed data available")
            return None
        
        return self.processed_data[self.processed_data['Mode'] == mode]
    
    def get_date_range_data(self, start_date, end_date):
        """Get data for a specific date range."""
        if self.processed_data is None:
            logger.error("No processed data available")
            return None
        
        mask = (self.processed_data['Date'] >= start_date) & (self.processed_data['Date'] <= end_date)
        return self.processed_data[mask]
    
    def get_summary_stats(self):
        """Generate summary statistics for each mode."""
        if self.processed_data is None:
            logger.error("No processed data available")
            return None
        
        summary = self.processed_data.groupby('Mode').agg({
            'Ridership': ['mean', 'min', 'max'],
            'Recovery_Percentage': ['mean', 'min', 'max'],
            'Pre_Pandemic_Baseline': ['mean']
        }).round(2)
        
        return summary
    
    
    def add_timeline_events(self):
        """Add enhanced timeline events with detailed context and impact analysis"""
        timeline_events = [
            {
                'date': '2020-03-01',
                'event': 'First COVID-19 Case in NYC',
                'category': 'health',
                'impact_level': 'critical',
                'description': 'First confirmed COVID-19 case in New York City',
                'ridership_impact': 'immediate decline',
                'phase': 'initial'
            },
            {
                'date': '2020-03-22',
                'event': 'NY PAUSE Program',
                'category': 'policy',
                'impact_level': 'critical',
                'description': 'Governor Cuomo announces NY PAUSE',
                'ridership_impact': 'severe decline',
                'phase': 'lockdown'
            },
            {
                'date': '2020-06-08',
                'event': 'Phase 1 Reopening',
                'category': 'policy',
                'impact_level': 'major',
                'description': 'NYC begins Phase 1 reopening',
                'ridership_impact': 'gradual increase',
                'phase': 'early_recovery'
            },
            {
                'date': '2020-09-09',
                'event': 'Indoor Dining Resumes',
                'category': 'policy',
                'impact_level': 'moderate',
                'description': 'Indoor dining at 25% capacity',
                'ridership_impact': 'moderate increase',
                'phase': 'adaptation'
            },
            {
                'date': '2020-12-14',
                'event': 'First Vaccine in NYC',
                'category': 'health',
                'impact_level': 'major',
                'description': 'First COVID-19 vaccine administered',
                'ridership_impact': 'positive outlook',
                'phase': 'recovery'
            },
            {
                'date': '2021-05-19',
                'event': 'Major Reopening',
                'category': 'policy',
                'impact_level': 'major',
                'description': 'Most capacity restrictions lifted',
                'ridership_impact': 'significant increase',
                'phase': 'late_recovery'
            },
            {
                'date': '2021-09-13',
                'event': 'Schools Fully Reopen',
                'category': 'policy',
                'impact_level': 'major',
                'description': 'NYC public schools fully reopen',
                'ridership_impact': 'sustained increase',
                'phase': 'new_normal'
            }
        ]
        
        self.timeline_events = pd.DataFrame(timeline_events)
        self.timeline_events['date'] = pd.to_datetime(self.timeline_events['date'])
        return self.timeline_events

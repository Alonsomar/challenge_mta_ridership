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
    
    def detect_anomalies(self, threshold=3):
        """Detect anomalies in ridership data using z-score method."""
        if self.processed_data is None:
            logger.error("No processed data available")
            return None
        
        def mark_anomalies(group):
            z_scores = np.abs(stats.zscore(group['Ridership']))
            return z_scores > threshold
        
        anomalies = self.processed_data.groupby('Mode').apply(mark_anomalies)
        return self.processed_data[anomalies]

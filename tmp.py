from scripts.data_processing import MTARidershipData

# Example usage
mta_data = MTARidershipData('data/MTA_Daily_Ridership.csv')
mta_data.load_raw_data()
mta_data.process_data()

# Get summary statistics
summary = mta_data.get_summary_stats()
print(summary)
# Get specific mode data
subway_data = mta_data.get_mode_data('Subways')
print(subway_data)

# Get date range data
date_range_data = mta_data.get_date_range_data('2020-03-01', '2020-12-31')
print(date_range_data)
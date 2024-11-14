# Contains functions to load, clean, and preprocess the dataset.



import pandas as pd

def load_data(filepath):
    # Load the dataset
    df = pd.read_csv(filepath, parse_dates=['Date'])
    # Perform preprocessing steps
    # E.g., handle missing values, filter data, create additional columns
    return df

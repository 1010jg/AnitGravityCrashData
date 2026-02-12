import pandas as pd
import streamlit as st

def check_completeness(df: pd.DataFrame) -> pd.DataFrame:
    """
    Checks for missing values in the dataframe.
    """
    missing_count = df.isnull().sum()
    missing_percent = (missing_count / len(df)) * 100
    completeness_df = pd.DataFrame({
        'Missing Values': missing_count,
        'Percentage': missing_percent
    })
    return completeness_df[completeness_df['Missing Values'] > 0].sort_values(by='Percentage', ascending=False)

def check_accuracy(df: pd.DataFrame) -> dict:
    """
    Checks for potential data accuracy issues.
    - Coordinate ranges (Latitude: -90 to 90, Longitude: -180 to 180)
    """
    issues = {}
    
    # Check Coordinates
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        invalid_lat = df[~df['Latitude'].between(-90, 90) & df['Latitude'].notnull()]
        invalid_lon = df[~df['Longitude'].between(-180, 180) & df['Longitude'].notnull()]
        
        issues['Invalid Latitude Count'] = len(invalid_lat)
        issues['Invalid Longitude Count'] = len(invalid_lon)

    return issues

def check_consistency(df: pd.DataFrame, key_column: str = 'Report Number') -> int:
    """
    Checks for duplicate records based on a key column.
    """
    if key_column in df.columns:
        return df.duplicated(subset=[key_column]).sum()
    return 0

def check_timeliness(df: pd.DataFrame, date_column: str = 'Crash Date/Time') -> dict:
    """
    Analyzes the date distribution to identify potential timeliness issues.
    """
    timeliness_stats = {}
    if date_column in df.columns:
        # Ensure datetime type
        if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
             df[date_column] = pd.to_datetime(df[date_column], errors='coerce')

        timeliness_stats['Min Date'] = df[date_column].min()
        timeliness_stats['Max Date'] = df[date_column].max()
        
        # Check for future dates (if relevant, though mostly for historical analysis)
        future_dates = df[df[date_column] > pd.Timestamp.now()]
        timeliness_stats['Future Dates Count'] = len(future_dates)
        
    return timeliness_stats

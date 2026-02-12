import streamlit as st
import pandas as pd
import os

@st.cache_data(show_spinner=True)
def load_data(filepath: str) -> pd.DataFrame:
    """
    Loads CSV data from a file path with caching.
    
    Args:
        filepath (str): The absolute path to the CSV file.
        
    Returns:
        pd.DataFrame: The loaded pandas DataFrame, or None if an error occurs.
    """
    if not os.path.exists(filepath):
        st.error(f"File not found: {filepath}")
        return None
        
    try:
        # Load data
        df = pd.read_csv(filepath, low_memory=False)
        
        # Optimize types if necessary (optional, but good for performance)
        # For this specific dataset, we might want to ensure 'Crash Date/Time' is datetime
        if 'Crash Date/Time' in df.columns:
            df['Crash Date/Time'] = pd.to_datetime(df['Crash Date/Time'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

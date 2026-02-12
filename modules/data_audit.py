import pandas as pd
import numpy as np

def check_completeness(df: pd.DataFrame, key_fields: list = None) -> pd.DataFrame:
    """
    Checks for missing values. Flags key fields if > 1% missing.
    """
    if key_fields is None:
        key_fields = ['Report Number', 'Crash Date/Time', 'Latitude', 'Longitude']

    missing_count = df.isnull().sum()
    missing_percent = (missing_count / len(df)) * 100
    
    completeness_df = pd.DataFrame({
        'Column': missing_count.index,
        'Missing Values': missing_count.values,
        'Percentage': missing_percent.values,
        'Type': df.dtypes.values.astype(str)
    })
    
    # Status Logic
    def get_status(row):
        if row['Column'] in key_fields and row['Percentage'] > 1.0:
            return 'Critical'
        elif row['Percentage'] > 20.0:
            return 'Warning'
        elif row['Percentage'] > 0:
            return 'Valid' # or Info implies minor missing
        return 'Valid'

    completeness_df['Status'] = completeness_df.apply(get_status, axis=1)
    completeness_df['Unique Values'] = df.nunique().values
    
    return completeness_df.sort_values(by='Percentage', ascending=False)

def check_consistency(df: pd.DataFrame, key_column: str = 'Report Number') -> dict:
    """
    Checks for duplicates based on Primary Key.
    """
    stats = {'Duplicate Count': 0, 'Duplicate Rate': 0.0}
    if key_column in df.columns:
        dup_count = df.duplicated(subset=[key_column]).sum()
        stats['Duplicate Count'] = dup_count
        stats['Duplicate Rate'] = (dup_count / len(df)) * 100 if len(df) > 0 else 0
    return stats

def check_accuracy(df: pd.DataFrame) -> dict:
    """
    Checks for logical errors.
    - Negative Age
    - Invalid Coordinates
    """
    issues = {}
    
    # Coordinate Logic
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        invalid_lat = len(df[~df['Latitude'].between(-90, 90) & df['Latitude'].notnull()])
        invalid_lon = len(df[~df['Longitude'].between(-180, 180) & df['Longitude'].notnull()])
        issues['Invalid Coordinates'] = invalid_lat + invalid_lon

    # Age Logic (if exists) - Example logic as 'Person Age' isn't standard in all crash sets, 
    # but requested in requirements. Adapting to likely column presence or skip.
    # We will assume a generic check or skip if column not found for now to avoid crashes.
    # For this specific dataset "1_crash_reports.csv", common cols are looked for.
    # If standard columns like 'Driver Age' exist, we check. 
    # Let's check for generic "Age" columns if they exist.
    age_cols = [c for c in df.columns if 'Age' in c]
    for col in age_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            neg_age = len(df[df[col] < 0])
            if neg_age > 0:
                issues[f'Negative {col}'] = neg_age

    return issues

def check_timeliness(df: pd.DataFrame, date_column: str = 'Crash Date/Time') -> dict:
    """
    Checks for future dates and finds latest date.
    """
    stats = {'Future Dates': 0, 'Latest Date': None}
    if date_column in df.columns:
        # We assume data_loader has already converted to datetime, but strictly checking here
        # or assuming it runs after type conversion. 
        # Ideally, we work on a copy or ensure types.
        try:
            # check if dt
            series = df[date_column]
            if not pd.api.types.is_datetime64_any_dtype(series):
                 series = pd.to_datetime(series, errors='coerce')
            
            stats['Latest Date'] = series.max()
            stats['Future Dates'] = len(series[series > pd.Timestamp.now()])
        except Exception:
            pass # Fail gracefully if date conversion issues
            
    return stats

def calculate_health_score(completeness_df, consistency_stats, accuracy_stats, timeliness_stats):
    """
    Calculates a 0-100 Health Score.
    """
    score = 100
    
    # Penalty 1: Critical Missing Fields
    critical_missing = len(completeness_df[completeness_df['Status'] == 'Critical'])
    score -= (critical_missing * 10) 
    
    # Penalty 2: Duplicates
    if consistency_stats['Duplicate Rate'] > 0:
        score -= 10
        if consistency_stats['Duplicate Rate'] > 5:
            score -= 10 # Extra penalty for high dupes
            
    # Penalty 3: Accuracy Issues
    total_accuracy_issues = sum(accuracy_stats.values())
    if total_accuracy_issues > 0:
        score -= 5
        if total_accuracy_issues > 100:
            score -= 10
            
    # Penalty 4: Future Dates
    if timeliness_stats['Future Dates'] > 0:
        score -= 5

    return max(0, score)

def generate_textual_summary(completeness_df, consistency_stats, accuracy_stats, timeliness_stats) -> str:
    """
    Generates a textual summary of findings.
    """
    summary_lines = []
    
    # Consistency
    dupes = consistency_stats['Duplicate Count']
    if dupes > 0:
        summary_lines.append(f"Found {dupes} duplicate IDs (Duplicate Rate: {consistency_stats['Duplicate Rate']:.2f}%).")
    
    # Completeness
    critical = completeness_df[completeness_df['Status'] == 'Critical']
    if not critical.empty:
        cols = ", ".join(critical['Column'].tolist())
        summary_lines.append(f"Critical missing values (>1%) found in key fields: {cols}.")
        
    # Accuracy
    acc_issues = sum(accuracy_stats.values())
    if acc_issues > 0:
         details = ", ".join([f"{k}: {v}" for k,v in accuracy_stats.items() if v > 0])
         summary_lines.append(f"Identified {acc_issues} logical errors ({details}).")
         
    # Timeliness
    future = timeliness_stats['Future Dates']
    if future > 0:
        summary_lines.append(f"Detected {future} records with future dates.")
        
    if not summary_lines:
        return "Data looks clean! No major issues detected."
        
    return " ".join(summary_lines)

def run_audit(df: pd.DataFrame):
    """
    Main orchestration function for Data Audit.
    Returns: score, completeness_df, consistency_stats, accuracy_stats, timeliness_stats, summary_text
    """
    # 1. Run Checks
    comp_df = check_completeness(df)
    const_stats = check_consistency(df)
    acc_stats = check_accuracy(df)
    time_stats = check_timeliness(df)
    
    # 2. Calculate Score
    score = calculate_health_score(comp_df, const_stats, acc_stats, time_stats)
    
    # 3. Generate Summary
    text_summary = generate_textual_summary(comp_df, const_stats, acc_stats, time_stats)
    
    return {
        'score': score,
        'completeness': comp_df,
        'consistency': const_stats,
        'accuracy': acc_stats,
        'timeliness': time_stats,
        'summary_text': text_summary
    }

import pandas as pd

def get_top_performer(df: pd.DataFrame, cat_col='Agency Name') -> dict:
    """
    Identifies the top performing category (by frequency).
    Default category is 'Agency Name' as per typical crash data analysis.
    """
    if cat_col not in df.columns:
        return {}
        
    top_cat = df[cat_col].mode()[0]
    count = df[df[cat_col] == top_cat].shape[0]
    total = len(df)
    
    return {
        'Category': cat_col,
        'Value': top_cat,
        'Count': count,
        'Percentage': round((count / total) * 100, 1)
    }

def get_pain_points(df: pd.DataFrame) -> dict:
    """
    Identifies the main pain point (highest missingness).
    """
    missing = df.isnull().sum()
    if missing.sum() == 0:
        return {}
        
    worst_col = missing.idxmax()
    count = missing.max()
    
    return {
        'Type': 'Missing Values',
        'Column': worst_col,
        'Count': count,
        'Percentage': round((count / len(df)) * 100, 1)
    }

def generate_smart_text(top_perf: dict, pain_point: dict) -> str:
    """
    Generates the strict markdown format for insights.
    """
    # 1. Formatting Top Performer Insight
    insight_1 = ""
    if top_perf:
        insight_1 = f"""
### 💡 Key Insight: Top Performer
* **What (เกิดอะไรขึ้น):** {top_perf['Category']} '{top_perf['Value']}' is the most frequent, appearing {top_perf['Count']} times.
* **Why (ทำไมถึงเป็นแบบนั้น):** Represents {top_perf['Percentage']}% of the total dataset, potentially indicating a high-activity zone or reporting bias.
* **So What (สำคัญอย่างไร):** This {top_perf['Category']} drives the majority of reports, making it a critical area for resource allocation.
* **Now What (ทำอะไรต่อ):** Focus deep-dive analysis on this specific {top_perf['Category']} to understand underlying drivers.
"""

    # 2. Formatting Pain Point Insight
    insight_2 = ""
    if pain_point:
        insight_2 = f"""
### ⚠️ Key Insight: Data Quality Pain Point
* **What (เกิดอะไรขึ้น):** Column '{pain_point['Column']}' has significant missing data ({pain_point['Count']} rows).
* **Why (ทำไมถึงเป็นแบบนั้น):** Missing {pain_point['Percentage']}% of values, likely due to optional field status or data collection gaps.
* **So What (สำคัญอย่างไร):** This reduces the reliability of analysis involving '{pain_point['Column']}'.
* **Now What (ทำอะไรต่อ):** Use the **Data Cleaning** module to impute missing values (Mean/Median/Mode) or filter out incomplete records.
"""

    return insight_1 + "\n---\n" + insight_2

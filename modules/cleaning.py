import pandas as pd
import streamlit as st

def init_cleaning_log():
    """
    Initializes the cleaning log in session state if it doesn't exist.
    """
    if 'cleaning_log' not in st.session_state:
        st.session_state['cleaning_log'] = []

def log_step(action: str):
    """
    Appends a cleaning action to the log.
    """
    init_cleaning_log()
    st.session_state['cleaning_log'].append(action)

def display_cleaning_log():
    """
    Displays the cleaning log in the sidebar.
    """
    init_cleaning_log()
    st.sidebar.markdown("### 🛠️ Transformation Steps")
    
    if not st.session_state['cleaning_log']:
        st.sidebar.info("No changes applied yet.")
    else:
        for i, step in enumerate(st.session_state['cleaning_log'], 1):
            st.sidebar.text(f"{i}. {step}")
            
def impute_missing_values(df: pd.DataFrame, column: str, method: str) -> pd.DataFrame:
    """
    Imputes missing values in the specified column using the selected method.
    Methods: Mean, Median, Mode, Drop, Zero, Unknown
    """
    df = df.copy()
    missing_count = df[column].isnull().sum()
    
    if missing_count == 0:
        return df, f"No missing values in {column} to fill."
    
    log_msg = ""
    
    if method == "Mean":
        if pd.api.types.is_numeric_dtype(df[column]):
            val = df[column].mean()
            df[column] = df[column].fillna(val)
            log_msg = f"Filled missing {column} with Mean: {val:.2f}"
        else:
            return df, f"Cannot calculate Mean for non-numeric column {column}."
            
    elif method == "Median":
        if pd.api.types.is_numeric_dtype(df[column]):
            val = df[column].median()
            df[column] = df[column].fillna(val)
            log_msg = f"Filled missing {column} with Median: {val:.2f}"
        else:
             return df, f"Cannot calculate Median for non-numeric column {column}."

    elif method == "Mode":
        if not df[column].mode().empty:
            val = df[column].mode()[0]
            df[column] = df[column].fillna(val)
            log_msg = f"Filled missing {column} with Mode: {val}"
        else:
             return df, f"Could not determine Mode for {column}."

    elif method == "Drop Rows":
        df = df.dropna(subset=[column])
        log_msg = f"Dropped {missing_count} rows with missing {column}"

    elif method == "Fill Zero":
        df[column] = df[column].fillna(0)
        log_msg = f"Filled missing {column} with 0"

    elif method == "Fill 'Unknown'":
        df[column] = df[column].fillna("Unknown")
        log_msg = f"Filled missing {column} with 'Unknown'"
        
    else:
        return df, "Invalid imputation method selected."
        
    return df, log_msg

def fix_date_formats(df: pd.DataFrame, columns: list = None) -> pd.DataFrame:
    """
    Attempts to convert specified columns (or auto-detected date strings) to datetime.
    """
    df = df.copy()
    log_msgs = []
    
    if columns is None:
        # Auto-detect logic could go here, but for now let's look for 'Date' in name
        columns = [c for c in df.columns if 'Date' in c or 'Time' in c]
        
    count = 0
    for col in columns:
        if col in df.columns:
            # Check if likely object/string that needs conversion
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    count += 1
                    log_msgs.append(f"Converted {col} to Datetime")
                except Exception:
                    pass
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                 # Already datetime, maybe just note it or skip
                 pass

    if count > 0:
        return df, f"Fixed Date Formats: {', '.join(log_msgs)}"
    else:
        return df, "No date columns required fixing."


def render_cleaning_ui(df: pd.DataFrame):
    """
    Renders the interactive data cleaning UI.
    Returns the modified dataframe.
    """
    st.subheader("🧹 Interactive Data Cleaning")
    
    # 1. Pipeline Log
    display_cleaning_log()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info("Select a column to clean:")
        # Filter for cols with missing values for better UX, or all cols
        all_cols = df.columns.tolist()
        miss_cols = [c for c in all_cols if df[c].isnull().sum() > 0]
        
        target_col = st.selectbox("Target Column", options=miss_cols + ["(Select)"], index=len(miss_cols))
        
        method = st.radio("Imputation Method", ["Mean", "Median", "Mode", "Drop Rows", "Fill Zero", "Fill 'Unknown'"])
        
        clean_btn = st.button("Apply Transformation", type="primary")
        
        st.markdown("---")
        if st.button("Fix Date Formats (Auto)"):
             new_df, msg = fix_date_formats(df)
             st.success(msg)
             log_step(msg)
             return new_df

    with col2:
        if target_col != "(Select)":
            # Show Distribution / Stats Before
            st.markdown(f"#### Analyzing: **{target_col}**")
            
            # Before Stats
            missing_before = df[target_col].isnull().sum()
            st.metric("Missing Values (Before)", f"{missing_before} ({missing_before/len(df):.1%})")
            
            if clean_btn:
                new_df, log_msg = impute_missing_values(df, target_col, method)
                
                if "Cannot" in log_msg or "Invalid" in log_msg:
                    st.error(log_msg)
                else:
                    st.success("Success!")
                    log_step(log_msg)
                    
                    # After Stats
                    missing_after = new_df[target_col].isnull().sum()
                    st.metric("Missing Values (After)", f"{missing_after} ({missing_after/len(new_df):.1%})", delta=missing_before-missing_after)
                    
                    return new_df
                    
    return df

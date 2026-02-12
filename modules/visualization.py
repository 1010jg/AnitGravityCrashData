import streamlit as st
import pandas as pd
import plotly.express as px

def apply_global_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renders sidebar filters and returns the filtered dataframe.
    """
    st.sidebar.markdown("### 📊 Global Filters")
    
    # Year Filter
    if 'Crash Date/Time' in df.columns:
        # Check if dt
        if not pd.api.types.is_datetime64_any_dtype(df['Crash Date/Time']):
             # Try temporary conversion for min/max
             temp_dates = pd.to_datetime(df['Crash Date/Time'], errors='coerce')
             min_date = temp_dates.min()
             max_date = temp_dates.max()
        else:
             min_date = df['Crash Date/Time'].min()
             max_date = df['Crash Date/Time'].max()
             
        if pd.notnull(min_date) and pd.notnull(max_date):
            # Convert to date object for slider
            min_d = min_date.date()
            max_d = max_date.date()
            
            if min_d < max_d:
                date_range = st.sidebar.slider(
                    "Date Range",
                    min_value=min_d,
                    max_value=max_d,
                    value=(min_d, max_d)
                )
                
                # Filter
                # Ensure df col is datetime for filtering
                # Note: modifying df here (copy) is safer
                df = df.copy() 
                if not pd.api.types.is_datetime64_any_dtype(df['Crash Date/Time']):
                     df['Crash Date/Time'] = pd.to_datetime(df['Crash Date/Time'], errors='coerce')
                
                df = df[
                    (df['Crash Date/Time'].dt.date >= date_range[0]) & 
                    (df['Crash Date/Time'].dt.date <= date_range[1])
                ]

    # Region/Agency Filter (Example)
    if 'Agency Name' in df.columns:
        agencies = sorted(df['Agency Name'].dropna().unique().tolist())
        selected_agencies = st.sidebar.multiselect("Filter by Agency", options=agencies)
        
        if selected_agencies:
            df = df[df['Agency Name'].isin(selected_agencies)]
            
    return df

def get_plot_data(df: pd.DataFrame, max_rows=10000):
    """
    Samples data if > max_rows to prevent lag.
    Returns (df_sampled, title_suffix)
    """
    if len(df) > max_rows:
        return df.sample(n=max_rows, random_state=42), "(Sampled Data)"
    return df, ""

def plot_trend(df: pd.DataFrame, date_col='Crash Date/Time', rolling_mean=False):
    """
    Plots a line chart of crashes over time.
    """
    if date_col not in df.columns:
        st.warning(f"Trend Analysis: {date_col} missing.")
        return

    # Prepare Data
    df_plot = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df_plot[date_col]):
        df_plot[date_col] = pd.to_datetime(df_plot[date_col], errors='coerce')
        
    daily_counts = df_plot.set_index(date_col).resample('D').size().rename('Crashes').reset_index()
    
    title = "Daily Crash Trend"
    
    fig = px.line(daily_counts, x=date_col, y='Crashes', title=title)
    
    if rolling_mean:
        daily_counts['Rolling Mean (7D)'] = daily_counts['Crashes'].rolling(window=7).mean()
        fig.add_scatter(x=daily_counts[date_col], y=daily_counts['Rolling Mean (7D)'], mode='lines', name='7-Day Rolling Mean', line=dict(dash='dash', color='orange'))

    st.plotly_chart(fig, use_container_width=True)

def plot_distribution(df: pd.DataFrame, num_col: str, show_outliers=True):
    """
    Plots distribution (Histogram/Box) for a numerical column.
    """
    if num_col not in df.columns:
        return

    st.markdown(f"#### Distribution of {num_col}")
    
    # Check numeric
    if not pd.api.types.is_numeric_dtype(df[num_col]):
         st.warning(f"{num_col} is not numeric.")
         return

    plot_df, suffix = get_plot_data(df, max_rows=50000) # Higher limit for hist
    
    tab1, tab2 = st.tabs(["Histogram", "Box Plot"])
    
    with tab1:
        fig_hist = px.histogram(plot_df, x=num_col, title=f"Histogram {suffix}", marginal="box")
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with tab2:
        points = "all" if show_outliers else False
        fig_box = px.box(plot_df, y=num_col, title=f"Box Plot {suffix}", points=points)
        st.plotly_chart(fig_box, use_container_width=True)

def plot_comparison(df: pd.DataFrame, cat_col: str, top_n=10):
    """
    Plots a bar chart for categorical comparison.
    """
    if cat_col not in df.columns:
        return

    st.markdown(f"#### Comparison by {cat_col}")
    
    # Aggregation (No sampling needed for counts usually, but plotting might need it if too many cats)
    counts = df[cat_col].value_counts().nlargest(top_n).reset_index()
    counts.columns = [cat_col, 'Count']
    
    fig = px.bar(counts, x=cat_col, y='Count', title=f"Top {top_n} {cat_col}s", color='Count')
    st.plotly_chart(fig, use_container_width=True)

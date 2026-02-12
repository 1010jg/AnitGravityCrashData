import streamlit as st
import pandas as pd
import plotly.express as px
from modules import data_loader, data_audit, history, ui, app_style, cleaning, visualization, insights

# 1. Page Config
st.set_page_config(
    page_title="Crash Data Audit Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Apply Style
st.markdown(app_style.get_app_style(), unsafe_allow_html=True)

# 3. Initialize History
history_log = history.HistoryLog()

# 4. Load Data & State Management
@st.cache_resource
def get_data_initial():
    file_path = "1_crash_reports.csv" 
    return data_loader.load_data(file_path)

if 'df' not in st.session_state:
    raw_df = get_data_initial()
    if raw_df is not None:
        st.session_state['df'] = raw_df.copy()
    else:
        st.session_state['df'] = None

df = st.session_state['df']

# 5. Sidebar Navigation
with st.sidebar:
    st.title("🚗 Crash Analyzer")
    st.markdown("---")
    page = st.radio("Navigation", ["Dashboard", "Data Audit", "Data Cleaning", "Visualizations", "History Log"])
    st.markdown("---")
    st.info("National Vocational Competition\nData Engineering Track")

# 6. Main Content
if page == "Dashboard":
    st.title("📊 Crash Data Dashboard")
    
    if df is not None:
        # Traceability
        if "Dashboard Viewed" not in [x['action'] for x in history_log.get_logs() if x['action'] == "Dashboard Viewed"]:
             history_log.add_entry("Dashboard Viewed", f"Loaded {len(df)} rows")

        # --- INSIGHTS SECTION ---
        st.markdown("### 💡 Automated Insights")
        top_perf = insights.get_top_performer(df)
        pain_point = insights.get_pain_points(df)
        insight_text = insights.generate_smart_text(top_perf, pain_point)
        st.markdown(insight_text)
        st.markdown("---")

        # Top Stats
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Crashes", f"{len(df):,}")
        
        if 'Agency Name' in df.columns:
            top_agency = df['Agency Name'].mode()[0]
            col2.metric("Top Agency", top_agency)
        
        if 'ACRS Report Type' in df.columns:
            injury_crashes = df[df['ACRS Report Type'] == 'Injury Crash']
            col3.metric("Injury Crashes", f"{len(injury_crashes):,}")

        if 'Crash Date/Time' in df.columns:
             # Ensure dt
             if pd.api.types.is_datetime64_any_dtype(df['Crash Date/Time']):
                 latest_date = df['Crash Date/Time'].max().strftime('%Y-%m-%d')
             else:
                 latest_date = "N/A"
             col4.metric("Latest Report", latest_date)

        st.markdown("### 🗺️ Geographic Distribution")
        # Empty State Check for Map
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            valid_coords = df.dropna(subset=['Latitude', 'Longitude'])
            # Filter valid ranges
            valid_coords = valid_coords[
                (valid_coords['Latitude'].between(-90, 90)) & 
                (valid_coords['Longitude'].between(-180, 180))
            ]
            
            if len(valid_coords) > 0:
                # Sample for performance if too large
                map_data = valid_coords.sample(min(1000, len(valid_coords)))
                st.map(map_data)
            else:
                ui.render_empty_state("No valid coordinates found for the map.")
        else:
             ui.render_empty_state("Latitude/Longitude columns missing.")

    else:
        ui.render_empty_state("Could not ensure data is loaded.")

elif page == "Data Audit":
    st.title("🛡️ Data Quality Audit")
    
    if df is not None:
        if st.button("Run Audit", type="primary"):
            history_log.add_entry("Audit Performed", "Ran DQ checks")
            
            results = data_audit.run_audit(df)
            
            # Scoreboard
            score = results['score']
            color = "green" if score > 80 else "orange" if score > 50 else "red"
            st.markdown(f"""
            <div style="background-color:#1E1E1E; padding:20px; border-radius:10px; text-align:center; border: 2px solid {color}">
                <h2 style="color:white; margin:0;">Data Health Score</h2>
                <h1 style="color:{color}; font-size: 60px; margin:0;">{score}/100</h1>
            </div>
            """, unsafe_allow_html=True)
            
            st.info(results['summary_text'])
            
            tab1, tab2, tab3, tab4 = st.tabs(["Completeness", "Accuracy", "Consistency", "Timeliness"])
            
            with tab1:
                st.subheader("Missing Values Analysis")
                completeness = results['completeness']
                if not completeness.empty:
                    st.dataframe(completeness, use_container_width=True)
                    fig = px.bar(completeness, x='Column', y='Percentage', title="Missing Values % by Column", color='Status')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    ui.render_audit_card("Perfect Completeness", "No missing values found!", "success")

            with tab2:
                st.subheader("Data Accuracy Checks")
                accuracy_issues = results['accuracy']
                total_acc = sum(accuracy_issues.values())
                
                if total_acc == 0:
                     ui.render_audit_card("High Accuracy", "No logic errors detected.", "success")
                else:
                     col1, col2 = st.columns(2)
                     for k, v in accuracy_issues.items():
                         status = "error" if v > 0 else "success"
                         ui.render_audit_card(k, f"{v} issues found", status)

            with tab3:
                st.subheader("Consistency Checks")
                consistency = results['consistency']
                dupes = consistency['Duplicate Count']
                if dupes > 0:
                    ui.render_audit_card("Duplicate Records", f"{dupes} duplicates found (Rate: {consistency['Duplicate Rate']:.2f}%).", "error")
                else:
                    ui.render_audit_card("Data Consistency", "No Duplicates found.", "success")

            with tab4:
                 st.subheader("Timeliness & Recency")
                 timeliness = results['timeliness']
                 
                 col1, col2 = st.columns(2)
                 col1.metric("Latest Date", str(timeliness.get('Latest Date', 'N/A')))
                 
                 future_count = timeliness.get('Future Dates', 0)
                 if future_count > 0:
                     ui.render_audit_card("Future Dates Detected", f"{future_count} records have dates in the future.", "error")
                 else:
                     ui.render_audit_card("Logical Consistency", "No future dates detected.", "success")
    else:
        ui.render_empty_state("No data available for audit.")

elif page == "Data Cleaning":
    # cleaning.render_cleaning_ui handles the UI and modifying st.session_state['df'] if we passed it correctly
    # But clean_ui returns a NEW df. We must capture it.
    if df is not None:
        st.session_state['df'] = cleaning.render_cleaning_ui(df) 
        # Note: render_cleaning_ui returns the modified df (or original if no change)
    else:
        ui.render_empty_state("No data to clean.")

elif page == "Visualizations":
    st.title("📈 Advanced Visualizations")
    
    if df is not None:
        # Global Filters
        df_vis = visualization.apply_global_filters(df)
        
        tab1, tab2, tab3 = st.tabs(["Trend Analysis", "Distributions", "Comparisons"])
        
        with tab1:
            st.subheader("Time Series Analysis")
            date_col = st.selectbox("Select Date Column", [c for c in df_vis.columns if 'Date' in c or 'Time' in c], index=0 if 'Crash Date/Time' in df_vis.columns else 0)
            rolling = st.checkbox("Show 7-Day Rolling Mean")
            visualization.plot_trend(df_vis, date_col, rolling)
            
        with tab2:
            st.subheader("Numerical Distributions")
            num_cols = df_vis.select_dtypes(include=['number']).columns.tolist()
            if num_cols:
                num_col = st.selectbox("Select Numerical Column", num_cols)
                show_outliers = st.toggle("Show Outliers", value=True)
                visualization.plot_distribution(df_vis, num_col, show_outliers)
            else:
                st.info("No numerical columns found.")
                
        with tab3:
            st.subheader("Categorical Comparisons")
            cat_cols = df_vis.select_dtypes(include=['object']).columns.tolist()
            if cat_cols:
                cat_col = st.selectbox("Select Categorical Column", cat_cols, index=cat_cols.index('Agency Name') if 'Agency Name' in cat_cols else 0)
                visualization.plot_comparison(df_vis, cat_col)
            else:
                st.info("No categorical columns found.")

    else:
        ui.render_empty_state("No data to visualize.")

elif page == "History Log":
    st.title("📜 Traceability Log")
    
    logs = history_log.get_logs()
    
    if len(logs) > 0:
        if st.button("Clear Logs"):
            history_log.clear_logs()
            st.rerun()
            
        for entry in logs[::-1]: # Show new first
            st.markdown(f"**{entry['timestamp']}** - `{entry['action']}`")
            st.info(entry['details'])
    else:
        ui.render_empty_state("No actions recorded yet.")

import streamlit as st
import pandas as pd
import plotly.express as px

from modules import data_loader, data_audit, history, ui, app_style

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

# 4. Load Data
@st.cache_resource
def get_data():
    # In a real scenario, this path might be dynamic or env var
    # For this competition task, we hardcode the provided filename
    file_path = "1_crash_reports.csv" 
    return data_loader.load_data(file_path)

df = get_data()

# 5. Sidebar Navigation
with st.sidebar:
    st.title("🚗 Crash Analyzer")
    st.markdown("---")
    page = st.radio("Navigation", ["Dashboard", "Data Audit", "History Log"])
    st.markdown("---")
    st.info("National Vocational Competition\nData Engineering Track")

# 6. Main Content
if page == "Dashboard":
    st.title("📊 Crash Data Dashboard")
    
    if df is not None:
        # Traceability
        if "Dashboard Viewed" not in [x['action'] for x in history_log.get_logs() if x['action'] == "Dashboard Viewed"]:
             history_log.add_entry("Dashboard Viewed", f"Loaded {len(df)} rows")

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
             latest_date = df['Crash Date/Time'].max().strftime('%Y-%m-%d')
             col4.metric("Latest Report", latest_date)

        st.markdown("### 🗺️ Geographic Distribution")
        # Empty State Check for Map
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            valid_coords = df.dropna(subset=['Latitude', 'Longitude'])
            if len(valid_coords) > 0:
                # Sample for performance if too large
                map_data = valid_coords.sample(min(1000, len(valid_coords)))
                st.map(map_data)
            else:
                ui.render_empty_state("No valid coordinates found for the map.")
        else:
             ui.render_empty_state("Latitude/Longitude columns missing.")

        st.markdown("### 📅 Trends Over Time")
        if 'Crash Date/Time' in df.columns:
             daily_crashes = df.set_index('Crash Date/Time').resample('D').size().rename('Crashes')
             st.line_chart(daily_crashes)
        else:
             ui.render_empty_state("Crash Date/Time column missing.")

    else:
        ui.render_empty_state("Could not ensure data is loaded.")

elif page == "Data Audit":
    st.title("🛡️ Data Quality Audit")
    
    if df is not None:
        history_log.add_entry("Audit Performed", "Ran DQ checks")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Completeness", "Accuracy", "Consistency", "Timeliness"])
        
        with tab1:
            st.subheader("Missing Values Analysis")
            completeness = data_audit.check_completeness(df)
            if not completeness.empty:
                st.dataframe(completeness, use_container_width=True)
                
                # Visual
                fig = px.bar(completeness, x=completeness.index, y='Percentage', title="Missing Values % by Column")
                st.plotly_chart(fig, use_container_width=True)
            else:
                ui.render_audit_card("Perfect Completeness", "No missing values found in the dataset!", "success")

        with tab2:
            st.subheader("Data Accuracy Checks")
            accuracy_issues = data_audit.check_accuracy(df)
            
            if not accuracy_issues and len(accuracy_issues) == 0:
                 ui.render_audit_card("High Accuracy", "No basic accuracy issues detected.", "success")
            else:
                 col1, col2 = st.columns(2)
                 for k, v in accuracy_issues.items():
                     if v > 0:
                         ui.render_audit_card(k, f"{v} issues found", "warning")
                     else:
                         ui.render_audit_card(k, "Pass", "success")

        with tab3:
            st.subheader("Consistency Checks")
            duplicates = data_audit.check_consistency(df)
            if duplicates > 0:
                ui.render_audit_card("Duplicate Records", f"{duplicates} duplicates found based on Report Number.", "error")
                if st.button("Log Duplicate Removal Attempt"):
                     history_log.add_entry("Consistency Check", "Flagged duplicates")
            else:
                ui.render_audit_card("Data Consistency", "No Duplicate Report Numbers found.", "success")

        with tab4:
             st.subheader("Timeliness & Recency")
             timeliness = data_audit.check_timeliness(df)
             
             col1, col2, col3 = st.columns(3)
             col1.metric("Earliest Date", str(timeliness.get('Min Date', 'N/A')))
             col2.metric("Latest Date", str(timeliness.get('Max Date', 'N/A')))
             
             future_count = timeliness.get('Future Dates Count', 0)
             if future_count > 0:
                 ui.render_audit_card("Future Dates Detected", f"{future_count} records have dates in the future.", "error")
             else:
                 ui.render_audit_card("Logical Consistency", "No future dates detected.", "success")
    else:
        ui.render_empty_state("No data available for audit.")

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

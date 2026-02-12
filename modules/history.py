from datetime import datetime
import streamlit as st

class HistoryLog:
    """
    A simple class to log actions for traceability.
    """
    def __init__(self):
        if 'history_log' not in st.session_state:
            st.session_state.history_log = []

    def add_entry(self, action: str, details: str):
        """
        Adds a new entry to the log.
        """
        entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'action': action,
            'details': details
        }
        st.session_state.history_log.append(entry)

    def get_logs(self):
        """
        Returns the log entries.
        """
        return st.session_state.history_log

    def clear_logs(self):
        """
        Clears the log.
        """
        st.session_state.history_log = []

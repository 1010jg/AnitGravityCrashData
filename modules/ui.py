import streamlit as st

def render_empty_state(message: str = "No data available. Please check your data source."):
    """
    Renders a styled empty state message.
    """
    st.markdown(f"""
        <div style="
            text-align: center;
            padding: 50px;
            background-color: #f8f9fa;
            border-radius: 10px;
            color: #6c757d;
            margin-top: 20px;
            border: 1px dashed #dee2e6;
        ">
            <h3>📭 {message}</h3>
            <p>Ensure the data file is present and correctly formatted.</p>
        </div>
    """, unsafe_allow_html=True)

def render_audit_metric(label: str, value, delta: str = None, help_text: str = None):
    """
    Renders a metric card.
    """
    st.metric(label=label, value=value, delta=delta, help=help_text)

def render_audit_card(title: str, content: str, status: str = "info"):
    """
    Renders a card for audit details.
    """
    colors = {
        "success": "#d4edda",
        "warning": "#fff3cd",
        "error": "#f8d7da",
        "info": "#d1ecf1"
    }
    color = colors.get(status, "#d1ecf1")
    
    st.markdown(f"""
        <div style="
            padding: 15px;
            background-color: {color};
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 5px solid {color.replace('d', 'a')}; 
        ">
            <h5 style="margin-top: 0;">{title}</h5>
            <p style="margin-bottom: 0;">{content}</p>
        </div>
    """, unsafe_allow_html=True)

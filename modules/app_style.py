def get_app_style():
    """
    Returns custom CSS for the application.
    """
    return """
    <style>
        /* Main Container */
        .main {
            background-color: #0e1117; 
            font-family: 'Inter', sans-serif;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #ffffff;
            font-weight: 700;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #262730;
            border-right: 1px solid #4a4a4a;
        }
        
        /* Cards & Metrics */
        .stMetric {
            background-color: #1f2937;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            border: 1px solid #374151;
        }
        
        /* Checkbox/Radio Buttons */
        .stCheckbox > label, .stRadio > label {
            color: #e5e7eb;
        }
        
        /* Dataframes */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
        }

        /* Custom "Empty State" override for dark mode */
        div[style*="background-color: #f8f9fa"] {
            background-color: #1f2937 !important;
            color: #9ca3af !important;
            border: 1px dashed #4b5563 !important;
        }
        
        /* Scrollbars */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        ::-webkit-scrollbar-track {
            background: #0e1117; 
        }
        ::-webkit-scrollbar-thumb {
            background: #4b5563; 
            border-radius: 5px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #6b7280; 
        }
    </style>
    """

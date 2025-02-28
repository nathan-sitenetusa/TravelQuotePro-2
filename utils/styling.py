import streamlit as st

def set_page_style():
    """Set custom page styling"""
    st.set_page_config(
        page_title="Travel Quote Calculator",
        page_icon="✈️",
        layout="wide"
    )
    
    st.markdown("""
        <style>
        .main {
            padding: 1rem 3rem;
        }
        .stButton>button {
            width: 100%;
        }
        .streamlit-expanderHeader {
            font-size: 1.1em;
            font-weight: 600;
        }
        .css-1d391kg {
            padding: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

def show_header():
    """Display page header"""
    st.title("✈️ Travel Quote Calculator")
    st.markdown("""
        Calculate group travel costs with different occupancy scenarios and pricing tiers.
        Input your costs below and get detailed price breakdowns.
    """)

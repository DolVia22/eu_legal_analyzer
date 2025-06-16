#!/usr/bin/env python3
"""
Quick test for homepage loading
"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="EU Legal Analyzer",
    page_icon="🇪🇺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import homepage
from ui.homepage import show_homepage

def main():
    """Simple homepage test"""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    # Sidebar
    with st.sidebar:
        st.title("EU Legal Analyzer")
        
        # Dark mode toggle
        dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.rerun()
    
    # Show homepage
    show_homepage()

if __name__ == "__main__":
    main()
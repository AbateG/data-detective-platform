#!/usr/bin/env python3
"""
Data Detective Platform Launcher
This script properly sets up the Python path and launches the Streamlit app.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables for Streamlit
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_SERVER_PORT'] = '8501'
os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'

# Import streamlit and run the app
import streamlit as st
from app.dashboard import main

if __name__ == "__main__":
    main()

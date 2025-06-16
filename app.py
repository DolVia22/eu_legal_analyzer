#!/usr/bin/env python3
"""
EU Legal Analyzer - Main Application Entry Point

This application analyzes company profiles against EU legal acts using AI/ML models
to determine compliance requirements and relevance.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

def main():
    """Main application entry point"""
    try:
        # Import and run the Streamlit app
        from ui.main_app import main as run_app
        run_app()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
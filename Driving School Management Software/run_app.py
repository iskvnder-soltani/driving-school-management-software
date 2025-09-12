#!/usr/bin/env python3
"""
Entry point for the Iskander Driving School Management System
Run this file to start the application with the separated code structure.
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
from main.main_app import init_db, IskanderDrivingSchool

if __name__ == '__main__':
    print("Starting Iskander Driving School Management System...")
    print("Separated code structure version")
    print("=" * 50)
    
    # Initialize database
    init_db()
    
    # Create and run the application
    app = IskanderDrivingSchool()
    app.mainloop()

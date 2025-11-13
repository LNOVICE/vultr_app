#!/usr/bin/env python3
"""
Vultr CLI Android App - Main Entry Point
This file serves as the entry point for Buildozer Android builds
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from vultr_cli.ui.app import VultrCliApp

if __name__ == "__main__":
    VultrCliApp().run()
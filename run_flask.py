#!/usr/bin/env python3
"""
Helper to run the Flask app for Live Share / Codespace guests.

Open this file in the browser-based Live Share session and press
the editor's "Run" button (or run `python run_flask.py`).
This will execute `src/gui/web/main.py` in-process so the Flask
app starts with the same behavior as running that script directly.
"""
import os
import sys 
import runpy

ROOT = os.path.abspath(os.path.dirname(__file__))
TARGET = os.path.join(ROOT, "src", "gui", "web", "main.py")

if not os.path.exists(TARGET):
    print(f"Error: target file not found: {TARGET}")
    sys.exit(1)

os.chdir(ROOT)

print("Starting MiniMony web app (src/gui/web/main.py)...\nPress Ctrl+C to stop.")

# Execute the target script as if run directly
runpy.run_path(TARGET, run_name="__main__")

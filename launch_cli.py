import subprocess
import os
import sys

# Determine the base directory
if hasattr(sys, "_MEIPASS"):
    # We're in a PyInstaller bundle
    base_dir = sys._MEIPASS
else:
    # We're running as a .py file
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Path to actual Streamlit app script
app_path = os.path.join(base_dir, "app_launcher.py")

# Run streamlit with the full path to the app script
subprocess.run(["streamlit", "run", app_path, " --server.maxUploadSize=1024"], check=True)


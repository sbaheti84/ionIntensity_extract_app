import subprocess
import os
import sys

def log(msg):
    print(f"[INFO] {msg}")

def get_app_path():
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "app_launcher.py")

if __name__ == "__main__":
    app_path = get_app_path()
    log(f"Using app path: {app_path}")

    # Ensure we're calling streamlit from the embedded site-packages
    try:
        result = subprocess.run(
            ["streamlit", "run", app_path, "--server.maxUploadSize=1024"],
            check=True
        )
    except FileNotFoundError:
        log("❌ Streamlit not found. Make sure it was bundled properly.")
    except subprocess.CalledProcessError as e:
        log(f"❌ Streamlit crashed with error code: {e.returncode}")
    except Exception as ex:
        log(f"❌ Unexpected error: {ex}")

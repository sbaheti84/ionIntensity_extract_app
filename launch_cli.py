import subprocess
import os
import sys

def main():
    # Determine base path
    if hasattr(sys, "_MEIPASS"):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # Point to app_launcher.py bundled with the app
    app_path = os.path.join(base_dir, "app_launcher.py")
    print(f"[INFO] Using app path: {app_path}")

    try:
        # Run Streamlit safely using the system Python (not the bundled EXE)
        subprocess.run([
            "streamlit", "run", app_path,
            "--server.maxUploadSize=1024"
        ], check=True)
    except FileNotFoundError as fnf:
        print("[ERROR] 'streamlit' not found. Ensure it's installed.")
        print(fnf)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Streamlit app failed: {e}")
    except Exception as ex:
        print(f"[ERROR] Unexpected exception: {ex}")

if __name__ == "__main__":
    main()

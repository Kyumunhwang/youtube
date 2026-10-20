import os
import sys
import streamlit.web.cli as stcli

if __name__ == "__main__":
    # Ensure base directory is configured properly
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
    os.chdir(base_dir)

    sys.argv = [
        "streamlit",
        "run",
        os.path.join(base_dir, "app.py"),
        "--global.developmentMode=false",
        "--server.port=8501",
        "--server.headless=false",
        "--browser.gatherUsageStats=false"
    ]
    
    sys.exit(stcli.main())

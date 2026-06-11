import streamlit.web.cli as stcli
import os
import sys

if __name__ == "__main__":
    # Ensure working directory is set to the application directory (sys._MEIPASS)
    if getattr(sys, 'frozen', False):
        os.chdir(sys._MEIPASS)
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
    sys.argv = [
        "streamlit",
        "run",
        "app.py",
        "--global.developmentMode=false",
        "--server.port=8501",
        "--browser.gatherUsageStats=false"
    ]
    
    sys.exit(stcli.main())

@echo off
echo Starting Personal Money Dashboard...
echo.
echo Make sure you have installed the requirements:
echo pip install -r requirements.txt
echo.
echo The dashboard will open in your default browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the application.
echo.
streamlit run app.py
pause

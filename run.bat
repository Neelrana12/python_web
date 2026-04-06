@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ============================================================
echo MedInsight Analytics - Starting Server
echo ============================================================
echo.
echo Application will be available at: http://localhost:5000
echo.
echo Default Credentials:
echo   Username: admin
echo   Password: password123
echo.
echo   Username: user
echo   Password: user123
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python app.py

pause

@echo off
REM Installation script for Legal Case Similarity Web Application
REM Supports: Windows 10/11

echo ==========================================
echo Legal Case Similarity - Installation
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Checking Python version...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Extract major and minor version
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

REM Check if version is 3.8 or higher
if %PYTHON_MAJOR% LSS 3 (
    echo Error: Python 3.8 or higher is required
    pause
    exit /b 1
)
if %PYTHON_MAJOR% EQU 3 if %PYTHON_MINOR% LSS 8 (
    echo Error: Python 3.8 or higher is required
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    echo.
    echo If you encounter SSL errors, try:
    echo pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
    pause
    exit /b 1
)

echo.
echo Downloading NLTK data...
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
if %errorlevel% neq 0 (
    echo Warning: Failed to download NLTK data
    echo You may need to download it manually later
)

echo.
echo Creating necessary directories...
if not exist "data\cases" mkdir data\cases
if not exist "data\vectors" mkdir data\vectors
if not exist "logs" mkdir logs
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "templates" mkdir templates

echo.
echo Verifying installation...
python verify_setup.py
if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo Installation completed successfully!
    echo ==========================================
    echo.
    echo To start the application:
    echo   1. Activate virtual environment: venv\Scripts\activate.bat
    echo   2. Run development server: python run_api.py
    echo   3. Run production server: python uvicorn_production.py
    echo.
    echo The application will be available at: http://localhost:8000
    echo.
    echo For more information, see:
    echo   - README.md for general documentation
    echo   - DEPLOYMENT.md for deployment instructions
    echo   - PRODUCTION_CHECKLIST.md for production deployment
    echo.
) else (
    echo.
    echo ==========================================
    echo Installation completed with warnings
    echo ==========================================
    echo.
    echo Please review the verification output above.
    echo Some components may need manual configuration.
    echo.
)

pause

@echo off
REM Quick Start Script for AI Knowledge Base + Chatbot (Windows)

echo ==========================================
echo AI Knowledge Base + Chatbot - Quick Start
echo ==========================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo + Python found
python --version

REM Check if virtual environment exists
if not exist "venv\" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    echo + Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo + Virtual environment activated

REM Install dependencies
echo.
echo Installing dependencies...
pip install -q -r requirements.txt
echo + Dependencies installed

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo . .env file not found. Creating from template...
    copy .env.example .env
    echo + .env file created
    echo.
    echo . IMPORTANT: Please edit .env and add your OpenAI API key:
    echo    OPENAI_API_KEY=sk-your-api-key-here
    echo.
    pause
    notepad .env
)

REM Create necessary directories
echo.
echo Creating necessary directories...
if not exist "data\chroma\" mkdir data\chroma
if not exist "uploads\" mkdir uploads
if not exist "static\" mkdir static
if not exist "templates\" mkdir templates
echo + Directories created

REM Start the application
echo.
echo ==========================================
echo Starting the application...
echo ==========================================
echo.
echo The application will be available at:
echo   http://localhost:8000
echo.
echo API documentation will be available at:
echo   http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

@ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION

ECHO.
ECHO.

where.exe python > NUL

IF ERRORLEVEL 1 (
   ECHO Python is not installed
   EXIT 1
)

cd /D "%~dp0"

rem ECHO %*
SET _all=%*
rem CALL SET args=%%_all:*%2=%%
SET args=%2%args%


IF NOT EXIST venv (
    ECHO Creating virtual environment
    python -m venv venv
)

CALL venv/Scripts/activate.bat

ECHO Installing dependencies
CALL pip install -r requirements.txt --upgrade
ECHO Install complete
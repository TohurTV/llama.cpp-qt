@echo off
setlocal enabledelayedexpansion

:: Check if the venv folder exists
if not exist .\venv (
    echo Virtual environment not found. Creating venv...
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment found.
)

:: Activate the virtual environment
call .\venv\Scripts\activate

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt
echo Requirements installed.

:: Run llama.cpp-qt.py
python llama.cpp-qt.py

:: Deactivate the virtual environment
deactivate

:: Pause to keep the command window open
pause

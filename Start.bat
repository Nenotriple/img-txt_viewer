@echo off
setlocal enabledelayedexpansion


REM Set up a Python virtual environment and run a specified Python script.


REM Variables
set "PYTHON_SCRIPT=app.py"
set "VENV_DIR=venv"
set "SCRIPT_DIR=%~dp0"
set "FAST_START=FALSE"
set "AUTO_FAST_START=TRUE"


REM Navigate to the script directory
cd /d "%SCRIPT_DIR%" || (
    echo Failed to set current directory.
    pause
    exit /b 1
)
echo Set current directory... OK


REM Check if settings.cfg exists and AUTO_FAST_START is enabled
if "%AUTO_FAST_START%"=="TRUE" (
    if exist "settings.cfg" (
        set "FAST_START=TRUE"
        echo settings.cfg found. Enabling FAST_START mode.
    )
)


REM Skip setup if FAST_START is TRUE and venv exists
if "%FAST_START%"=="TRUE" (
    if exist "%VENV_DIR%\Scripts\activate.bat" (
        call "%VENV_DIR%\Scripts\activate.bat" || (
            echo Activating the virtual environment... FAIL
            pause
            exit /b 1
        )
        echo Virtual environment activated.
        echo Launching: %PYTHON_SCRIPT%
        echo.
        python "%PYTHON_SCRIPT%" || (
            echo Launching... FAIL
        )
        call cmd /k
        exit /b 0
    ) else (
        echo Fast start enabled but virtual environment not found.
        set "FAST_START=FALSE"
    )
)


REM Check if Python is installed
python --version >nul 2>&1 || (
    echo Python is not installed or not found in PATH.
    pause
    exit /b 1
)


REM Check if the virtual environment already exists
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Creating a Python virtual environment: "%SCRIPT_DIR%\%VENV_DIR%"
    python -m venv "%VENV_DIR%" || (
        echo An error occurred while creating the virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created.
) else (
    echo Virtual environment already exists: "%SCRIPT_DIR%\%VENV_DIR%"
)


REM Activate the virtual environment
call "%VENV_DIR%\Scripts\activate.bat" || (
    echo Activating the virtual environment... FAIL
    pause
    exit /b 1
)
echo Virtual environment activated.


REM Upgrade pip
python -m pip install --upgrade pip


REM Install requirements if requirements.txt exists
if exist "requirements.txt" (
    echo Installing requirements...
    pip install -r requirements.txt || (
        echo Failed to install requirements.
        pause
        exit /b 1
    )
)


REM Launch the user-defined Python script
if "%PYTHON_SCRIPT%"=="" (
    echo Auto-Launch: Skipping
) else (
    echo Launching: %PYTHON_SCRIPT%
    echo.
    python "%PYTHON_SCRIPT%" || (
        echo Launching... FAIL
        pause
        exit /b 1
    )
)


echo.
call cmd /k


endlocal

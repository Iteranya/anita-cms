@echo off
setlocal enabledelayedexpansion
echo Starting Anita-CMS setup and launch...
echo.

REM Set project directory
set "PROJECT_DIR=%USERPROFILE%\Documents\anita-cms"
cd /d "%PROJECT_DIR%" || (
    echo Failed to change directory to %PROJECT_DIR%.
    pause
    exit /b 1
)

REM Check for main.py
if not exist "main.py" (
    echo Error: main.py not found in %PROJECT_DIR%.
    echo Please run the anita_installer.bat script first.
    pause
    exit /b 1
)

REM Look for Python 3.10 explicitly
set "PYTHON_EXE="
for /f "delims=" %%p in ('where python') do (
    for /f "tokens=2" %%v in ('"%%p --version 2>&1"') do (
        echo Checking Python version: %%v
        echo %%v | findstr "3.10" >nul
        if !errorlevel! == 0 (
            set "PYTHON_EXE=%%p"
            goto found_python
        )
    )
)

echo Error: Python 3.10 not found.
pause
exit /b 1

:found_python
echo Found Python 3.10 at: %PYTHON_EXE%
echo.

REM Set up virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    "%PYTHON_EXE%" -m venv venv || (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

REM Activate venv
call venv\Scripts\activate.bat || (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)
echo Virtual environment activated.

REM Install uv if not present
pip show uv >nul 2>&1
if errorlevel 1 (
    echo Installing UV...
    pip install uv || (
        echo UV installation failed.
        pause
        exit /b 1
    )
)

REM Install requirements
if exist "requirements.txt" (
    echo Installing dependencies from requirements.txt...
    uv pip install -r requirements.txt || (
        echo Failed to install dependencies.
        pause
        exit /b 1
    )
) else (
    echo Warning: requirements.txt not found.
)
REM Check and create .env with JWT_SECRET if needed
set "NEED_JWT_SECRET=1"
if exist ".env" (
    findstr /I /C:"JWT_SECRET=" ".env" >nul
    if !errorlevel! == 0 (
        set "NEED_JWT_SECRET=0"
        echo .env already contains JWT_SECRET
    )
)

if !NEED_JWT_SECRET! == 1 (
    echo Generating JWT_SECRET in .env file...
    
    REM Generate a random string for JWT_SECRET using Python
    (
        echo import secrets
        echo print^("JWT_SECRET=" ^+ secrets.token_urlsafe^(32^)^)
    ) > gen_jwt.py
    
    "%PYTHON_EXE%" gen_jwt.py > temp_jwt.txt
    set /p JWT_SECRET=<temp_jwt.txt
    
    REM Clean up temporary files
    del gen_jwt.py
    del temp_jwt.txt
    
    if exist ".env" (
        REM Append to existing .env file
        echo !JWT_SECRET!>>.env
    ) else (
        REM Create new .env file
        echo !JWT_SECRET!>.env
    )
    echo Added JWT_SECRET to .env file
)

REM Run application
echo Starting Anita-CMS...
python main.py

echo.
echo ---------------------------------------------
echo Anita-CMS has exited. Deactivating venv.
echo ---------------------------------------------
call venv\Scripts\deactivate.bat
echo Done.
pause
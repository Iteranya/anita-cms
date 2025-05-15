@echo off
echo Starting setup for Anita-CMS...
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrator privileges.
    echo Please right-click the file and select "Run as administrator".
    pause
    exit /b 1
)

REM Check if Python 3.10 is installed
python --version 2>nul | findstr "3.10" >nul
if %errorlevel% neq 0 (
    echo Python 3.10 is not installed. Installing Python 3.10...
    echo.

    REM Download Python 3.10 installer
    echo Downloading Python 3.10 installer...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe' -OutFile '%TEMP%\python310_installer.exe'"

    REM Install Python 3.10
    echo Installing Python 3.10...
    %TEMP%\python310_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

    echo Python 3.10 installation completed.
    echo.
) else (
    echo Python 3.10 is already installed.
    echo.
)

REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git is not installed. Installing Git...
    echo.

    REM Download Git installer
    echo Downloading Git installer...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.41.0.windows.1/Git-2.41.0-64-bit.exe' -OutFile '%TEMP%\git_installer.exe'"

    REM Install Git
    echo Installing Git...
    %TEMP%\git_installer.exe /VERYSILENT /NORESTART

    echo Git installation completed.
    echo.
) else (
    echo Git is already installed.
    echo.
)

REM Set install directory
set "INSTALL_DIR=%USERPROFILE%\Documents\anita-cms"

REM Clone the repository
echo Cloning the Anita-CMS repository to: %INSTALL_DIR%
echo.

if exist "%INSTALL_DIR%" (
    echo The anita-cms directory already exists at %INSTALL_DIR%.
    echo.

    set /p answer="Do you want to update the existing repository? (Y/N): "
    if /i "%answer%"=="Y" (
        cd /d "%INSTALL_DIR%"
        git pull
        echo Repository updated successfully.
    ) else (
        echo Repository update skipped.
    )
) else (
    mkdir "%INSTALL_DIR%"
    git clone https://github.com/Iteranya/anita-cms "%INSTALL_DIR%"
    echo Repository cloned successfully to %INSTALL_DIR%.
)

REM Create desktop shortcut for start.bat
echo Creating desktop shortcut for Anita-CMS...

set "TARGET_PATH=%INSTALL_DIR%\start.bat"
set "SHORTCUT_PATH=%USERPROFILE%\Desktop\Anita-CMS.lnk"
set "ICON_PATH=%INSTALL_DIR%\anita.ico"

if exist "%TARGET_PATH%" (
    echo Found start.bat at: %TARGET_PATH%
    
    REM Use PowerShell to create the shortcut with a custom icon
    powershell -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%SHORTCUT_PATH%'); $sc.TargetPath = '%TARGET_PATH%'; $sc.WorkingDirectory = '%INSTALL_DIR%'; $sc.IconLocation = '%ICON_PATH%'; $sc.Save()"

    if exist "%SHORTCUT_PATH%" (
        echo Desktop shortcut created successfully at: %SHORTCUT_PATH%
    ) else (
        echo Failed to create shortcut. Check permissions.
    )
) else (
    echo Error: start.bat not found in anita-cms directory.
    echo Checked path: %TARGET_PATH%
)

pause

@echo off
setlocal EnableDelayedExpansion

:: Enable UTF-8
chcp 65001 >nul
title Wallpaper Engine Downloader - Auto Setup
color 0F
cls

echo.
echo ========================================================
echo   WALLPAPER ENGINE DOWNLOADER - AUTO SETUP
echo ========================================================
echo.

:: ----------------------------------------------------------
:: STEP 1 : PYTHON CHECK
:: ----------------------------------------------------------
echo [1/4] Checking Python...

where python >nul 2>&1
if !errorlevel! NEQ 0 (
    echo    [*] Python is not installed.
    echo    [*] Downloading installer...
    curl -L -o python_installer.exe https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe
    
    echo    [*] Installing Python...
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    del python_installer.exe
    echo    [OK] Python installed.
    echo.
    echo    IMPORTANT: Please close this window and restart the file.
    pause
    exit /b
)
echo    [OK] Python is already installed.
echo.

:: ----------------------------------------------------------
:: STEP 2 : LIBRARIES CHECK
:: ----------------------------------------------------------
echo [2/4] Checking libraries...

python -c "import selenium, winotify, requests" >nul 2>&1
if !errorlevel! NEQ 0 (
    echo    [*] Installing missing libraries...
    pip install selenium winotify requests -q >nul 2>&1
)
echo    [OK] Libraries ready.
echo.

:: ----------------------------------------------------------
:: STEP 3 : TOOLS CHECK
:: ----------------------------------------------------------
echo [3/4] Checking external tools...

:: Check if we need 7-Zip
set "NEED_7Z=0"
if not exist "chromium\chrome.exe" set "NEED_7Z=1"
if not exist "DepotDownloaderMod\DepotDownloadermod.exe" set "NEED_7Z=1"

if "!NEED_7Z!"=="1" (
    if not exist "7z.exe" (
        echo    [*] Downloading 7-Zip...
        curl -L -s -o 7zr.exe https://www.7-zip.org/a/7zr.exe
        curl -L -s -o 7z_inst.exe https://www.7-zip.org/a/7z2408-x64.exe
        7zr.exe e 7z_inst.exe 7z.exe 7z.dll -y >nul 2>&1
        del 7zr.exe 7z_inst.exe 2>nul
        echo    [OK] 7-Zip ready.
    )
)

:: --- CHROMIUM ---
if exist "chromium\chrome.exe" (
    echo    [OK] Chromium found.
) else (
    echo    [*] Downloading Chromium...
    curl -L -s -o chromium.7z "https://tinyurl.com/crmdwnld"
    
    :: Verify download size
    for %%A in (chromium.7z) do set "SIZE=%%~zA"
    if !SIZE! LSS 1000000 (
        echo    [ERROR] Chromium download failed. Size: !SIZE! bytes
        del chromium.7z 2>nul
        pause
        exit /b
    )
    
    echo    [*] Extracting Chromium - Please wait...
    if exist "chromium" rmdir /s /q "chromium" 2>nul
    if exist "chromium_temp" rmdir /s /q "chromium_temp" 2>nul
    
    7z.exe x chromium.7z -ochromium_temp -y >nul 2>&1
    
    :: Find ungoogled-chromium-* folder and copy contents
    mkdir chromium 2>nul
    for /d %%D in (chromium_temp\ungoogled-chromium-*) do (
        xcopy /E /Y /Q "%%D\*" "chromium\" >nul
        goto :ChromiumDone
    )
    
    :ChromiumDone
    rmdir /s /q chromium_temp 2>nul
    del chromium.7z 2>nul
    
    if exist "chromium\chrome.exe" (
        echo    [OK] Chromium installed.
    ) else (
        echo    [ERROR] chrome.exe not found after extraction.
        pause
        exit /b
    )
)

:: --- DEPOTDOWNLOADER ---
if exist "DepotDownloaderMod\DepotDownloadermod.exe" (
    echo    [OK] DepotDownloader found.
) else (
    echo    [*] Downloading DepotDownloader...
    curl -L -s -o depot.rar "https://github.com/SteamAutoCracks/DepotDownloaderMod/releases/download/DepotDownloaderMod_3.4.0.2/Release.rar"
    
    :: Verify download size
    for %%A in (depot.rar) do set "SIZE=%%~zA"
    if !SIZE! LSS 100000 (
        echo    [ERROR] DepotDownloader download failed. Size: !SIZE! bytes
        del depot.rar 2>nul
        pause
        exit /b
    )
    
    echo    [*] Extracting DepotDownloader...
    if exist "DepotDownloaderMod" rmdir /s /q "DepotDownloaderMod" 2>nul
    if exist "depot_temp" rmdir /s /q "depot_temp" 2>nul
    
    7z.exe x depot.rar -odepot_temp -y >nul 2>&1
    
    mkdir DepotDownloaderMod 2>nul
    xcopy /E /Y /Q "depot_temp\Release\net9.0\*" "DepotDownloaderMod\" >nul
    
    rmdir /s /q depot_temp 2>nul
    del depot.rar 2>nul
    
    if exist "DepotDownloaderMod\DepotDownloadermod.exe" (
        echo    [OK] DepotDownloader installed.
    ) else (
        echo    [ERROR] DepotDownloadermod.exe not found.
        pause
        exit /b
    )
)

:: Cleanup 7z
if exist "7z.exe" del 7z.exe 2>nul
if exist "7z.dll" del 7z.dll 2>nul
echo.

:: ----------------------------------------------------------
:: STEP 4 : LAUNCH
:: ----------------------------------------------------------
echo ========================================================
echo   STARTING PYTHON SCRIPT...
echo ========================================================
echo.

python main.py

pause
exit /b
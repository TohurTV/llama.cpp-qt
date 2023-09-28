@echo off
setlocal enabledelayedexpansion

:: Set the GitHub repository and release tag
set REPO=ggerganov/llama.cpp
set TAG=b1280

:: Create a temporary directory
set TEMP_DIR=%TEMP%\llama_cpp_temp
mkdir "%TEMP_DIR%"

:: Direct download link to the zip file
set "download_url=https://github.com/%REPO%/releases/download/%TAG%/llama-%TAG%-bin-win-openblas-x64.zip"

:: Create a temporary PowerShell script
echo Invoke-WebRequest -Uri "!download_url!" -OutFile llama-%TAG%-bin-win-openblas-x64.zip > download.ps1

:: Download the zip file using PowerShell
powershell.exe -ExecutionPolicy Bypass -File download.ps1

:: Check if the downloaded file is valid
if not exist llama-%TAG%-bin-win-openblas-x64.zip (
  echo Error: Failed to download the zip file.
  exit /b 1
)

:: Extract the downloaded release zip file using Windows built-in zip utility
echo Extracting files...
powershell -command "Expand-Archive -Path 'llama-%TAG%-bin-win-openblas-x64.zip' -DestinationPath '%TEMP_DIR%'"

:: Copy DLL files and server.exe to the current directory
echo Copying files to the current directory...
copy "%TEMP_DIR%\*.dll" .
copy "%TEMP_DIR%\OpenBLAS-0.3.23.txt" .
copy "%TEMP_DIR%\server.exe" .

:: Cleanup: Remove the temporary directory and downloaded zip file
echo Cleaning up...
rd /s /q "%TEMP_DIR%"
del llama-%TAG%-bin-win-openblas-x64.zip

:: Done
echo Latest release downloaded and extracted successfully.

:: Pause to keep the command window open
pause

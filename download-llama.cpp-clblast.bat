@echo off
setlocal enabledelayedexpansion

:: Set the GitHub repository and release tag
set REPO=ggerganov/llama.cpp
set TAG=b1280

:: Create a temporary directory
set TEMP_DIR=%TEMP%\llama_cpp_temp
mkdir "%TEMP_DIR%"

:: Download the latest release assets
echo Downloading latest release...
curl -LJO https://github.com/%REPO%/releases/%TAG%/download/llama-b1280-bin-win-clblast-x64.zip

:: Extract the downloaded release zip file using Windows built-in zip utility
echo Extracting files...
Call :UnZipFile %TEMP_DIR% llama-b1280-bin-win-clblast-x64.zip

:: Copy DLL files and server.exe to the current directory
echo Copying files to the current directory...
copy "%TEMP_DIR%\*.dll" .
copy "%TEMP_DIR%\CLBlast-1.6.0.txt" .
copy "%TEMP_DIR%\server.exe" .

:: Cleanup: Remove the temporary directory and downloaded zip file
echo Cleaning up...
rd /s /q "%TEMP_DIR%"
del llama-b1280-bin-win-clblast-x64.zip

:: Done
echo Latest release downloaded and extracted successfully.

:: Pause to keep the command window open
pause

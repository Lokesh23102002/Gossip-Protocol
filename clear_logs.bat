@echo off
set folderPath=logs

REM Check if the folder exists
if exist "%folderPath%" (
    rd /s /q "%folderPath%"
    echo Folder deleted successfully.
) else (
    echo Folder does not exist.
)

pause

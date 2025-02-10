@echo off
cd /d "%~dp0"

REM Activate Conda environment
call "%USERPROFILE%\anaconda3\Scripts\activate.bat" myapp_env

REM Run the application
python simple-app\app.py
exit

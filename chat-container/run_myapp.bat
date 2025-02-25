@echo off
cd /d "%~dp0"
call "%USERPROFILE%\anaconda3\Scripts\activate.bat" depressionappenv
python simple-app\src\realtime.py
exit

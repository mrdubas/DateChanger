@echo off
chcp 65001 > nul
title build DateChanger
python.exe --version >nul 2>&1
if errorlevel 1 goto python_errors
python.exe -m pip install --upgrade pip
pip install PyQt5 win32_setctime
pip install pyinstaller
pyinstaller --onefile --windowed DateChanger.pyw
if errorlevel 1 goto errors
echo build compleate
pause
exit
:errors
echo Error something went wrong!
pause
exit
:python_errors
echo Error python not found!
pause
exit
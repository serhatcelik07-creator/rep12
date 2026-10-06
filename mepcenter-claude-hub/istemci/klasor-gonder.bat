@echo off
REM Bir klasoru (or. G: surucusu) MepCenter huba gonderir. Cift tiklayin.
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul && (py "%USERPROFILE%\.mepcenter\hub_senkron.py") || (python "%USERPROFILE%\.mepcenter\hub_senkron.py")
pause

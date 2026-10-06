@echo off
REM Windows: bu dosyaya cift tiklayin
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul && (py kur.py) || (where python >nul 2>nul && (python kur.py) || (echo Python bulunamadi. https://www.python.org/downloads/ adresinden kurun, kurulumda "Add python.exe to PATH" kutusunu isaretleyin. & start https://www.python.org/downloads/))
pause

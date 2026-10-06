@echo off
rem Cift tiklayinca calisir. Ilk seferde gerekli paketleri kendisi kurar.
cd /d "%~dp0"
where py >nul 2>&1 && (set PY=py) || (set PY=python)
%PY% -c "import pynput, cryptography" >nul 2>&1
if errorlevel 1 (
    echo Ilk kurulum yapiliyor ^(bir kere^), biraz surebilir...
    %PY% -m pip install -q -r requirements-windows.txt
    if errorlevel 1 (
        echo Kurulum basarisiz. Python kurulu mu? https://www.python.org/downloads/
        pause
        exit /b 1
    )
)
%PY% windows_taraf.py %*
pause

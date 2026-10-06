@echo off
rem Cift tiklayinca calisir. Ilk seferde gerekli paketleri kendisi kurar.
cd /d "%~dp0"
rem Python'u bul: once py baslaticisi, sonra PATH, sonra standart kurulum klasorleri.
rem (PATH'te yoksa "python" Microsoft Store kisayoluna gider ve "Python bulunamadi" der.)
set PY=
py -c "import sys" >nul 2>&1 && set PY=py
if not defined PY python -c "import sys" >nul 2>&1 && set PY=python
if not defined PY for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*" "%ProgramFiles%\Python3*" "C:\Python3*") do if exist "%%~D\python.exe" set PY="%%~D\python.exe"
if not defined PY (
    echo Python bulunamadi.
    echo Acilan sayfadan Python'u indir. Kurarken en alttaki
    echo "Add python.exe to PATH" kutusunu isaretle, sonra bu dosyaya tekrar cift tikla.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)
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

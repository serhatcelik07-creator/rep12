@echo off
rem Cift tiklayinca calisir. Ilk seferde gerekli paketleri kendisi kurar.
cd /d "%~dp0"
where py >nul 2>&1 && (set PY=py) || (set PY=python)
rem Python yoksa Windows'un Microsoft Store kisayolu calisir ve hata verir.
%PY% -c "import sys" >nul 2>&1
if errorlevel 1 (
    echo Python kurulu degil.
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

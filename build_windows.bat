@echo off
REM Baut eine portable EXE (kein Installer nötig).
REM Auf einem Windows-PC mit Python ausführen.

cd /d "%~dp0"

echo.
echo === iPhone Foto-Konverter: EXE bauen ===
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python wurde nicht gefunden.
    echo Bitte Python von https://www.python.org/downloads/ installieren
    echo und dabei "Add python.exe to PATH" anhaken.
    pause
    exit /b 1
)

echo [1/3] Abhaengigkeiten installieren...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo FEHLER beim Installieren der Pakete.
    pause
    exit /b 1
)

echo.
echo [2/3] Portable EXE erzeugen...
python -m PyInstaller --noconfirm --clean ^
    --onefile ^
    --windowed ^
    --name "iPhone-Foto-Konverter" ^
    --hidden-import pillow_heif ^
    --collect-all pillow_heif ^
    heic_converter_app.py
if errorlevel 1 (
    echo FEHLER beim Bauen der EXE.
    pause
    exit /b 1
)

echo.
echo [3/3] Fertig.
echo.
echo Die Datei liegt hier:
echo   dist\iPhone-Foto-Konverter.exe
echo.
echo Diese eine EXE kannst du z.B. auf den Desktop oder auf einen
echo USB-Stick kopieren. Keine Installation noetig.
echo.
pause

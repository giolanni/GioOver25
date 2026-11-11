@echo off
setlocal
chcp 65001 >nul
set "PROJECT=%~dp0"

if not exist "%PROJECT%\gioover25_gui.py" (
    echo ERRORE: GUI non trovata in:
    echo %PROJECT%
    echo.
    echo Avvia questo file dalla cartella del repository completa.
    pause
    exit /b 1
)

cd /d "%PROJECT%" || (
    echo ERRORE: impossibile aprire la cartella del progetto.
    pause
    exit /b 1
)

where py >nul 2>&1
if not errorlevel 1 (
    py -3 -m gioover25_gui
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo ERRORE: Python non trovato. Installa Python o aggiungilo al PATH.
        pause
        exit /b 1
    )
    python -m gioover25_gui
)

if errorlevel 1 (
    echo.
    echo La GUI si e' chiusa con un errore. Controlla il messaggio qui sopra.
    pause
)
endlocal

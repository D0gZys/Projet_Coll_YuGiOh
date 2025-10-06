@echo off
title Yu-Gi-Oh Collection Manager
echo 🎮 Lancement du Yu-Gi-Oh Collection Manager...
echo.

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    echo ✅ Environnement virtuel détecté
    ".venv\Scripts\python.exe" collection_manager\main_gui.py
) else if exist "venv\Scripts\python.exe" (
    echo ✅ Environnement virtuel détecté (venv)
    "venv\Scripts\python.exe" collection_manager\main_gui.py
) else (
    echo ⚠️  Environnement virtuel non trouvé, utilisation de Python système
    python collection_manager\main_gui.py
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Erreur lors du lancement
    echo 💡 Assurez-vous que Python et les dépendances sont installées
    pause
)
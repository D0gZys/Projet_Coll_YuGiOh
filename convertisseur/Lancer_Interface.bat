@echo off
title Convertisseur Yu-Gi-Oh V2 - Interface Graphique
echo 🎮 Lancement du Convertisseur Yu-Gi-Oh V2...
echo.

cd /d "%~dp0"

if exist "..\\.venv\Scripts\python.exe" (
    echo ✅ Environnement virtuel détecté
    "..\\.venv\Scripts\python.exe" Convertisseur_GUI.py
) else if exist "..\\venv\Scripts\python.exe" (
    echo ✅ Environnement virtuel détecté (venv)
    "..\\venv\Scripts\python.exe" Convertisseur_GUI.py
) else (
    echo ⚠️  Environnement virtuel non trouvé, utilisation de Python système
    python Convertisseur_GUI.py
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Erreur lors du lancement
    echo 💡 Assurez-vous que Python et les dépendances sont installées
    pause
)
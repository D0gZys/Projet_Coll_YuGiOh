@echo off
echo 🔄 Sauvegarde du projet sur GitHub...
echo.

echo 📁 Ajout des fichiers modifiés...
"C:\Program Files\Git\bin\git.exe" add .

echo.
echo 📝 Saisir le message de commit:
set /p commit_msg="Message: "

echo.
echo 💾 Création du commit...
"C:\Program Files\Git\bin\git.exe" commit -m "%commit_msg%"

echo.
echo 🚀 Envoi vers GitHub...
"C:\Program Files\Git\bin\git.exe" push

echo.
echo ✅ Sauvegarde terminée !
pause
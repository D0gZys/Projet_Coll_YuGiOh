#!/bin/bash

echo "🔄 Synchronisation du projet Yu-Gi-Oh..."
echo

echo "📥 Récupération des dernières modifications..."
git pull

echo
echo "📁 Ajout des fichiers modifiés..."
git add .

echo
read -p "📝 Message de commit: " commit_msg

echo
echo "💾 Création du commit..."
git commit -m "$commit_msg"

echo
echo "🚀 Envoi vers GitHub..."
git push

echo
echo "✅ Synchronisation terminée !"
echo "Appuyer sur Entrée pour fermer..."
read
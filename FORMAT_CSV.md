# 📊 Format CSV - Documentation

## 🎯 Nouveau format de sauvegarde

Le convertisseur génère maintenant des fichiers **CSV** au lieu de TXT, optimisés pour l'analyse de données et l'import dans Excel/Google Sheets.

## 📋 Structure du fichier CSV

### En-têtes des colonnes :
```
Code_Serie, Nom_Carte, Rareté, Numéro_Carte
```

### Format des données :
- **Code_Serie** : Code du set (BLMM, RA02, CYAC, etc.)
- **Nom_Carte** : Nom français de la carte
- **Rareté** : Une seule rareté par ligne
- **Numéro_Carte** : Numéro complet (BLMM-FR001, RA02-FR001, etc.)

## 🔄 Gestion des raretés multiples

**Problème résolu :** Les cartes avec plusieurs raretés créent maintenant **une ligne par rareté**.

### Exemple avec "Chat Sauveteur" (RA02-FR001) :
```csv
Code_Serie,Nom_Carte,Rareté,Numéro_Carte
RA02,Chat Sauveteur,Super Rare,RA02-FR001
RA02,Chat Sauveteur,Ultra Rare,RA02-FR001
RA02,Chat Sauveteur,Secret Rare,RA02-FR001
RA02,Chat Sauveteur,Platinum Secret Rare,RA02-FR001
RA02,Chat Sauveteur,Quarter Century Secret Rare,RA02-FR001
RA02,Chat Sauveteur,Ultimate Rare,RA02-FR001
RA02,Chat Sauveteur,Collector's Rare,RA02-FR001
```

## 📈 Avantages du format CSV

### 🔍 **Analyse facilitée :**
- Tri par rareté, série, ou nom
- Filtrage par série spécifique
- Comptage automatique des raretés
- Import direct dans Excel/Sheets

### 🎯 **Cas d'usage :**
- **Inventaire de collection** : Cocher les cartes possédées par rareté
- **Analyse de marché** : Grouper par rareté pour les prix
- **Statistiques** : Compter les cartes par série/rareté
- **Base de données** : Import direct dans des logiciels de gestion

## 💾 Utilisation

### Interface graphique :
1. Saisir l'URL Yugipedia
2. Donner un nom (ex: "RA02")
3. Extraction → **nom.csv** créé automatiquement

### Résultat type :
- **5 cartes** avec **7 raretés chacune** = **35 lignes CSV**
- Prêt pour analyse dans n'importe quel tableur !

## 🔧 Codes de série supportés

| Format | Exemple | Description |
|--------|---------|-------------|
| XXXX-FR | BLMM-FR001 | 4 lettres standard |
| XX##-FR | RA02-FR001 | 2 lettres + 2 chiffres |
| XXXX-FR | CYAC-FR001 | Codes mixtes |

Le système détecte automatiquement le bon format selon l'URL utilisée !
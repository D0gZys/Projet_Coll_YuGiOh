# � Yu-Gi-Oh Collection Manager

Un gestionnaire de collection Yu-Gi-Oh moderne avec interface graphique, permettant de gérer et organiser votre collection de cartes.

## ✨ Fonctionnalités

### 🔄 Convertisseur automatique
- **Import depuis Yugipedia** : Extraction automatique des données de cartes
- **Génération CSV** : Création automatique de fichiers CSV dans `convertisseur/temp/`
- **Nettoyage automatique** : Suppression des fichiers temporaires après import
- **Extraction intelligente** : Récupération automatique des noms de séries depuis les URLs

### 💾 Gestionnaire de base de données
- **Import CSV intelligent** : Import automatique avec détection des doublons
- **Sauvegarde des sources** : Conservation des URLs sources pour traçabilité
- **Mise à jour intelligente** : Enrichissement automatique des séries existantes
- **Structure relationnelle** : Base de données SQLite optimisée

### 🎨 Interface graphique moderne
- **Design CustomTkinter** : Interface moderne et intuitive
- **Gestion multi-onglets** : Import, Collection, Configuration
- **Mode sélection avancé** : Sélection multiple avec outils dédiés
- **Actions en lot** : Ajout/suppression en masse
- **Suppression définitive** : Suppression complète avec confirmation
- **Logs en temps réel** : Suivi des opérations

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip (gestionnaire de paquets Python)

### Installation
1. **Cloner le projet**
   ```bash
   git clone https://github.com/[votre-username]/Projet_Coll_YuGiOh.git
   cd Projet_Coll_YuGiOh
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv .venv
   ```

3. **Activer l'environnement virtuel**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

4. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Utilisation

### Lancement de l'application
```bash
python collection_manager/main_gui.py
```

### Convertisseur (Extraction de cartes)
```bash
# Double-cliquez sur :
Lancer_Convertisseur.bat
```

## 📋 **Fonctionnalités**

### 🔧 **Convertisseur** (`convertisseur/`)
- ✅ Extraction automatique depuis Yugipedia
- ✅ Support multi-formats : LOB, MRD, RA02, etc.
- ✅ Export CSV avec une ligne par rareté
- ✅ Interface graphique intuitive

### 💾 **Base de Données** (`database/`)
- ✅ SQLite intégré (aucun serveur requis)
- ✅ Schema normalisé (séries, cartes, raretés)
- ✅ Import CSV automatique
- ✅ Statistiques de collection

### 🖥️ **Interface de Gestion** (`collection_manager/`)
- ✅ Vue d'ensemble avec statistiques
- ✅ Import/Export de données
- ✅ Gestion de possession (Possédé/Non possédé)
- ✅ Interface à onglets moderne

## �️ **Structure du Projet**

```
Projet_Coll_YuGiOh/
├── 🚀 Lancer_Collection_Manager.bat    # Lanceur principal
├── 🚀 Lancer_Convertisseur.bat         # Lanceur convertisseur
├── 
├── convertisseur/                       # Module d'extraction
│   ├── Convertisseur.py                # Interface principale
│   └── BLMM_SET.txt                    # Données existantes
│
├── database/                           # Module base de données  
│   ├── db_manager.py                   # Gestionnaire SQLite
│   ├── csv_importer.py                 # Import CSV → DB
│   └── collection.db                   # Base de données (auto-créée)
│
├── collection_manager/                 # Interface de gestion
│   └── main_gui.py                     # Interface principale
│
└── shared/                            # Configuration partagée
    └── config.py                      # Paramètres globaux
```

## 🎯 **Workflow Type**

1. **Extraire des cartes** → Convertisseur → CSV
2. **Importer en base** → Collection Manager → Onglet Import
3. **Gérer sa collection** → Marquer possédé/non possédé
4. **Consulter statistiques** → Vue d'ensemble

## 🔧 **Prérequis**

### Python & Dépendances
```powershell
# Créer environnement virtuel
python -m venv .venv
.venv\Scripts\Activate.ps1

# Installer dépendances
pip install selenium requests tkinter
```

### WebDriver (pour Convertisseur)
- Chrome/Edge automatiquement géré par Selenium 4+
- Ou télécharger manuellement ChromeDriver

## 📊 **Format CSV Exporté**

```csv
Code_Serie,Nom_Carte,Rareté,Numéro_Carte
RA02,Blue-Eyes White Dragon,Secret Rare,RA02-FR001
RA02,Blue-Eyes White Dragon,Ultra Rare,RA02-FR001
RA02,Dark Magician,Ghost Rare,RA02-FR002
```

## � **Séries Supportées**

- **LOB** : Legend of Blue Eyes White Dragon
- **MRD** : Metal Raiders  
- **SRL** : Spell Ruler
- **PSV** : Pharaoh's Servant
- **RA02** : 25th Anniversary Rarity Collection II
- *Et plus...*

## 🔄 **Évolutions Futures**

- [ ] Export PDF de collection
- [ ] Statistiques avancées par rareté
- [ ] Import depuis autres sources
- [ ] Sauvegarde cloud
- [ ] Mode recherche avancée

## 🐛 **Problèmes Connus**

- Selenium peut nécessiter des mises à jour du WebDriver
- Certains sites peuvent bloquer l'extraction automatique
- Interface peut être lente sur de très grandes collections

## 📞 **Support**

En cas de problème :
1. Vérifiez que Python est installé
2. Vérifiez les dépendances (`pip list`)
3. Consultez les logs d'erreur dans la console

---
*Projet créé pour la gestion de collections Yu-Gi-Oh personnelles*

---

*Convertisseur Yu-Gi-Oh V2 - Interface Graphique*
*Extraction automatique de cartes depuis Yugipedia*
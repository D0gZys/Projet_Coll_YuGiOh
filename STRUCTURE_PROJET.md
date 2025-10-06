# 🎮 Projet Yu-Gi-Oh Collection Manager
# Structure des dossiers proposée

Projet_Coll_YuGiOh/
│
├── 📁 convertisseur/              # Module d'extraction
│   ├── Convertisseur.py           # Moteur d'extraction
│   ├── Convertisseur_GUI.py       # Interface d'extraction
│   ├── Lancer_Interface.bat       # Lanceur rapide
│   ├── urls_sauvees.json          # URLs mémorisées
│   └── temp/                      # CSV temporaires
│       └── *.csv                  # Fichiers extraits
│
├── 📁 database/                   # Module base de données
│   ├── db_manager.py              # Gestionnaire SQLite
│   ├── db_schema.sql              # Structure des tables
│   ├── collection.db              # Base SQLite
│   └── csv_importer.py            # Import des CSV
│
├── 📁 collection_manager/         # Interface principale
│   ├── main_gui.py                # Interface de gestion
│   ├── collection_viewer.py       # Visualiseur de collection
│   └── stats_viewer.py            # Statistiques
│
├── 📁 shared/                     # Utilitaires partagés
│   ├── config.py                  # Configuration
│   └── utils.py                   # Fonctions communes
│
├── requirements.txt               # Dépendances Python
├── README.md                      # Documentation
└── run_collection_manager.bat     # Lanceur principal
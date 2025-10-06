#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration globale du projet Yu-Gi-Oh Collection Manager
"""

import os
from pathlib import Path

# Chemins du projet
PROJECT_ROOT = Path(__file__).parent.parent
CONVERTISSEUR_DIR = PROJECT_ROOT / "convertisseur"
DATABASE_DIR = PROJECT_ROOT / "database"  
COLLECTION_MANAGER_DIR = PROJECT_ROOT / "collection_manager"
TEMP_CSV_DIR = CONVERTISSEUR_DIR / "temp"

# Base de données
DATABASE_PATH = DATABASE_DIR / "collection.db"
SCHEMA_PATH = DATABASE_DIR / "database_schema.sql"

# Configuration de l'interface
GUI_CONFIG = {
    "titre_principal": "Yu-Gi-Oh Collection Manager",
    "titre_convertisseur": "Convertisseur Yu-Gi-Oh V2", 
    "taille_fenetre_principale": "1200x800",
    "taille_fenetre_convertisseur": "700x600",
    "theme": "clam"
}

# Palette de couleurs douce
COLORS = {
    "primary": "#2E4057",      # Bleu marine doux
    "secondary": "#048A81",     # Turquoise
    "accent": "#54C6EB",       # Bleu clair
    "success": "#52B788",      # Vert doux
    "warning": "#F4A261",      # Orange doux
    "danger": "#E76F51",       # Rouge doux
    "light": "#F8F9FA",        # Blanc cassé
    "dark": "#495057",         # Gris foncé
    "muted": "#6C757D",        # Gris moyen
    "card_bg": "#FFFFFF",      # Blanc pur pour les cartes
    "hover": "#E9ECEF",        # Gris très clair pour hover
    "selected": "#CCE7FF"      # Bleu très clair pour sélection
}

# Symboles Unicode subtils
SYMBOLS = {
    "series": "◆",
    "cards": "♢", 
    "owned": "●",
    "not_owned": "○",
    "stats": "▣",
    "import": "⤴",
    "export": "⤵",
    "refresh": "↻",
    "search": "⌕",
    "filter": "⧩",
    "collection": "⬢",
    "folder": "📁",
    "file": "📄"
}

# Séries Yu-Gi-Oh connues (pour l'auto-détection)
SERIES_CONNUES = {
    'BLMM': 'Battles of Legend: Monster Mayhem',
    'BLMR': 'Battles of Legend: Monstrous Revenge',
    'BLAR': 'Battles of Legend: Armageddon', 
    'BLCR': 'Battles of Legend: Crystal Revenge',
    'RA02': '25th Anniversary Rarity Collection II',
    'RA01': '25th Anniversary Rarity Collection',
    'CYAC': 'Cyberstorm Access',
    'MP24': 'Mega Pack 2024',
    'MP23': 'Mega Pack 2023',
    'POTE': 'Power of the Elements',
    'DABL': 'Darkwing Blast',
    'BACH': 'Battle of Chaos',
    'GFTP': 'Ghosts From the Past',
    'ROTD': 'Rise of the Duelist',
    'ETCO': 'Eternity Code',
    'IGAS': 'Ignition Assault'
}

# Configuration des raretés (ordre et couleurs pour l'affichage)
RARETES_CONFIG = {
    'Common': {'ordre': 1, 'couleur': '#000000', 'abbrev': 'C'},
    'Rare': {'ordre': 2, 'couleur': '#FFD700', 'abbrev': 'R'},
    'Super Rare': {'ordre': 3, 'couleur': '#C0C0C0', 'abbrev': 'SR'},
    'Ultra Rare': {'ordre': 4, 'couleur': '#FF6B35', 'abbrev': 'UR'},
    'Secret Rare': {'ordre': 5, 'couleur': '#8A2BE2', 'abbrev': 'ScR'},
    'Ultimate Rare': {'ordre': 6, 'couleur': '#FF1493', 'abbrev': 'UtR'},
    'Ghost Rare': {'ordre': 7, 'couleur': '#708090', 'abbrev': 'GR'},
    'Starlight Rare': {'ordre': 8, 'couleur': '#FFE4B5', 'abbrev': 'StR'},
    'Collector\'s Rare': {'ordre': 9, 'couleur': '#9932CC', 'abbrev': 'CR'},
    'Platinum Secret Rare': {'ordre': 10, 'couleur': '#E5E4E2', 'abbrev': 'PScR'},
    'Quarter Century Secret Rare': {'ordre': 11, 'couleur': '#DAA520', 'abbrev': 'QCScR'}
}

# URLs par défaut pour le convertisseur
URLS_DEFAUT = {
    "BLMM": "https://yugipedia.com/wiki/Set_Card_Lists:Battles_of_Legend:_Monster_Mayhem_(TCG-FR)",
    "BLMR": "https://yugipedia.com/wiki/Set_Card_Lists:Battles_of_Legend:_Monstrous_Revenge_(TCG-FR)",
    "BLAR": "https://yugipedia.com/wiki/Set_Card_Lists:Battles_of_Legend:_Armageddon_(TCG-FR)",
    "RA02": "https://yugipedia.com/wiki/Set_Card_Lists:25th_Anniversary_Rarity_Collection_II_(TCG-FR)"
}

def creer_dossiers_projet():
    """Crée tous les dossiers nécessaires du projet"""
    dossiers = [
        CONVERTISSEUR_DIR,
        TEMP_CSV_DIR,
        DATABASE_DIR,
        COLLECTION_MANAGER_DIR
    ]
    
    for dossier in dossiers:
        dossier.mkdir(exist_ok=True)
        print(f"📁 Dossier vérifié : {dossier}")

def get_chemin_relatif(chemin_absolu):
    """Convertit un chemin absolu en relatif par rapport au projet"""
    try:
        return Path(chemin_absolu).relative_to(PROJECT_ROOT)
    except ValueError:
        return Path(chemin_absolu)

def formater_nombre_cartes(nombre):
    """Formate un nombre de cartes pour l'affichage"""
    if nombre == 0:
        return "Aucune carte"
    elif nombre == 1:
        return "1 carte"
    else:
        return f"{nombre:,} cartes".replace(',', ' ')

def formater_pourcentage(pourcentage):
    """Formate un pourcentage pour l'affichage"""
    if pourcentage == 0:
        return "0%"
    elif pourcentage == 100:
        return "100% ✅"
    elif pourcentage >= 80:
        return f"{pourcentage:.1f}% 🟢"
    elif pourcentage >= 50:
        return f"{pourcentage:.1f}% 🟡"
    else:
        return f"{pourcentage:.1f}% 🔴"

# Test de la configuration
if __name__ == "__main__":
    print("🔧 Test de la configuration")
    print(f"📂 Racine du projet : {PROJECT_ROOT}")
    print(f"🗄️ Base de données : {DATABASE_PATH}")
    print(f"📊 CSV temporaires : {TEMP_CSV_DIR}")
    
    # Créer les dossiers
    creer_dossiers_projet()
    
    print(f"📋 {len(SERIES_CONNUES)} séries configurées")
    print(f"🎨 {len(RARETES_CONFIG)} raretés configurées")
    print("✅ Configuration OK")
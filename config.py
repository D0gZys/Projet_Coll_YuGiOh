# Configuration des sets Yu-Gi-Oh pour l'interface graphique
# Format : "CODE_SET": {"nom": "Nom complet", "url": "URL Yugipedia"}

SETS_PREDEFINED = {
    "BLMM": {
        "nom": "Monster Mayhem",
        "url": "https://yugipedia.com/wiki/Set_Card_Lists:Battles_of_Legend:_Monster_Mayhem_(TCG-FR)"
    },
    "BLMR": {
        "nom": "Monstrous Revenge", 
        "url": "https://yugipedia.com/wiki/Set_Card_Lists:Battles_of_Legend:_Monstrous_Revenge_(TCG-FR)"
    },
    "BLAR": {
        "nom": "Armageddon",
        "url": "https://yugipedia.com/wiki/Set_Card_Lists:Battles_of_Legend:_Armageddon_(TCG-FR)"
    },
    "BLCR": {
        "nom": "Crystal Revenge",
        "url": "https://yugipedia.com/wiki/Set_Card_Lists:Battles_of_Legend:_Crystal_Revenge_(TCG-FR)"
    },
    "ROTD": {
        "nom": "Rise of the Duelist",
        "url": "https://yugipedia.com/wiki/Set_Card_Lists:Rise_of_the_Duelist_(TCG-FR)"
    }
}

# Configuration de l'interface
INTERFACE_CONFIG = {
    "titre": "🎮 Convertisseur Yu-Gi-Oh V2 - Interface Graphique",
    "taille_fenetre": "700x600",
    "theme": "clam",
    "police_titre": ("Arial", 16, "bold"),
    "police_normale": ("Arial", 10),
    "police_console": ("Consolas", 9)
}

# Messages d'aide
AIDE_MESSAGES = {
    "url_aide": "Coller l'URL de la page Yugipedia du set (format TCG-FR)",
    "serie_aide": "Nom pour le fichier de sortie (sans extension .txt)",
    "extraction_aide": "L'extraction peut prendre 10-30 secondes selon la taille du set"
}
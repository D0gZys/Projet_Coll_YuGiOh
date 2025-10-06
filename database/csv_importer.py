#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importateur de fichiers CSV dans la base de données SQLite
"""

import csv
import os
import re
import json
import requests
from urllib.parse import unquote
from pathlib import Path
from typing import List, Dict, Tuple
from db_manager import DatabaseManager

class CSVImporter:
    def __init__(self, db_manager: DatabaseManager = None):
        """
        Initialise l'importateur CSV
        
        Args:
            db_manager: Instance du gestionnaire de base de données
        """
        self.db = db_manager or DatabaseManager()
    
    def charger_urls_sauvees(self) -> Dict[str, str]:
        """
        Charge les URLs sauvegardées depuis les fichiers JSON du convertisseur
        
        Returns:
            Dict[str, str]: Dictionnaire {code_serie: url}
        """
        urls = {}
        
        # Chemins possibles pour les fichiers d'URLs
        chemins_possibles = [
            # Fichier global dans la racine du projet
            Path(__file__).parent.parent / "urls_sauvees.json",
            # Fichier dans le convertisseur
            Path(__file__).parent.parent / "convertisseur" / "urls_sauvees.json",
            # Fichier local dans le répertoire courant
            Path("urls_sauvees.json")
        ]
        
        for chemin in chemins_possibles:
            try:
                if chemin.exists():
                    with open(chemin, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        urls.update(data)
                    print(f"📂 URLs chargées depuis : {chemin}")
                    break
            except Exception as e:
                print(f"⚠️ Erreur lors du chargement de {chemin} : {e}")
                continue
        
        if urls:
            print(f"🔗 {len(urls)} URLs de séries chargées")
        else:
            print("⚠️ Aucune URL de série trouvée")
        
        return urls
    
    def extraire_nom_serie_depuis_url(self, url: str) -> str:
        """
        Extrait le nom de la série depuis une URL Yugipedia
        
        Args:
            url (str): URL Yugipedia de la série
            
        Returns:
            str: Nom de la série extrait de l'URL, ou nom générique si échec
        """
        if not url or not isinstance(url, str):
            return None
        
        try:
            # Extraire le nom depuis l'URL
            # Ex: "Set_Card_Lists:Battles_of_Legend:_Monster_Mayhem_(TCG-FR)"
            patterns = [
                r'Set_Card_Lists:([^(]+?)_\(TCG-FR\)',           # Pattern principal
                r'Set_Card_Lists:([^(]+?)_\(TCG',                # Sans -FR
                r'Set_Card_Lists:([^/]+?)(?:\?|$)',             # Pattern alternatif
                r'wiki/([^/]+?)(?:\?|$)',                        # Pattern général wiki
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    nom_brut = match.group(1)
                    
                    # Décoder les caractères URL d'abord
                    nom_decode = unquote(nom_brut)
                    
                    # Nettoyer le nom
                    nom_propre = nom_decode.replace('_', ' ')
                    nom_propre = nom_propre.replace(':', ': ')
                    nom_propre = nom_propre.strip()
                    
                    # Corrections spécifiques
                    nom_propre = nom_propre.replace('25th Anniversary Tin  Dueling Heroes', '25th Anniversary Tin: Dueling Heroes')
                    
                    return nom_propre
        
        except Exception as e:
            print(f"⚠️ Erreur lors de l'extraction du nom depuis l'URL : {e}")
        
        return None
    
    def detecter_info_serie(self, nom_fichier: str, premier_code: str = None) -> Tuple[str, str]:
        """
        Détecte automatiquement les informations de série depuis le nom de fichier
        ou le premier code de carte
        
        Args:
            nom_fichier (str): Nom du fichier CSV
            premier_code (str): Premier code de carte trouvé
        
        Returns:
            Tuple[str, str]: (code_serie, nom_serie_estimé)
        """
        # Extraire depuis le nom de fichier
        nom_base = Path(nom_fichier).stem
        
        # Priorité 1: Extraire depuis le premier code de carte (plus fiable)
        if premier_code:
            match_code = re.match(r'^([A-Z0-9]+)-FR', premier_code)
            code_serie = match_code.group(1) if match_code else "UNKNOWN"
        else:
            # Priorité 2: Essayer d'extraire le code depuis le nom de fichier
            code_depuis_nom = re.match(r'^([A-Z0-9]+)', nom_base.upper())
            if code_depuis_nom:
                code_serie = code_depuis_nom.group(1)
            else:
                code_serie = "UNKNOWN"
        
        # Essayer de récupérer le nom depuis l'URL correspondante
        nom_serie = f"Série {code_serie}"  # Nom par défaut
        
        # Charger les URLs pour récupérer le nom depuis l'URL
        try:
            urls_sauvees = self.charger_urls_sauvees()
            url_serie = urls_sauvees.get(code_serie)
            
            if url_serie:
                nom_extrait = self.extraire_nom_serie_depuis_url(url_serie)
                if nom_extrait:
                    nom_serie = nom_extrait
                    print(f"📝 Nom extrait de l'URL pour {code_serie} : {nom_serie}")
            
        except Exception as e:
            print(f"⚠️ Erreur lors de l'extraction du nom depuis l'URL : {e}")
        
        return code_serie, nom_serie
    
    def valider_format_csv(self, fichier_csv: str) -> Tuple[bool, str]:
        """
        Valide que le fichier CSV a le bon format
        
        Returns:
            Tuple[bool, str]: (est_valide, message)
        """
        try:
            with open(fichier_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Vérifier les colonnes requises
                colonnes_requises = ['Code_Serie', 'Nom_Carte', 'Rareté', 'Numéro_Carte']
                colonnes_presentes = reader.fieldnames
                
                if not colonnes_presentes:
                    return False, "Fichier CSV vide ou sans en-têtes"
                
                colonnes_manquantes = [col for col in colonnes_requises if col not in colonnes_presentes]
                if colonnes_manquantes:
                    return False, f"Colonnes manquantes : {', '.join(colonnes_manquantes)}"
                
                # Tester la première ligne pour vérifier le format
                premiere_ligne = next(reader, None)
                if not premiere_ligne:
                    return False, "Fichier CSV sans données"
                
                # Vérifier que les champs ne sont pas vides
                for colonne in colonnes_requises:
                    if not premiere_ligne.get(colonne, '').strip():
                        return False, f"Première ligne invalide : colonne '{colonne}' vide"
                
                return True, "Format CSV valide"
                
        except Exception as e:
            return False, f"Erreur lors de la validation : {e}"
    
    def importer_csv(self, fichier_csv: str, auto_detect: bool = True, 
                    code_serie_force: str = None, nom_serie_force: str = None,
                    url_source: str = None) -> Dict[str, int]:
        """
        Importe un fichier CSV dans la base de données
        
        Args:
            fichier_csv (str): Chemin vers le fichier CSV
            auto_detect (bool): Détection automatique des infos de série
            code_serie_force (str): Forcer un code de série spécifique
            nom_serie_force (str): Forcer un nom de série spécifique
            url_source (str): URL source Yugipedia
        
        Returns:
            Dict[str, int]: Statistiques d'import (cartes ajoutées, liens créés, etc.)
        """
        print(f"📥 Import du fichier : {fichier_csv}")
        
        # Valider le format
        valide, message = self.valider_format_csv(fichier_csv)
        if not valide:
            raise ValueError(f"Format CSV invalide : {message}")
        
        print(f"✅ {message}")
        
        stats = {
            'cartes_ajoutees': 0,
            'liens_crees': 0,
            'cartes_existantes': 0,
            'erreurs': 0
        }
        
        # Lire le CSV
        with open(fichier_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            lignes = list(reader)
        
        if not lignes:
            raise ValueError("Fichier CSV vide")
        
        # Détecter ou utiliser les informations de série
        if auto_detect and not code_serie_force:
            premier_numero = lignes[0]['Numéro_Carte']
            code_serie, nom_serie = self.detecter_info_serie(fichier_csv, premier_numero)
        else:
            code_serie = code_serie_force or "UNKNOWN"
            nom_serie = nom_serie_force or f"Série {code_serie}"
        
        print(f"📊 Série détectée : {code_serie} - {nom_serie}")
        
        # Charger les URLs sauvegardées et récupérer l'URL pour cette série
        if not url_source:  # Si pas d'URL fournie en paramètre
            urls_sauvees = self.charger_urls_sauvees()
            url_source = urls_sauvees.get(code_serie)
            if url_source:
                print(f"🔗 URL trouvée pour {code_serie} : {url_source}")
        
        # Ajouter/récupérer la série
        try:
            serie_id = self.db.ajouter_serie(code_serie, nom_serie, url_source)
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout de série : {e}")
            return stats
        
        # Traiter chaque ligne
        cartes_traitees = set()  # Pour éviter les doublons de cartes
        
        for i, ligne in enumerate(lignes, 1):
            try:
                numero_carte = ligne['Numéro_Carte'].strip()
                nom_carte = ligne['Nom_Carte'].strip()
                nom_rarete = ligne['Rareté'].strip()
                
                if not all([numero_carte, nom_carte, nom_rarete]):
                    print(f"⚠️  Ligne {i} : données manquantes, ignorée")
                    continue
                
                # Ajouter la carte si pas encore traitée
                if numero_carte not in cartes_traitees:
                    carte_id = self.db.ajouter_carte(numero_carte, nom_carte, serie_id)
                    if carte_id:
                        stats['cartes_ajoutees'] += 1
                        cartes_traitees.add(numero_carte)
                    else:
                        stats['cartes_existantes'] += 1
                        cartes_traitees.add(numero_carte)
                
                # Récupérer l'ID de la carte
                carte_id = self.db.get_connection().execute(
                    'SELECT id FROM cartes WHERE numero_carte = ?', (numero_carte,)
                ).fetchone()
                
                if not carte_id:
                    print(f"❌ Ligne {i} : impossible de trouver la carte {numero_carte}")
                    stats['erreurs'] += 1
                    continue
                
                carte_id = carte_id[0]
                
                # Récupérer/créer l'ID de la rareté
                rarete_id = self.db.get_rarete_id(nom_rarete)
                
                # Créer le lien carte-rareté
                if self.db.lier_carte_rarete(carte_id, rarete_id):
                    stats['liens_crees'] += 1
                
            except Exception as e:
                print(f"❌ Erreur ligne {i} : {e}")
                stats['erreurs'] += 1
                continue
        
        # Afficher le résumé
        print(f"\n📊 Import terminé pour {code_serie} :")
        print(f"  ➕ Cartes ajoutées : {stats['cartes_ajoutees']}")
        print(f"  🔗 Liens carte-rareté créés : {stats['liens_crees']}")
        print(f"  ↻  Cartes existantes : {stats['cartes_existantes']}")
        print(f"  ❌ Erreurs : {stats['erreurs']}")
        
        return stats
    
    def importer_dossier(self, dossier_csv: str = "convertisseur/temp") -> Dict[str, Dict]:
        """
        Importe tous les fichiers CSV d'un dossier
        
        Args:
            dossier_csv (str): Chemin vers le dossier contenant les CSV
        
        Returns:
            Dict[str, Dict]: Statistiques d'import par fichier
        """
        if not os.path.exists(dossier_csv):
            print(f"❌ Dossier non trouvé : {dossier_csv}")
            return {}
        
        fichiers_csv = [f for f in os.listdir(dossier_csv) if f.endswith('.csv')]
        
        if not fichiers_csv:
            print(f"❌ Aucun fichier CSV trouvé dans {dossier_csv}")
            return {}
        
        print(f"📁 Import de {len(fichiers_csv)} fichiers CSV...")
        
        resultats = {}
        fichiers_a_supprimer = []
        
        for fichier in fichiers_csv:
            chemin_complet = os.path.join(dossier_csv, fichier)
            try:
                stats = self.importer_csv(chemin_complet)
                resultats[fichier] = stats
                # Marquer le fichier pour suppression si l'import a réussi
                if stats.get('cartes_ajoutees', 0) > 0 or stats.get('liens_crees', 0) > 0:
                    fichiers_a_supprimer.append(chemin_complet)
                    stats['fichier_supprime'] = True
            except Exception as e:
                print(f"❌ Échec import {fichier} : {e}")
                resultats[fichier] = {'erreur': str(e)}
        
        # Supprimer les fichiers importés avec succès
        for chemin_fichier in fichiers_a_supprimer:
            try:
                os.remove(chemin_fichier)
                nom_fichier = os.path.basename(chemin_fichier)
                print(f"🗑️ Fichier supprimé : {nom_fichier}")
            except Exception as e:
                print(f"⚠️ Impossible de supprimer {nom_fichier} : {e}")
        
        return resultats

# Test et utilitaires
def tester_import():
    """Fonction de test de l'importateur"""
    print("🧪 Test de l'importateur CSV")
    
    # Créer une instance de test
    importer = CSVImporter(DatabaseManager("database/test_collection.db"))
    
    # Test avec un fichier factice (si disponible)
    test_files = ["test_RA02.csv", "convertisseur/temp/*.csv"]
    
    for pattern in test_files:
        if '*' in pattern:
            import glob
            files = glob.glob(pattern)
            for file in files:
                if os.path.exists(file):
                    print(f"📄 Test avec : {file}")
                    try:
                        stats = importer.importer_csv(file)
                        print(f"✅ Import réussi : {stats}")
                    except Exception as e:
                        print(f"❌ Erreur : {e}")
        else:
            if os.path.exists(pattern):
                print(f"📄 Test avec : {pattern}")
                try:
                    stats = importer.importer_csv(pattern)
                    print(f"✅ Import réussi : {stats}")
                except Exception as e:
                    print(f"❌ Erreur : {e}")
    
    print("✅ Test terminé")

if __name__ == "__main__":
    tester_import()
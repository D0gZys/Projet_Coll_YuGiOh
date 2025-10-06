#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convertisseur pour extraire les cartes Yu-Gi-Oh du set BLMM
Extrait le nom français, numéro et rareté de chaque carte
"""

import re
from html import unescape
import requests
import time
import csv

# Import optionnel pour Selenium (navigateur automatisé)
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

def recuperer_contenu_selenium(url):
    """
    Utilise Selenium pour récupérer le contenu (contourne les protections anti-bot)
    
    Args:
        url (str): L'URL de la page
    
    Returns:
        str: Le contenu HTML ou None
    """
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium n'est pas installé. Utilisez: pip install selenium")
        return None
    
    try:
        print("🤖 Lancement du navigateur automatisé...")
        
        # Configuration Chrome en mode headless (sans interface)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Mode sans interface
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Installer et utiliser ChromeDriver automatiquement
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Masquer les traces de Selenium
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print(f"🌐 Chargement de la page: {url}")
        driver.get(url)
        
        # Attendre que la page se charge complètement
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "tbody"))
        )
        
        # Récupérer le HTML complet
        page_source = driver.page_source
        
        # Fermer le navigateur
        driver.quit()
        
        # Chercher tous les tbody et filtrer celui qui contient des cartes
        pattern_tbody = r'<tbody>.*?</tbody>'
        matches = re.findall(pattern_tbody, page_source, re.DOTALL | re.IGNORECASE)
        
        print(f"🔍 Trouvé {len(matches)} tableaux sur la page")
        
        for i, tbody in enumerate(matches):
            # Chercher des codes de cartes avec plusieurs patterns
            patterns_cartes = [
                r'[A-Z]{4}-FR\d+',           # Pattern standard (BLMM, CYAC, etc.)
                r'[A-Z]{2}\d{2}-FR\d+',      # Pattern RA02, MP24, etc. (2 lettres + 2 chiffres)
                r'[A-Z0-9]{4}-FR\d+',        # Pattern mixte lettres/chiffres
                r'RA02-FR\d+',               # Pattern spécifique RA02
                r'href="[^"]*-FR\d+'         # Liens vers les cartes
            ]
            
            carte_trouvee = False
            for j, pattern in enumerate(patterns_cartes):
                matches_pattern = re.findall(pattern, tbody)
                if matches_pattern:
                    print(f"✅ Tableau #{i+1} avec cartes trouvé! (Pattern {j+1}: {len(matches_pattern)} cartes)")
                    print(f"📊 Taille: {len(tbody)} caractères")
                    print(f"🔍 Exemples trouvés: {matches_pattern[:3]}")
                    return tbody
            
            if not carte_trouvee:
                print(f"⏭️  Tableau #{i+1} sans cartes (taille: {len(tbody)} chars)")
        
        print("❌ Aucun tableau contenant des cartes trouvé")
        return None
            
    except Exception as e:
        print(f"❌ Erreur Selenium: {e}")
        if 'driver' in locals():
            driver.quit()
        return None

def recuperer_contenu_web(url):
    """
    Récupère le contenu HTML d'une page web et extrait la section contenant les cartes
    
    Args:
        url (str): L'URL de la page contenant les informations des cartes
    
    Returns:
        str: Le contenu HTML de la section avec les cartes, ou None en cas d'erreur
    """
    try:
        # Headers pour simuler un navigateur web normal et contourner les protections anti-bot
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        print(f"Récupération du contenu depuis: {url}")
        
        # Créer une session pour maintenir les cookies
        session = requests.Session()
        session.headers.update(headers)
        
        # Attendre un peu pour simuler un comportement humain
        time.sleep(2)
        
        response = session.get(url, timeout=30)
        response.raise_for_status()  # Lève une exception si le statut HTTP indique une erreur
        
        # Le contenu HTML complet
        html_content = response.text
        
        # Chercher la section contenant le tableau des cartes
        # Pattern pour trouver le tbody contenant les cartes
        pattern_tbody = r'<tbody>.*?</tbody>'
        match = re.search(pattern_tbody, html_content, re.DOTALL | re.IGNORECASE)
        
        if match:
            tbody_content = match.group(0)
            print(f"Section des cartes trouvée! ({len(tbody_content)} caractères)")
            return tbody_content
        else:
            print("⚠️  Aucune section <tbody> trouvée dans la page")
            # Essayer de chercher directement les lignes de cartes
            pattern_tr = r'<tr>.*?</tr>'
            matches_tr = re.findall(pattern_tr, html_content, re.DOTALL | re.IGNORECASE)
            
            # Filtrer pour ne garder que les lignes contenant des références de cartes
            lignes_cartes = []
            for tr in matches_tr:
                if re.search(r'[A-Z]{4}-FR\d+', tr):  # Pattern générique pour les codes de cartes
                    lignes_cartes.append(tr)
            
            if lignes_cartes:
                contenu_cartes = ''.join(lignes_cartes)
                print(f"Lignes de cartes trouvées directement! ({len(lignes_cartes)} cartes)")
                return contenu_cartes
            else:
                print("❌ Aucune carte trouvée dans la page")
                return None
                
    except requests.exceptions.Timeout:
        print("❌ Erreur: Timeout lors de la récupération de la page")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Impossible de se connecter au site")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"❌ Erreur HTTP: {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du contenu web: {e}")
        return None

def extraire_cartes_depuis_fichier():
    """
    Extrait les cartes depuis un fichier local (méthode originale)
    """
    # Essayer différents fichiers selon le set
    fichiers_possibles = ['BOLM_SET.txt', 'JUSH_SET.txt', 'BLMM_SET.txt']
    
    for fichier in fichiers_possibles:
        try:
            with open(fichier, 'r', encoding='utf-8') as f:
                print(f"📁 Lecture du fichier: {fichier}")
                return f.read()
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier {fichier}: {e}")
            continue
    
    print(f"❌ Aucun fichier trouvé parmi: {', '.join(fichiers_possibles)}")
    return None

def extraire_cartes_blmm(url=None):
    """
    Extrait toutes les cartes depuis une URL ou un fichier local
    
    Args:
        url (str, optional): URL de la page contenant les cartes. Si None, utilise le fichier local.
    
    Returns:
        list: Liste de dictionnaires avec nom, numero et rareté
    """
    cartes = []
    
    try:
        # Récupérer le contenu soit depuis l'URL soit depuis le fichier
        if url:
            # Essayer d'abord Selenium (plus efficace contre les protections)
            contenu = recuperer_contenu_selenium(url)
            
            # Si Selenium échoue, essayer requests classique
            if not contenu:
                print("🔄 Tentative avec requests classique...")
                contenu = recuperer_contenu_web(url)
            
            # Si tout échoue, utiliser le fichier local
            if not contenu:
                print("🔄 Échec de la récupération web, tentative avec le fichier local...")
                contenu = extraire_cartes_depuis_fichier()
        else:
            contenu = extraire_cartes_depuis_fichier()
        
        if not contenu:
            return []
        
        # DEBUG: Afficher un extrait du contenu récupéré
        print(f"🔍 Extrait du contenu récupéré (500 premiers caractères):")
        print(contenu[:500])
        print("..." if len(contenu) > 500 else "")
        
        # Diviser le contenu en lignes de cartes
        lignes_tr = re.findall(r'<tr>.*?</tr>', contenu, re.DOTALL)
        
        for ligne in lignes_tr:
            # Extraire le numéro de carte - patterns multiples pour différents sets
            patterns_numero = [
                r'<a href="[^"]*?([A-Z]{4}-FR\d+)"',     # Standard 4 lettres
                r'<a href="[^"]*?([A-Z]{2}\d{2}-FR\d+)"', # RA02, MP24, etc.
                r'<a href="[^"]*?([A-Z0-9]{4}-FR\d+)"',  # Mixte lettres/chiffres
                r'title="([A-Z]{2}\d{2}-FR\d+)"',        # Dans les titres
                r'([A-Z]{2}\d{2}-FR\d+)',                # Pattern direct RA02
                r'([A-Z]{4}-FR\d+)',                     # Pattern direct standard
            ]
            
            numero = None
            for pattern in patterns_numero:
                match_numero = re.search(pattern, ligne)
                if match_numero:
                    numero = match_numero.group(1)
                    break
            
            if not numero:
                continue
            
            # Extraire le nom français
            nom_francais = "Nom non trouvé"
            
            # Chercher d'abord dans un span lang="fr" - gérer les guillemets imbriqués
            match_nom_fr = re.search(r'<span lang="fr">"(.*?)"</span>', ligne, re.DOTALL)
            if match_nom_fr:
                nom_francais = match_nom_fr.group(1)
            else:
                # Si pas de span, chercher dans les td directement
                tds = re.findall(r'<td>([^<]*)</td>', ligne)
                if len(tds) >= 2:
                    # Essayer de prendre le deuxième td qui pourrait être le nom français
                    potential_name = tds[1].strip()
                    if potential_name and potential_name.startswith('"') and potential_name.endswith('"'):
                        nom_francais = potential_name[1:-1]  # Enlever les guillemets
            
            # Nettoyer le nom français
            nom_francais = unescape(nom_francais.strip())
            
            # Extraire les raretés avec patterns améliorés
            raretes = []
            patterns_rarete = [
                r'title="([^"]*(?:Rare|Common)[^"]*)"',    # Pattern principal
                r'alt="([^"]*(?:Rare|Common)[^"]*)"',      # Pattern alternatif
                r'>([^<]*(?:Rare|Common)[^<]*)<',          # Dans le texte direct
            ]
            
            for pattern in patterns_rarete:
                matches_rarete = re.findall(pattern, ligne)
                for rarete in matches_rarete:
                    rarete_clean = rarete.strip()
                    if rarete_clean and rarete_clean not in raretes:
                        raretes.append(rarete_clean)
            
            # Limiter le nombre de raretés pour éviter les chaînes trop longues
            if len(raretes) > 8:  # Limiter à 8 raretés max
                raretes = raretes[:8]
                raretes.append("...")  # Indiquer qu'il y en a plus
            
            rarete_finale = " / ".join(raretes) if raretes else "Rareté non trouvée"
            
            # Limiter la longueur totale de la chaîne de rareté
            if len(rarete_finale) > 200:  # Limiter à 200 caractères
                rarete_finale = rarete_finale[:197] + "..."
            
            carte = {
                'numero': numero,
                'nom': nom_francais,
                'rarete': rarete_finale
            }
            
            cartes.append(carte)
    
    except Exception as e:
        print(f"Erreur lors du traitement des données: {e}")
        return []
    
    return cartes

def extraire_code_serie(numero_carte):
    """
    Extrait le code de série d'un numéro de carte
    Ex: BLMM-FR001 -> BLMM, RA02-FR001 -> RA02
    """
    import re
    match = re.match(r'([A-Z0-9]+)-FR\d+', numero_carte)
    if match:
        return match.group(1)
    return "UNKNOWN"

def sauvegarder_cartes_csv(cartes, nom_fichier="cartes.csv"):
    """
    Sauvegarde la liste des cartes dans un fichier CSV
    Format: Code_Serie, Nom_Carte, Rareté, Numéro_Carte
    Une ligne par rareté si une carte a plusieurs raretés
    """
    try:
        import os
        
        # Obtenir le répertoire du fichier Convertisseur.py
        repertoire_script = os.path.dirname(os.path.abspath(__file__))
        
        # Créer le dossier temp dans le même répertoire que le convertisseur
        dossier_temp = os.path.join(repertoire_script, "temp")
        if not os.path.exists(dossier_temp):
            os.makedirs(dossier_temp)
            print(f"📁 Dossier créé: {dossier_temp}")
        
        # Construire le chemin complet vers le fichier CSV
        chemin_fichier = os.path.join(dossier_temp, nom_fichier)
        
        lignes_csv = []
        
        for carte in cartes:
            code_serie = extraire_code_serie(carte['numero'])
            nom_carte = carte['nom']
            numero_carte = carte['numero']
            
            # Séparer les raretés multiples
            if ' / ' in carte['rarete']:
                raretes = [r.strip() for r in carte['rarete'].split(' / ')]
            else:
                raretes = [carte['rarete']]
            
            # Créer une ligne pour chaque rareté
            for rarete in raretes:
                if rarete and rarete != "...":  # Ignorer les "..." ajoutés pour limiter
                    lignes_csv.append([code_serie, nom_carte, rarete, numero_carte])
        
        # Écrire le fichier CSV dans le dossier temp
        with open(chemin_fichier, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            # En-têtes
            writer.writerow(['Code_Serie', 'Nom_Carte', 'Rareté', 'Numéro_Carte'])
            
            # Données
            writer.writerows(lignes_csv)
        
        print(f"Fichier CSV sauvegardé: {chemin_fichier}")
        print(f"Nombre de lignes créées: {len(lignes_csv)} (cartes avec raretés séparées)")
        print(f"Nombre de cartes originales: {len(cartes)}")
        
    except Exception as e:
        print(f"Erreur lors de la sauvegarde CSV: {e}")

def sauvegarder_cartes_txt(cartes, nom_fichier="cartes_BOLM.txt"):
    """
    Sauvegarde la liste des cartes dans un fichier texte (ancienne version)
    """
    try:
        with open(nom_fichier, 'w', encoding='utf-8') as f:
            f.write("Liste des cartes du set Battles of Legend: Monster Mayhem\n")
            f.write("=" * 50 + "\n\n")
            
            for carte in cartes:
                f.write(f"Numéro: {carte['numero']}\n")
                f.write(f"Nom: {carte['nom']}\n")
                f.write(f"Rareté: {carte['rarete']}\n")
                f.write("-" * 30 + "\n")
        
        print(f"Fichier sauvegardé: {nom_fichier}")
        print(f"Nombre de cartes extraites: {len(cartes)}")
        
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")

def main(url=None):
    """
    Fonction principale
    
    Args:
        url (str, optional): URL de la page contenant les cartes
    """
    print("Extraction des cartes...")
    
    if url:
        print(f"Mode Web: Récupération depuis {url}")
    else:
        print("Mode Fichier: Lecture depuis le fichier local")
    
    # Extraire les cartes
    cartes = extraire_cartes_blmm(url)
    
    if cartes:
        # Afficher quelques exemples
        print(f"\nNombre de cartes trouvées: {len(cartes)}")
        print("\nPremières cartes extraites:")
        for i, carte in enumerate(cartes[:5]):
            print(f"{i+1}. {carte['numero']} - {carte['nom']} ({carte['rarete']})")
        
        # Sauvegarder dans un fichier
        sauvegarder_cartes_txt(cartes)
    else:
        print("Aucune carte n'a pu être extraite.")

def extraire_depuis_url(url):
    """
    Fonction helper pour extraire directement depuis une URL
    
    Args:
        url (str): L'URL de la page Yu-Gi-Oh wiki contenant les cartes
        
    Example:
        extraire_depuis_url("https://yugioh.fandom.com/wiki/Judgment_of_the_Light")
    """
    return main(url)

def extraire_depuis_fichier():
    """
    Fonction helper pour extraire depuis le fichier local
    """
    return main()

def demander_url_utilisateur():
    """
    Demande à l'utilisateur de saisir une URL ou d'utiliser le fichier local
    """
    print("\n" + "="*60)
    print("🎮 CONVERTISSEUR YU-GI-OH V2")
    print("="*60)
    print("Choisissez votre mode :")
    print("1. 🌐 Récupérer depuis une URL (site web)")
    print("2. 📁 Lire depuis un fichier local")
    print("3. ❌ Quitter")
    
    while True:
        choix = input("\nVotre choix (1/2/3): ").strip()
        
        if choix == "1":
            print("\n📝 Saisissez l'URL de la page Yu-Gi-Oh Wiki:")
            print("Exemple: https://yugioh.fandom.com/wiki/Brothers_of_Legend")
            url = input("URL: ").strip()
            
            if url:
                return url
            else:
                print("❌ URL vide, veuillez réessayer.")
                
        elif choix == "2":
            return None  # Utiliser le fichier local
            
        elif choix == "3":
            print("👋 Au revoir !")
            exit()
            
        else:
            print("❌ Choix invalide. Veuillez choisir 1, 2 ou 3.")

if __name__ == "__main__":
    # 🔧 CONFIGURATION RAPIDE :
    # Méthode 1 - Renseigner directement l'URL ici :
    URL_SITE = "https://yugipedia.com/wiki/Set_Card_Lists:Battles_of_Legend:_Monster_Mayhem_(TCG-FR)"
    
    # Méthode 2 - Mode interactif (décommentez la ligne ci-dessous) :
    # URL_SITE = demander_url_utilisateur()
    
    # Exemples d'URLs Yu-Gi-Oh Wiki courantes :
    # "https://yugioh.fandom.com/wiki/Judgment_of_the_Light"
    # "https://yugioh.fandom.com/wiki/Brothers_of_Legend" 
    # "https://yugioh.fandom.com/wiki/Legacy_of_Destruction"
    # "https://yugioh.fandom.com/wiki/Battles_of_Legend:_Monstrous_Revenge"
    
    # Exécution selon la configuration
    if URL_SITE:
        print(f"🌐 Mode Web activé avec l'URL: {URL_SITE}")
        main(URL_SITE)
    else:
        print("📁 Mode Fichier activé (lecture depuis fichier local)")
        main()

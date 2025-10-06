#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface graphique pour le Convertisseur Yu-Gi-Oh V2
Permet de saisir l'URL et le nom de série via une interface conviviale
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import sys
import os
from pathlib import Path
import webbrowser
import json
import re

# Import du convertisseur existant
from Convertisseur import extraire_cartes_blmm, sauvegarder_cartes_csv

class ConvertisseurGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎮 Convertisseur Yu-Gi-Oh V2 - Interface Graphique")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Variables
        self.url_var = tk.StringVar()
        self.serie_var = tk.StringVar()
        self.progression_var = tk.StringVar(value="Prêt à extraire...")
        
        # Fichier pour sauvegarder les URLs
        self.urls_file = "urls_sauvees.json"
        
        # Configuration du style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Charger les URLs sauvées
        self.urls_sauvees = self.charger_urls_sauvees()
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Titre principal
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(
            title_frame, 
            text="🎮 Convertisseur Yu-Gi-Oh V2",
            font=("Arial", 16, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Extracteur automatique de cartes depuis Yugipedia",
            font=("Arial", 10)
        )
        subtitle_label.pack()
        
        # Cadre principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Section URL
        url_frame = ttk.LabelFrame(main_frame, text="🌐 URL du set Yugipedia", padding="10")
        url_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(url_frame, text="Coller l'URL de la page du set :").pack(anchor=tk.W)
        
        url_entry_frame = ttk.Frame(url_frame)
        url_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.url_entry = ttk.Entry(
            url_entry_frame, 
            textvariable=self.url_var,
            font=("Arial", 10),
            width=60
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            url_entry_frame,
            text="📋",
            width=3,
            command=self.coller_url
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Exemples d'URLs
        self.exemples_frame = ttk.Frame(url_frame)
        self.exemples_frame.pack(fill=tk.X, pady=(5, 0))
        
        exemples_header_frame = ttk.Frame(self.exemples_frame)
        exemples_header_frame.pack(fill=tk.X)
        
        ttk.Label(exemples_header_frame, text="💡 Exemples rapides :", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        ttk.Button(
            exemples_header_frame,
            text="🔄",
            width=3,
            command=self.rafraichir_exemples
        ).pack(side=tk.RIGHT)
        
        # Créer les boutons d'exemples dynamiques
        self.rafraichir_exemples()
        
        # Section nom de série
        serie_frame = ttk.LabelFrame(main_frame, text="📁 Nom de la série", padding="10")
        serie_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(serie_frame, text="Nom pour le fichier (sans extension) :").pack(anchor=tk.W)
        
        self.serie_entry = ttk.Entry(
            serie_frame,
            textvariable=self.serie_var,
            font=("Arial", 10)
        )
        self.serie_entry.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(
            serie_frame,
            text="� Le fichier sera sauvé comme : [nom_serie].csv (format tableur)",
            font=("Arial", 9),
            foreground="gray"
        ).pack(anchor=tk.W, pady=(2, 0))
        
        # Boutons d'action
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.btn_extraire = ttk.Button(
            action_frame,
            text="🚀 Extraire les cartes",
            command=self.lancer_extraction,
            style="Accent.TButton"
        )
        self.btn_extraire.pack(side=tk.LEFT)
        
        ttk.Button(
            action_frame,
            text="📂 Ouvrir dossier",
            command=self.ouvrir_dossier
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(
            action_frame,
            text="❓ Aide",
            command=self.afficher_aide
        ).pack(side=tk.RIGHT)
        
        # Zone de progression
        progress_frame = ttk.LabelFrame(main_frame, text="📊 Progression", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_label = ttk.Label(
            progress_frame,
            textvariable=self.progression_var,
            font=("Arial", 10)
        )
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate'
        )
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Zone de log
        log_frame = ttk.LabelFrame(main_frame, text="📋 Journal d'activité", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def charger_urls_sauvees(self):
        """Charge les URLs sauvées depuis le fichier JSON"""
        try:
            if os.path.exists(self.urls_file):
                with open(self.urls_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement des URLs : {e}")
        
        # URLs par défaut si le fichier n'existe pas
        return {
            "BLMM - Monster Mayhem": "https://yugipedia.com/wiki/Set_Card_Lists:Battles_of_Legend:_Monster_Mayhem_(TCG-FR)",
            "BLMR - Monstrous Revenge": "https://yugipedia.com/wiki/Set_Card_Lists:Battles_of_Legend:_Monstrous_Revenge_(TCG-FR)",
            "BLAR - Armageddon": "https://yugipedia.com/wiki/Set_Card_Lists:Battles_of_Legend:_Armageddon_(TCG-FR)"
        }
    
    def sauvegarder_urls(self):
        """Sauvegarde les URLs dans le fichier JSON"""
        try:
            with open(self.urls_file, 'w', encoding='utf-8') as f:
                json.dump(self.urls_sauvees, f, indent=2, ensure_ascii=False)
            self.log(f"💾 URLs sauvées dans {self.urls_file}")
        except Exception as e:
            self.log(f"❌ Erreur lors de la sauvegarde des URLs : {e}")
    
    def extraire_nom_set_depuis_url(self, url):
        """Extrait un nom de set depuis l'URL"""
        # Chercher des patterns comme "Battles_of_Legend:_Monster_Mayhem"
        patterns = [
            r'Set_Card_Lists:([^_(]+(?:_[^_(]+)*)',
            r'wiki/([^/]+)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                nom_brut = match.group(1)
                # Nettoyer le nom
                nom_propre = nom_brut.replace('_', ' ').replace(':', ' - ')
                # Enlever "(TCG-FR)" et autres suffixes
                nom_propre = re.sub(r'\s*\([^)]*\)\s*$', '', nom_propre)
                return nom_propre.strip()
        
        # Si aucun pattern ne marche, utiliser un nom générique
        return f"Set {len(self.urls_sauvees) + 1}"
    
    def ajouter_nouvelle_url(self, url, nom_serie):
        """Ajoute une nouvelle URL aux exemples si elle n'existe pas déjà"""
        # Vérifier si l'URL existe déjà
        if url in self.urls_sauvees.values():
            return False
        
        # Créer un nom pour l'exemple
        nom_exemple = self.extraire_nom_set_depuis_url(url)
        
        # Si on a un nom de série personnalisé, l'utiliser
        if nom_serie and nom_serie.strip():
            nom_exemple = nom_serie.strip()
        
        # Ajouter à la liste
        self.urls_sauvees[nom_exemple] = url
        
        # Sauvegarder et rafraîchir l'interface
        self.sauvegarder_urls()
        self.rafraichir_exemples()
        
        self.log(f"✨ Nouvelle URL ajoutée aux exemples : {nom_exemple}")
        return True
    
    def rafraichir_exemples(self):
        """Rafraîchit les boutons d'exemples"""
        # Supprimer les anciens boutons d'exemples
        for widget in self.exemples_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.destroy()
        
        # Recréer les boutons avec les nouvelles données
        for nom, url in self.urls_sauvees.items():
            btn_frame = ttk.Frame(self.exemples_frame)
            btn_frame.pack(fill=tk.X, pady=1)
            
            ttk.Button(
                btn_frame,
                text=nom,
                command=lambda u=url, n=nom: self.utiliser_exemple(u, n)
            ).pack(side=tk.LEFT)
            
            # Bouton pour supprimer cet exemple
            ttk.Button(
                btn_frame,
                text="🗑️",
                width=3,
                command=lambda n=nom: self.supprimer_exemple(n)
            ).pack(side=tk.RIGHT, padx=(5, 0))
    
    def supprimer_exemple(self, nom):
        """Supprime un exemple des URLs sauvées"""
        if nom in self.urls_sauvees:
            del self.urls_sauvees[nom]
            self.sauvegarder_urls()
            self.rafraichir_exemples()
            self.log(f"🗑️ Exemple supprimé : {nom}")
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def coller_url(self):
        """Colle le contenu du presse-papier dans l'URL"""
        try:
            clipboard_content = self.root.clipboard_get()
            self.url_var.set(clipboard_content)
            self.log("📋 URL collée depuis le presse-papier")
        except tk.TclError:
            self.log("⚠️  Rien à coller dans le presse-papier")
    
    def utiliser_exemple(self, url, nom):
        """Utilise un exemple prédéfini"""
        self.url_var.set(url)
        # Extraire un nom de série propre pour le fichier
        serie_suggeree = nom.split(" - ")[-1] if " - " in nom else nom
        self.serie_var.set(serie_suggeree)
        self.log(f"💡 Exemple sélectionné : {nom}")
    
    def log(self, message):
        """Ajoute un message au journal"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def valider_saisie(self):
        """Valide les données saisies"""
        url = self.url_var.get().strip()
        serie = self.serie_var.get().strip()
        
        if not url:
            messagebox.showerror("Erreur", "Veuillez saisir une URL")
            return False
        
        if not serie:
            messagebox.showerror("Erreur", "Veuillez saisir un nom de série")
            return False
        
        if not url.startswith("http"):
            messagebox.showerror("Erreur", "L'URL doit commencer par http:// ou https://")
            return False
        
        return True
    
    def lancer_extraction(self):
        """Lance l'extraction en arrière-plan"""
        if not self.valider_saisie():
            return
        
        # Désactiver le bouton pendant l'extraction
        self.btn_extraire.config(state="disabled")
        self.progress_bar.start()
        
        # Lancer l'extraction dans un thread séparé
        thread = threading.Thread(target=self.extraire_cartes)
        thread.daemon = True
        thread.start()
    
    def extraire_cartes(self):
        """Effectue l'extraction des cartes"""
        try:
            url = self.url_var.get().strip()
            serie = self.serie_var.get().strip()
            
            self.progression_var.set("🚀 Lancement de l'extraction...")
            self.log(f"🌐 Début de l'extraction depuis : {url}")
            self.log(f"📁 Série : {serie}")
            
            # Import de la variable globale pour modifier l'URL
            import Convertisseur
            Convertisseur.URL_ACTUELLE = url
            
            self.progression_var.set("🤖 Lancement du navigateur...")
            self.log("🤖 Ouverture du navigateur automatisé...")
            
            # Extraction
            cartes = extraire_cartes_blmm(url)
            
            if cartes:
                self.progression_var.set(f"💾 Sauvegarde de {len(cartes)} cartes...")
                self.log(f"✅ {len(cartes)} cartes extraites avec succès!")
                
                # Sauvegarder avec le nom personnalisé au format CSV
                nom_fichier = f"{serie}.csv"
                sauvegarder_cartes_csv(cartes, nom_fichier)
                
                self.log(f"💾 Cartes sauvegardées dans : {nom_fichier}")
                self.progression_var.set(f"✅ Extraction terminée! ({len(cartes)} cartes)")
                
                # Afficher quelques exemples
                self.log("📋 Aperçu des cartes extraites :")
                for i, carte in enumerate(cartes[:3]):
                    self.log(f"  {i+1}. {carte['numero']} - {carte['nom']} ({carte['rarete']})")
                if len(cartes) > 3:
                    self.log(f"  ... et {len(cartes) - 3} autres cartes")
                
                # Ajouter l'URL aux exemples si c'est une nouvelle
                if self.ajouter_nouvelle_url(url, serie):
                    self.log("🔖 URL ajoutée aux exemples rapides pour les prochaines fois!")
                
                messagebox.showinfo(
                    "Extraction réussie",
                    f"🎉 Extraction terminée!\n\n"
                    f"📊 {len(cartes)} cartes extraites\n"
                    f"💾 Fichier : {nom_fichier}\n\n"
                    f"Voulez-vous ouvrir le dossier?"
                )
                
            else:
                self.log("❌ Aucune carte trouvée")
                self.progression_var.set("❌ Extraction échouée")
                messagebox.showerror(
                    "Erreur d'extraction",
                    "Aucune carte n'a pu être extraite.\n"
                    "Vérifiez l'URL et votre connexion internet."
                )
        
        except Exception as e:
            error_msg = str(e)
            self.log(f"❌ Erreur : {error_msg}")
            self.progression_var.set("❌ Erreur lors de l'extraction")
            messagebox.showerror("Erreur", f"Erreur lors de l'extraction :\n{error_msg}")
        
        finally:
            # Réactiver l'interface
            self.btn_extraire.config(state="normal")
            self.progress_bar.stop()
    
    def ouvrir_dossier(self):
        """Ouvre le dossier contenant les fichiers"""
        try:
            dossier = Path(__file__).parent
            if sys.platform == "win32":
                os.startfile(dossier)
            elif sys.platform == "darwin":
                os.system(f"open {dossier}")
            else:
                os.system(f"xdg-open {dossier}")
        except Exception as e:
            self.log(f"❌ Impossible d'ouvrir le dossier : {e}")
    
    def afficher_aide(self):
        """Affiche la fenêtre d'aide"""
        aide_window = tk.Toplevel(self.root)
        aide_window.title("❓ Aide - Convertisseur Yu-Gi-Oh")
        aide_window.geometry("600x500")
        aide_window.resizable(False, False)
        
        # Centre la fenêtre d'aide
        aide_window.transient(self.root)
        aide_window.grab_set()
        
        # Contenu de l'aide
        aide_frame = ttk.Frame(aide_window, padding="20")
        aide_frame.pack(fill=tk.BOTH, expand=True)
        
        aide_text = scrolledtext.ScrolledText(aide_frame, wrap=tk.WORD, font=("Arial", 10))
        aide_text.pack(fill=tk.BOTH, expand=True)
        
        aide_content = """
🎮 GUIDE D'UTILISATION - CONVERTISSEUR YU-GI-OH V2

📋 ÉTAPES D'EXTRACTION :

1️⃣ TROUVER L'URL :
   • Aller sur yugipedia.com
   • Chercher votre set (ex: "Battles of Legend Monster Mayhem")
   • Aller dans "Set Card Lists" → Version française (TCG-FR)
   • Copier l'URL de la page

2️⃣ CONFIGURER L'EXTRACTION :
   • Coller l'URL dans le champ prévu
   • Donner un nom à votre série (ex: "Monster_Mayhem")
   • Cliquer sur "Extraire les cartes"

3️⃣ RÉSULTAT :
   • Le fichier sera créé automatiquement
   • Format : cartes_[nom_serie].txt
   • Contient : Numéro - Nom français (Rareté)

🌐 URLS COMPATIBLES :
   ✅ yugipedia.com/wiki/Set_Card_Lists:..._(TCG-FR)
   ✅ Pages de sets français sur Yugipedia
   ❌ Autres sites non supportés

🔧 DÉPANNAGE :

⚠️ "Aucune carte trouvée" :
   • Vérifiez que l'URL est correcte
   • Assurez-vous que c'est une page de set français
   • Testez votre connexion internet

⚠️ "Erreur de navigateur" :
   • Fermez les autres navigateurs Chrome
   • Redémarrez le programme

💡 CONSEILS :
   • Utilisez les exemples pour tester
   • Le nom de série peut contenir des lettres, chiffres et underscores
   • L'extraction peut prendre 10-30 secondes selon le set

🆘 SUPPORT :
   En cas de problème persistant, vérifiez les messages dans le journal d'activité.
        """
        
        aide_text.insert("1.0", aide_content)
        aide_text.config(state="disabled")
        
        # Bouton fermer
        ttk.Button(
            aide_frame,
            text="Fermer",
            command=aide_window.destroy
        ).pack(pady=(10, 0))
    
    def run(self):
        """Lance l'interface graphique"""
        self.root.mainloop()

def main():
    """Fonction principale"""
    app = ConvertisseurGUI()
    app.run()

if __name__ == "__main__":
    main()
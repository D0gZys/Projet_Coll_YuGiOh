#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface moderne du gestionnaire de collection Yu-Gi-Oh avec CustomTkinter
Version avec angles arrondis et design moderne natif
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
import sqlite3
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif pour éviter les conflits
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import numpy as np

# Configuration CustomTkinter
ctk.set_appearance_mode("system")  # "light", "dark" ou "system"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

# Ajouter le dossier parent au path pour les imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    # Imports préférés (packages)
    from database.db_manager import DatabaseManager
    from database.csv_importer import CSVImporter  
    from shared.config import GUI_CONFIG, TEMP_CSV_DIR, COLORS, SYMBOLS, formater_nombre_cartes, formater_pourcentage
except ImportError:
    # Fallback : imports directs
    sys.path.insert(0, str(project_root / "database"))
    sys.path.insert(0, str(project_root / "shared"))
    try:
        from db_manager import DatabaseManager
        from csv_importer import CSVImporter
        from config import GUI_CONFIG, TEMP_CSV_DIR, COLORS, SYMBOLS, formater_nombre_cartes, formater_pourcentage
    except ImportError as e:
        print(f"❌ Erreur d'import critique : {e}")
        print("💡 Vérifiez que tous les fichiers sont présents")
        sys.exit(1)

class CollectionManagerGUI:
    def __init__(self):
        # Fenêtre principale CustomTkinter
        self.root = ctk.CTk()
        self.root.title("Yu-Gi-Oh Collection Manager")
        self.root.geometry("2400x1600")
        
        # Initialiser la base de données
        self.db = DatabaseManager()
        self.importer = CSVImporter(self.db)
        
        # Variables
        self.stats_var = tk.StringVar()
        
        # Configuration basique du style (pour compatibilité)
        self.style = ttk.Style()
        
        self.setup_ui()
        self.rafraichir_donnees()
        self.center_window()
    
    def create_modern_card(self, parent, title, **kwargs):
        """Crée une carte moderne avec effet ombre simulé"""
        # Frame conteneur avec marge pour l'ombre
        container = ttk.Frame(parent, style="Modern.TFrame")
        
        # Simulation d'ombre avec plusieurs frames décalés
        shadow_frame = tk.Frame(container, bg="#CBD5E0", height=2)
        shadow_frame.pack(fill=tk.X, pady=(0, 0), padx=(2, 0))
        
        # Frame principal de la carte
        card_frame = ttk.LabelFrame(container, text=title, style="Card.TLabelframe", **kwargs)
        card_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 2), padx=(0, 2))
        
        return container, card_frame
    
    def create_gradient_frame(self, parent, color1="#FFFFFF", color2="#F7FAFC"):
        """Simule un dégradé avec des frames superposées"""
        gradient_frame = tk.Frame(parent, bg=color1)
        
        # Effet de dégradé simulé avec transparence
        overlay = tk.Frame(gradient_frame, bg=color2, height=1)
        overlay.pack(fill=tk.X, side=tk.BOTTOM)
        
        return gradient_frame
    
    def setup_styles(self):
        """Configure les styles visuels modernes"""
        # Configuration de la fenêtre principale avec gradient simulé
        self.root.configure(bg="#F5F7FA")  # Gris très clair moderne
        
        # === STYLES MODERNES MATERIAL DESIGN ===
        
        # Cadre principal moderne
        self.style.configure("Modern.TFrame", 
                           background="#F5F7FA",
                           relief="flat")
        
        # Cartes modernes avec effet ombre simulé
        self.style.configure("Card.TLabelframe",
                           background="#FFFFFF",
                           relief="solid",
                           borderwidth=1,
                           lightcolor="#E2E8F0",
                           darkcolor="#CBD5E0")
        
        self.style.configure("Card.TLabelframe.Label",
                           font=("Segoe UI", 10, "bold"),
                           background="#FFFFFF",
                           foreground="#2D3748")
        
        # Titre principal moderne
        self.style.configure("Hero.TLabel", 
                           font=("Segoe UI", 24, "normal"),
                           background="#F5F7FA",
                           foreground="#1A202C")
        
        # Sous-titre moderne
        self.style.configure("Subtitle.TLabel", 
                           font=("Segoe UI", 11),
                           background="#F5F7FA",
                           foreground="#718096")
        
        # Stats avec style Material
        self.style.configure("Stats.TLabel", 
                           font=("Segoe UI", 10, "bold"),
                           background="#FFFFFF",
                           foreground="#2D3748",
                           padding=(16, 12))
        
        # Boutons modernes style Material
        self.style.configure("Primary.TButton",
                           font=("Segoe UI", 9, "bold"),
                           padding=(20, 12),
                           focuscolor='none',
                           borderwidth=0,
                           relief="flat")
        
        # Effet hover simulé pour boutons
        self.style.map("Primary.TButton",
                      background=[('active', COLORS["secondary"]),
                                ('!active', COLORS["primary"])])
        
        # Boutons secondaires
        self.style.configure("Secondary.TButton",
                           font=("Segoe UI", 9),
                           padding=(16, 10),
                           focuscolor='none',
                           borderwidth=1,
                           relief="solid")
        
        self.style.map("Secondary.TButton",
                      background=[('active', COLORS["hover"]),
                                ('!active', "#FFFFFF")],
                      bordercolor=[('active', COLORS["primary"]),
                                 ('!active', "#E2E8F0")])
        
        # Treeview moderne
        self.style.configure("Modern.Treeview",
                           background="#FFFFFF",
                           foreground="#2D3748",
                           fieldbackground="#FFFFFF",
                           font=("Segoe UI", 9),
                           borderwidth=1,
                           relief="solid")
        
        self.style.configure("Modern.Treeview.Heading",
                           font=("Segoe UI", 9, "bold"),
                           foreground="#4A5568",
                           background="#F7FAFC",
                           borderwidth=1,
                           relief="solid")
        
        # Alternance de lignes moderne
        self.style.map("Modern.Treeview",
                      background=[('selected', '#EBF8FF'),
                                ('!selected', '#FFFFFF')])
        
        # Configuration des tags pour les cartes possédées/non possédées
        # Ces tags seront appliqués après la création du Treeview
    
    def configure_treeview_tags(self, treeview):
        """Configure les tags visuels pour différencier les cartes possédées"""
        # Tag pour les cartes possédées - vert prononcé
        treeview.tag_configure("owned", 
                             background="#D1FAE5",  # Vert clair mais visible
                             foreground="#047857",  # Vert très foncé et contrasté
                             font=("Segoe UI", 9, "bold"))  # Police en gras pour plus de visibilité
        
        # Tag pour les cartes non possédées - gris doux
        treeview.tag_configure("not_owned", 
                             background="#F9FAFB",  # Gris très clair
                             foreground="#6B7280",  # Gris moyen
                             font=("Segoe UI", 9, "normal"))
        
        # Tag pour les cartes sélectionnées possédées (ancien système)
        treeview.tag_configure("owned_selected",
                             background="#10B981",  # Vert vif
                             foreground="#FFFFFF")  # Blanc pour contraste maximal
        
        # Tag pour les cartes sélectionnées non possédées (ancien système)
        treeview.tag_configure("not_owned_selected",
                             background="#E5E7EB",  # Gris plus visible
                             foreground="#374151")  # Gris très foncé
        
        # Tags pour les cartes sélectionnées en mode sélection (BLEU)
        treeview.tag_configure("owned_selection_active",
                             background="#3B82F6",  # Bleu vif
                             foreground="#FFFFFF",  # Blanc pour contraste
                             font=("Segoe UI", 9, "bold"))
        
        treeview.tag_configure("not_owned_selection_active",
                             background="#60A5FA",  # Bleu plus clair
                             foreground="#FFFFFF",  # Blanc pour contraste
                             font=("Segoe UI", 9, "bold"))
        
        # Notebook moderne (onglets)
        self.style.configure("Modern.TNotebook",
                           background="#F5F7FA",
                           borderwidth=0)
        
        self.style.configure("Modern.TNotebook.Tab",
                           font=("Segoe UI", 10),
                           padding=(20, 12),
                           background="#E2E8F0",
                           foreground="#4A5568")
        
        self.style.map("Modern.TNotebook.Tab",
                      background=[('selected', '#FFFFFF'),
                                ('active', '#F7FAFC'),
                                ('!active', '#E2E8F0')])
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Menu principal
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        menu_fichier = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=f"{SYMBOLS['file']} Fichier", menu=menu_fichier)
        menu_fichier.add_command(label="⚙ Lancer Convertisseur", command=self.lancer_convertisseur)
        menu_fichier.add_separator()
        menu_fichier.add_command(label=f"{SYMBOLS['import']} Importer CSV...", command=self.importer_csv_fichier)
        menu_fichier.add_command(label=f"{SYMBOLS['folder']} Importer dossier CSV", command=self.importer_dossier_csv)
        menu_fichier.add_separator()
        menu_fichier.add_command(label=f"{SYMBOLS['refresh']} Actualiser", command=self.rafraichir_donnees)
        menu_fichier.add_separator()
        menu_fichier.add_command(label="✕ Quitter", command=self.root.quit)
        
        # Menu Collection
        menu_collection = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=f"{SYMBOLS['collection']} Collection", menu=menu_collection)
        menu_collection.add_command(label=f"{SYMBOLS['stats']} Voir statistiques", command=self.afficher_stats_detaillees)
        menu_collection.add_command(label=f"{SYMBOLS['search']} Cartes manquantes", command=self.afficher_cartes_manquantes)
        menu_collection.add_command(label=f"{SYMBOLS['owned']} Gerer possession", command=self.gerer_possession)
        
        # Header moderne CustomTkinter
        header_frame = ctk.CTkFrame(self.root, height=100, corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Titre principal moderne
        title_label = ctk.CTkLabel(
            header_frame,
            text="⬢ Yu-Gi-Oh Collection Manager",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 5))
        
        # Sous-titre moderne
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Gestionnaire moderne de collection avec base de données SQLite",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        subtitle_label.pack()
        
        # TabView moderne CustomTkinter
        self.tabview = ctk.CTkTabview(self.root, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Créer les onglets
        self.tab_overview = self.tabview.add(f"{SYMBOLS['stats']} Vue d'ensemble")
        self.tab_import = self.tabview.add(f"{SYMBOLS['import']} Import/Export")
        self.tab_collection = self.tabview.add(f"{SYMBOLS['collection']} Ma Collection")
        
        # Configurer chaque onglet
        self.setup_onglet_overview(self.tab_overview)
        self.setup_onglet_import(self.tab_import)
        self.setup_onglet_collection(self.tab_collection)
        
        # Barre de statut moderne CustomTkinter
        status_frame = ctk.CTkFrame(self.root, height=35, corner_radius=0)
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.stats_var,
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=15, pady=8)
    
    def setup_onglet_overview(self, tab_frame):
        """Configure l'onglet vue d'ensemble moderne"""
        # Frame principal avec scroll
        main_frame = ctk.CTkScrollableFrame(tab_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # En-tête de bienvenue
        welcome_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#1E3A8A")
        welcome_frame.pack(fill="x", pady=(0, 20))
        
        welcome_title = ctk.CTkLabel(
            welcome_frame,
            text="🎮 Collection Yu-Gi-Oh!",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        welcome_title.pack(pady=(20, 5))
        
        welcome_subtitle = ctk.CTkLabel(
            welcome_frame,
            text="Gérez votre collection de cartes avec style",
            font=ctk.CTkFont(size=14),
            text_color="#93C5FD"
        )
        welcome_subtitle.pack(pady=(0, 20))
        
        # Grid de cartes statistiques
        stats_grid = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="transparent")
        stats_grid.pack(fill="x", pady=(0, 20))
        
        # Configurer la grille
        stats_grid.grid_columnconfigure(0, weight=1)
        stats_grid.grid_columnconfigure(1, weight=1)
        stats_grid.grid_columnconfigure(2, weight=1)
        
        # Labels de statistiques (seront mis à jour par rafraichir_donnees)
        self.stats_labels = {}
        
        # Cartes statistiques avec couleurs et icônes
        stats_cards = [
            ("total_series", f"{SYMBOLS['series']} Séries", "Total", "#059669", "#D1FAE5"),
            ("total_cartes", f"{SYMBOLS['cards']} Cartes uniques", "Unique", "#DC2626", "#FEE2E2"),
            ("pourcentage_global", f"{SYMBOLS['stats']} Progression", "Global", "#7C3AED", "#EDE9FE"),
            ("exemplaires_possedes", f"{SYMBOLS['owned']} Possédés", "Possédés", "#059669", "#D1FAE5"),
            ("cartes_manquantes", f"{SYMBOLS['not_owned']} Manquantes", "Manquantes", "#DC2626", "#FEF2F2"),
            ("total_exemplaires", f"◇ Exemplaires", "Total", "#2563EB", "#DBEAFE")
        ]
        
        row, col = 0, 0
        for i, (key, title, subtitle, color, bg_color) in enumerate(stats_cards):
            card_frame = ctk.CTkFrame(stats_grid, corner_radius=12, fg_color=bg_color)
            card_frame.grid(row=row, column=col, padx=8, pady=8, sticky="ew")
            
            # Titre de la carte
            title_label = ctk.CTkLabel(
                card_frame,
                text=title,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=color
            )
            title_label.pack(pady=(15, 5))
            
            # Valeur statistique
            self.stats_labels[key] = ctk.CTkLabel(
                card_frame,
                text="...",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#1F2937"
            )
            self.stats_labels[key].pack(pady=(0, 5))
            
            # Éléments spéciaux selon le type de carte
            if key == "pourcentage_global":
                self.progress_bar = ctk.CTkProgressBar(
                    card_frame,
                    width=100,
                    height=8,
                    corner_radius=4,
                    progress_color=color
                )
                self.progress_bar.pack(pady=(0, 5))
                self.progress_bar.set(0)  # Sera mis à jour dans rafraichir_donnees
            elif key == "cartes_manquantes":
                # Bouton pour voir les détails des cartes manquantes
                btn_details = ctk.CTkButton(
                    card_frame,
                    text="📋 Voir les détails",
                    command=self.afficher_cartes_manquantes,
                    width=120,
                    height=28,
                    corner_radius=6,
                    fg_color=color,
                    hover_color="#B91C1C",
                    font=ctk.CTkFont(size=11)
                )
                btn_details.pack(pady=(0, 5))
            elif key == "exemplaires_possedes":
                # Bouton pour voir les détails des cartes possédées
                btn_details_owned = ctk.CTkButton(
                    card_frame,
                    text="📋 Voir les détails",
                    command=self.afficher_cartes_possedees,
                    width=120,
                    height=28,
                    corner_radius=6,
                    fg_color=color,
                    hover_color="#047857",
                    font=ctk.CTkFont(size=11)
                )
                btn_details_owned.pack(pady=(0, 5))
            elif key == "total_exemplaires":
                # Bouton pour voir tous les exemplaires (possédés + manquants)
                btn_details_total = ctk.CTkButton(
                    card_frame,
                    text="📋 Voir les détails",
                    command=self.afficher_tous_exemplaires,
                    width=120,
                    height=28,
                    corner_radius=6,
                    fg_color=color,
                    hover_color="#1D4ED8",
                    font=ctk.CTkFont(size=11)
                )
                btn_details_total.pack(pady=(0, 5))
            
            # Sous-titre
            subtitle_label = ctk.CTkLabel(
                card_frame,
                text=subtitle,
                font=ctk.CTkFont(size=10),
                text_color="#6B7280"
            )
            subtitle_label.pack(pady=(0, 15))
            
            col += 1
            if col >= 3:  # 3 colonnes max
                col = 0
                row += 1
        
        # Section des séries avec en-tête moderne
        series_section = ctk.CTkFrame(main_frame, corner_radius=15)
        series_section.pack(fill="both", expand=True, pady=(10, 0))
        
        # En-tête de la section
        series_header = ctk.CTkFrame(series_section, corner_radius=12, height=60)
        series_header.pack(fill="x", padx=15, pady=15)
        series_header.pack_propagate(False)
        
        series_title = ctk.CTkLabel(
            series_header,
            text=f"{SYMBOLS['series']} Aperçu des Séries",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1F2937"
        )
        series_title.pack(side="left", padx=15, pady=15)
        
        # Bouton d'actualisation global
        refresh_btn = ctk.CTkButton(
            series_header,
            text=f"{SYMBOLS['refresh']} Actualiser Tout",
            command=self.actualiser_vue_ensemble_complete,
            width=140,
            height=32,
            corner_radius=8,
            fg_color="#059669",
            hover_color="#047857"
        )
        refresh_btn.pack(side="right", padx=15, pady=14)
        
        # Container pour le tableau avec un effet d'ombre
        table_wrapper = ctk.CTkFrame(series_section, corner_radius=12, fg_color="#F8F9FA")
        table_wrapper.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Treeview pour les séries avec style moderne
        columns = ("Code", "Nom", "Total", "Possédés", "%")
        self.series_tree = ttk.Treeview(table_wrapper, columns=columns, show="headings", height=10)
        
        # Configuration des colonnes avec emojis
        self.series_tree.heading("Code", text="📦 Code")
        self.series_tree.heading("Nom", text="📚 Nom de la série")
        self.series_tree.heading("Total", text="🎴 Total")
        self.series_tree.heading("Possédés", text="✅ Possédés")
        self.series_tree.heading("%", text="📊 %")
        
        self.series_tree.column("Code", width=100, anchor="center")
        self.series_tree.column("Nom", width=350)
        self.series_tree.column("Total", width=80, anchor="center")
        self.series_tree.column("Possédés", width=90, anchor="center")
        self.series_tree.column("%", width=80, anchor="center")
        
        # Style pour le treeview
        style = ttk.Style()
        style.configure("Modern.Treeview", 
                       background="#FFFFFF",
                       foreground="#374151",
                       rowheight=25,
                       fieldbackground="#FFFFFF")
        style.configure("Modern.Treeview.Heading",
                       background="#F3F4F6",
                       foreground="#1F2937",
                       font=("Segoe UI", 10, "bold"))
        
        self.series_tree.configure(style="Modern.Treeview")
        
        # Scrollbar moderne
        tree_scroll = ttk.Scrollbar(table_wrapper, orient="vertical", command=self.series_tree.yview)
        self.series_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.series_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        tree_scroll.pack(side="right", fill="y", pady=10)
        
        # Petit texte d'aide en bas
        help_frame = ctk.CTkFrame(series_section, corner_radius=8, height=40, fg_color="#EFF6FF")
        help_frame.pack(fill="x", padx=15, pady=(0, 15))
        help_frame.pack_propagate(False)
        
        help_text = ctk.CTkLabel(
            help_frame,
            text="💡 Astuce: Cliquez sur 'Ma Collection' pour voir les détails de chaque série",
            font=ctk.CTkFont(size=11),
            text_color="#1E40AF"
        )
        help_text.pack(pady=12)
        
        # Créer une grille pour les graphiques (2 par ligne)
        self.graphs_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.graphs_container.pack(fill="both", expand=True, pady=(20, 0))
        
        # Configurer la grille
        self.graphs_container.grid_columnconfigure(0, weight=1)
        self.graphs_container.grid_columnconfigure(1, weight=1)
        
        # Ajouter les graphiques en grille 2x2 selon la nouvelle disposition
        self.creer_graphique_progression_series_compact(self.graphs_container, row=0, column=0)
        self.creer_heatmap_completion_compact(self.graphs_container, row=0, column=1)
        self.creer_graphique_objectifs_compact(self.graphs_container, row=1, column=0)
        self.creer_graphique_repartition_raretes_compact(self.graphs_container, row=1, column=1)
    
    def setup_onglet_import(self, tab_frame):
        """Configure l'onglet import/export moderne"""
        # Frame principal avec scroll
        main_frame = ctk.CTkScrollableFrame(tab_frame)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # En-tête de bienvenue
        welcome_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#7C3AED")
        welcome_frame.pack(fill="x", pady=(0, 20))
        
        welcome_title = ctk.CTkLabel(
            welcome_frame,
            text="🔄 Import & Export Manager",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        welcome_title.pack(pady=(20, 5))
        
        welcome_subtitle = ctk.CTkLabel(
            welcome_frame,
            text="Gérez vos données de collection avec efficacité",
            font=ctk.CTkFont(size=14),
            text_color="#C4B5FD"
        )
        welcome_subtitle.pack(pady=(0, 20))
        
        # Container pour les deux sections principales
        sections_container = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="transparent")
        sections_container.pack(fill="x", pady=(0, 20))
        
        # Section Convertisseur (gauche)
        conv_section = ctk.CTkFrame(sections_container, corner_radius=12)
        conv_section.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # En-tête section convertisseur
        conv_header = ctk.CTkFrame(conv_section, corner_radius=10, fg_color="#2563EB", height=60)
        conv_header.pack(fill="x", padx=15, pady=15)
        conv_header.pack_propagate(False)
        
        conv_title = ctk.CTkLabel(
            conv_header,
            text="⚙️ Convertisseur",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        conv_title.pack(pady=15)
        
        # Contenu convertisseur
        conv_content = ctk.CTkFrame(conv_section, corner_radius=8, fg_color="#F8FAFC")
        conv_content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        conv_desc = ctk.CTkLabel(
            conv_content,
            text="🌐 Extraire des cartes depuis Yugipedia\n📄 Convertir les données en format CSV\n⚡ Traitement automatisé des séries",
            font=ctk.CTkFont(size=12),
            text_color="#1E293B",
            justify="left"
        )
        conv_desc.pack(pady=(20, 15))
        
        conv_btn = ctk.CTkButton(
            conv_content,
            text="🚀 Lancer le Convertisseur",
            command=self.lancer_convertisseur,
            width=200,
            height=40,
            corner_radius=10,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        conv_btn.pack(pady=(0, 20))
        
        # Section Import CSV (droite)
        import_section = ctk.CTkFrame(sections_container, corner_radius=12)
        import_section.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        # En-tête section import
        import_header = ctk.CTkFrame(import_section, corner_radius=10, fg_color="#059669", height=60)
        import_header.pack(fill="x", padx=15, pady=15)
        import_header.pack_propagate(False)
        
        import_title = ctk.CTkLabel(
            import_header,
            text="📥 Import CSV",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        import_title.pack(pady=15)
        
        # Contenu import
        import_content = ctk.CTkFrame(import_section, corner_radius=8, fg_color="#F0FDF4")
        import_content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        import_desc = ctk.CTkLabel(
            import_content,
            text="📄 Importer des fichiers CSV individuels\n📁 Traitement en lot du dossier temp/\n🎯 Mise à jour automatique de la base",
            font=ctk.CTkFont(size=12),
            text_color="#1E293B",
            justify="left"
        )
        import_desc.pack(pady=(20, 15))
        
        # Boutons d'import
        import_btn_frame = ctk.CTkFrame(import_content, corner_radius=8, fg_color="transparent")
        import_btn_frame.pack(pady=(0, 20))
        
        import_file_btn = ctk.CTkButton(
            import_btn_frame,
            text="📄 Fichier CSV",
            command=self.importer_csv_fichier,
            width=140,
            height=35,
            corner_radius=8,
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        import_file_btn.pack(pady=5)
        
        import_folder_btn = ctk.CTkButton(
            import_btn_frame,
            text="📁 Dossier temp/",
            command=self.importer_dossier_csv,
            width=140,
            height=35,
            corner_radius=8,
            fg_color="#0891B2",
            hover_color="#0E7490",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        import_folder_btn.pack(pady=5)
        
        # Section Journal d'activité
        log_section = ctk.CTkFrame(main_frame, corner_radius=15)
        log_section.pack(fill="both", expand=True)
        
        # En-tête du journal
        log_header = ctk.CTkFrame(log_section, corner_radius=12, fg_color="#DC2626", height=60)
        log_header.pack(fill="x", padx=20, pady=20)
        log_header.pack_propagate(False)
        
        log_title = ctk.CTkLabel(
            log_header,
            text="📋 Journal d'Activité",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        log_title.pack(side="left", padx=20, pady=15)
        
        # Bouton de nettoyage du journal
        clear_log_btn = ctk.CTkButton(
            log_header,
            text="🗑️ Vider",
            command=self.vider_journal,
            width=80,
            height=30,
            corner_radius=8,
            fg_color="#7F1D1D",
            hover_color="#991B1B",
            font=ctk.CTkFont(size=11)
        )
        clear_log_btn.pack(side="right", padx=20, pady=15)
        
        # Container pour le journal avec scrollbar moderne
        log_container = ctk.CTkFrame(log_section, corner_radius=12, fg_color="#F8F9FA")
        log_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Zone de texte moderne avec scrollbar CustomTkinter
        self.log_text = tk.Text(
            log_container, 
            height=18, 
            wrap=tk.WORD, 
            font=("Consolas", 10),
            bg="#FFFFFF",
            fg="#1F2937",
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=10
        )
        
        log_scroll = ctk.CTkScrollbar(log_container, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        
        self.log_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        log_scroll.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
        # Message d'aide en bas
        help_frame = ctk.CTkFrame(log_section, corner_radius=8, height=50, fg_color="#EFF6FF")
        help_frame.pack(fill="x", padx=20, pady=(0, 20))
        help_frame.pack_propagate(False)
        
        help_text = ctk.CTkLabel(
            help_frame,
            text="💡 Conseil: Utilisez d'abord le convertisseur pour générer les fichiers CSV, puis importez-les dans la base de données",
            font=ctk.CTkFont(size=11),
            text_color="#1E40AF"
        )
        help_text.pack(pady=15)
    
    def setup_onglet_collection(self, tab_frame):
        """Configure l'onglet gestion de collection moderne"""
        # Frame principal avec en-tête
        main_frame = ctk.CTkFrame(tab_frame, corner_radius=12, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # En-tête moderne de la collection
        header_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#1E3A8A", height=80)
        header_frame.pack(fill="x", pady=(0, 15))
        header_frame.pack_propagate(False)
        
        # Titre et statistiques rapides dans l'en-tête
        header_content = ctk.CTkFrame(header_frame, corner_radius=8, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        collection_title = ctk.CTkLabel(
            header_content,
            text="🎴 Ma Collection Yu-Gi-Oh!",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        collection_title.pack(side="left")
        
        # Statistiques rapides dans l'en-tête
        self.quick_stats_label = ctk.CTkLabel(
            header_content,
            text="Chargement...",
            font=ctk.CTkFont(size=12),
            text_color="#93C5FD"
        )
        self.quick_stats_label.pack(side="right")
        
        # Container principal avec deux panels améliorés
        content_container = ctk.CTkFrame(main_frame, corner_radius=12)
        content_container.pack(fill="both", expand=True)
        
        # Panel gauche amélioré : Sélecteur de séries
        left_panel = ctk.CTkFrame(content_container, corner_radius=10)
        left_panel.pack(side="left", fill="both", expand=False, padx=(15, 8), pady=15)
        left_panel.configure(width=450)
        
        # En-tête du panel gauche
        left_header = ctk.CTkFrame(left_panel, corner_radius=8, fg_color="#F8FAFC", height=60)
        left_header.pack(fill="x", padx=10, pady=(10, 5))
        left_header.pack_propagate(False)
        
        series_title = ctk.CTkLabel(
            left_header, 
            text="📚 Sélectionnez une Série", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1E293B"
        )
        series_title.pack(pady=15)
        
        # Barre de recherche pour filtrer les séries
        search_frame = ctk.CTkFrame(left_panel, corner_radius=8, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Rechercher une série...",
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        self.search_entry.pack(fill="x", pady=5)
        self.search_entry.bind("<KeyRelease>", self.filtrer_series)
        
        # Container amélioré pour la liste des séries
        series_container = ctk.CTkFrame(left_panel, corner_radius=8)
        series_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Listbox améliorée avec style moderne
        self.series_listbox = tk.Listbox(
            series_container, 
            bg="#FFFFFF", 
            fg="#1F2937",
            selectbackground="#3B82F6",
            selectforeground="white",
            font=("Segoe UI", 11),
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            activestyle="none"
        )
        self.series_listbox.pack(fill="both", expand=True, padx=8, pady=8)
        self.series_listbox.bind('<<ListboxSelect>>', self.on_serie_select)
        
        # Scrollbar moderne pour la listbox
        series_scroll = ctk.CTkScrollbar(series_container, command=self.series_listbox.yview)
        series_scroll.pack(side="right", fill="y", padx=(0, 8), pady=8)
        self.series_listbox.configure(yscrollcommand=series_scroll.set)
        
        # Panel droit amélioré : Détails des cartes
        right_panel = ctk.CTkFrame(content_container, corner_radius=10)
        right_panel.pack(side="left", fill="both", expand=True, padx=(8, 15), pady=15)
        
        # En-tête du panel droit avec statistiques de série
        right_header = ctk.CTkFrame(right_panel, corner_radius=8, fg_color="#F8FAFC", height=80)
        right_header.pack(fill="x", padx=10, pady=(10, 5))
        right_header.pack_propagate(False)
        
        # Titre de la série sélectionnée
        self.serie_info_label = ctk.CTkLabel(
            right_header, 
            text="🎯 Sélectionnez une série", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1E293B"
        )
        self.serie_info_label.pack(pady=(10, 5))
        
        # Barre de progression de la série
        self.serie_progress_frame = ctk.CTkFrame(right_header, corner_radius=6, fg_color="transparent")
        self.serie_progress_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.serie_progress_bar = ctk.CTkProgressBar(
            self.serie_progress_frame,
            height=8,
            corner_radius=4,
            progress_color="#10B981"
        )
        self.serie_progress_bar.pack(fill="x")
        self.serie_progress_bar.set(0)
        
        # Outils et filtres
        tools_frame = ctk.CTkFrame(right_panel, corner_radius=8, fg_color="transparent")
        tools_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Frame unifié pour tous les filtres sur une seule ligne
        unified_filter_frame = ctk.CTkFrame(tools_frame, corner_radius=6)
        unified_filter_frame.pack(fill="x", pady=5)
        
        # Section 1: Filtres par statut
        filter_title = ctk.CTkLabel(unified_filter_frame, text="🔍 Statut :", 
                                   font=ctk.CTkFont(size=11, weight="bold"))
        filter_title.pack(side="left", padx=(10, 5), pady=8)
        
        # Boutons de filtre par statut
        self.filter_all_btn = ctk.CTkButton(
            unified_filter_frame,
            text="Toutes",
            command=lambda: self.filtrer_cartes("all"),
            width=70,
            height=28,
            corner_radius=6,
            fg_color="#6B7280",
            hover_color="#4B5563",
            font=ctk.CTkFont(size=10)
        )
        self.filter_all_btn.pack(side="left", padx=2, pady=8)
        
        self.filter_owned_btn = ctk.CTkButton(
            unified_filter_frame,
            text="Possédées",
            command=lambda: self.filtrer_cartes("owned"),
            width=70,
            height=28,
            corner_radius=6,
            fg_color="#10B981",
            hover_color="#059669",
            font=ctk.CTkFont(size=10)
        )
        self.filter_owned_btn.pack(side="left", padx=2, pady=8)
        
        self.filter_missing_btn = ctk.CTkButton(
            unified_filter_frame,
            text="Manquantes",
            command=lambda: self.filtrer_cartes("missing"),
            width=70,
            height=28,
            corner_radius=6,
            fg_color="#EF4444",
            hover_color="#DC2626",
            font=ctk.CTkFont(size=10)
        )
        self.filter_missing_btn.pack(side="left", padx=2, pady=8)
        
        # Séparateur visuel
        separator1 = ctk.CTkLabel(unified_filter_frame, text="|", 
                                 font=ctk.CTkFont(size=12),
                                 text_color="#9CA3AF")
        separator1.pack(side="left", padx=10, pady=8)
        
        # Section 2: Filtre par rareté
        rarity_title = ctk.CTkLabel(unified_filter_frame, text="⭐ Rareté :", 
                                   font=ctk.CTkFont(size=11, weight="bold"))
        rarity_title.pack(side="left", padx=(5, 5), pady=8)
        
        self.rarity_combobox = ctk.CTkComboBox(
            unified_filter_frame,
            values=["Toutes les raretés"],
            width=150,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(size=10),
            dropdown_font=ctk.CTkFont(size=9),
            command=self.filtrer_par_rarete
        )
        self.rarity_combobox.pack(side="left", padx=5, pady=8)
        self.rarity_combobox.set("Toutes les raretés")
        
        # Séparateur visuel
        separator2 = ctk.CTkLabel(unified_filter_frame, text="|", 
                                 font=ctk.CTkFont(size=12),
                                 text_color="#9CA3AF")
        separator2.pack(side="left", padx=10, pady=8)
        
        # Section 3: Recherche par nom/numéro
        search_title = ctk.CTkLabel(unified_filter_frame, text="🔎 Recherche :", 
                                   font=ctk.CTkFont(size=11, weight="bold"))
        search_title.pack(side="left", padx=(5, 5), pady=8)
        
        self.card_search_entry = ctk.CTkEntry(
            unified_filter_frame,
            placeholder_text="Nom ou n°...",
            width=180,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(size=10)
        )
        self.card_search_entry.pack(side="left", padx=5, pady=8)
        self.card_search_entry.bind("<KeyRelease>", self.rechercher_cartes)
        
        # Bouton pour effacer la recherche
        clear_search_btn = ctk.CTkButton(
            unified_filter_frame,
            text="✖",
            command=self.effacer_recherche_cartes,
            width=25,
            height=28,
            corner_radius=6,
            fg_color="#9CA3AF",
            hover_color="#6B7280",
            font=ctk.CTkFont(size=10)
        )
        clear_search_btn.pack(side="left", padx=2, pady=8)
        
        # Frame pour les outils de sélection multiple
        selection_frame = ctk.CTkFrame(right_panel, corner_radius=8, fg_color="#F8FAFC")
        selection_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Bouton pour activer/désactiver le mode sélection
        self.toggle_selection_btn = ctk.CTkButton(
            selection_frame,
            text="🎯 Activer Sélection",
            command=self.toggle_selection_mode,
            width=130,
            height=32,
            corner_radius=6,
            fg_color="#6366F1",
            hover_color="#4F46E5",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.toggle_selection_btn.pack(side="left", padx=(10, 5), pady=8)
        
        # Frame pour les outils de sélection (initialement cachés)
        self.selection_tools_frame = ctk.CTkFrame(selection_frame, corner_radius=6, fg_color="transparent")
        
        # Bouton "Tout sélectionner / Tout désélectionner"
        self.select_all_btn = ctk.CTkButton(
            self.selection_tools_frame,
            text="⭕ Tout sélectionner",
            command=self.toggle_select_all,
            width=130,
            height=30,
            corner_radius=6,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.select_all_btn.pack(side="left", padx=5, pady=8)
        
        # Bouton pour ajouter les cartes sélectionnées à la collection
        self.add_selected_btn = ctk.CTkButton(
            self.selection_tools_frame,
            text="➕ Ajouter",
            command=self.ajouter_cartes_selectionnees,
            width=120,
            height=30,
            corner_radius=6,
            fg_color="#10B981",
            hover_color="#059669",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.add_selected_btn.pack(side="left", padx=5, pady=8)
        
        # Bouton pour supprimer les cartes sélectionnées de la collection
        self.remove_selected_btn = ctk.CTkButton(
            self.selection_tools_frame,
            text="➖ Supprimer",
            command=self.supprimer_cartes_selectionnees,
            width=120,
            height=30,
            corner_radius=6,
            fg_color="#EF4444",
            hover_color="#DC2626",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.remove_selected_btn.pack(side="left", padx=5, pady=8)
        
        # Bouton pour supprimer définitivement les cartes sélectionnées de la base de données
        self.delete_selected_btn = ctk.CTkButton(
            self.selection_tools_frame,
            text="🗑️ Supprimer définitivement",
            command=self.supprimer_cartes_definitivement,
            width=180,
            height=30,
            corner_radius=6,
            fg_color="#B91C1C",
            hover_color="#991B1B",
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.delete_selected_btn.pack(side="left", padx=5, pady=8)
        
        # Label pour afficher le nombre de cartes sélectionnées
        self.selection_count_label = ctk.CTkLabel(
            self.selection_tools_frame,
            text="0 carte(s) sélectionnée(s)",
            font=ctk.CTkFont(size=10),
            text_color="#6B7280"
        )
        self.selection_count_label.pack(side="right", padx=(0, 10), pady=8)
        
        # Container amélioré pour le tableau des cartes
        tree_container = ctk.CTkFrame(right_panel, corner_radius=8)
        tree_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Treeview moderne pour les cartes (colonne sélection conditionnelle)
        self.base_columns = ("numero", "nom", "rarete", "possede")
        self.selection_columns = ("select", "numero", "nom", "rarete", "possede")
        
        # Commencer sans la colonne de sélection
        self.cartes_tree = ttk.Treeview(tree_container, columns=self.base_columns, show="headings", height=18)
        
        # Configuration des colonnes de base
        self.setup_tree_columns(False)
        
        # Style moderne pour le treeview des cartes
        style = ttk.Style()
        style.configure("Cards.Treeview",
                       background="#FFFFFF",
                       foreground="#1F2937",
                       rowheight=28,
                       fieldbackground="#FFFFFF")
        style.configure("Cards.Treeview.Heading",
                       background="#F1F5F9",
                       foreground="#334155",
                       font=("Segoe UI", 10, "bold"),
                       relief="flat")
        style.map("Cards.Treeview.Heading",
                 background=[('active', '#E2E8F0')])
        
        self.cartes_tree.configure(style="Cards.Treeview")
        
        # Configuration des tags visuels améliorés
        self.configure_treeview_tags(self.cartes_tree)
        
        # Scrollbar moderne
        tree_scroll = ctk.CTkScrollbar(tree_container, command=self.cartes_tree.yview)
        self.cartes_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.cartes_tree.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        tree_scroll.pack(side="right", fill="y", padx=(0, 8), pady=8)
        
        # Double-clic pour basculer le statut
        self.cartes_tree.bind("<Double-1>", self.toggle_carte_status)
        
        # Clic simple pour gérer la sélection
        self.cartes_tree.bind("<Button-1>", self.on_tree_click)
        
        # Variables pour la sélection
        self.selected_cards = set()
        self.all_selected = False
        self.selection_mode_active = False
        
        # Panel d'actions en bas amélioré
        actions_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        actions_frame.pack(fill="x", pady=(15, 0))
        
        # Légende moderne avec design amélioré
        legend_section = ctk.CTkFrame(actions_frame, corner_radius=8, fg_color="#F8FAFC")
        legend_section.pack(fill="x", padx=15, pady=(15, 10))
        
        legend_container = ctk.CTkFrame(legend_section, corner_radius=6, fg_color="transparent")
        legend_container.pack(fill="x", padx=15, pady=10)
        
        legend_title = ctk.CTkLabel(
            legend_container, 
            text="📋 Légende :", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#1E293B"
        )
        legend_title.pack(side="left")
        
        # Indicators visuels modernisés
        owned_indicator = ctk.CTkFrame(legend_container, corner_radius=15, width=20, height=20, fg_color="#10B981")
        owned_indicator.pack(side="left", padx=(20, 5))
        owned_indicator.pack_propagate(False)
        
        owned_legend = ctk.CTkLabel(legend_container, text="Possédé",
                                  font=ctk.CTkFont(size=11),
                                  text_color="#059669")
        owned_legend.pack(side="left", padx=(0, 20))
        
        missing_indicator = ctk.CTkFrame(legend_container, corner_radius=15, width=20, height=20, fg_color="#EF4444")
        missing_indicator.pack(side="left", padx=(0, 5))
        missing_indicator.pack_propagate(False)
        
        missing_legend = ctk.CTkLabel(legend_container, text="Manquant",
                                    font=ctk.CTkFont(size=11),
                                    text_color="#DC2626")
        missing_legend.pack(side="left", padx=(0, 20))
        
        # Aide interactive
        help_text = ctk.CTkLabel(
            legend_container,
            text="💡 Double-cliquez sur une carte pour changer son statut",
            font=ctk.CTkFont(size=10),
            text_color="#6B7280"
        )
        help_text.pack(side="right")
        
        # Boutons d'action modernisés et groupés
        button_section = ctk.CTkFrame(actions_frame, corner_radius=8, fg_color="transparent")
        button_section.pack(fill="x", padx=15, pady=(0, 15))
        
        # Groupe d'actions de modification
        modify_group = ctk.CTkFrame(button_section, corner_radius=8)
        modify_group.pack(side="left", padx=(0, 10))
        
        modify_title = ctk.CTkLabel(modify_group, text="⚡ Actions Rapides",
                                  font=ctk.CTkFont(size=11, weight="bold"))
        modify_title.pack(pady=(8, 5))
        
        modify_buttons = ctk.CTkFrame(modify_group, corner_radius=6, fg_color="transparent")
        modify_buttons.pack(padx=8, pady=(0, 8))
        
        mark_owned_btn = ctk.CTkButton(
            modify_buttons, 
            text=f"✅ Marquer possédé",
            command=self.marquer_possede,
            width=140,
            height=32,
            corner_radius=8,
            fg_color="#10B981",
            hover_color="#059669",
            font=ctk.CTkFont(size=11)
        )
        mark_owned_btn.pack(side="left", padx=(0, 5))
        
        mark_not_owned_btn = ctk.CTkButton(
            modify_buttons, 
            text=f"❌ Marquer manquant",
            command=self.marquer_non_possede,
            width=140,
            height=32,
            corner_radius=8,
            fg_color="#EF4444",
            hover_color="#DC2626",
            font=ctk.CTkFont(size=11)
        )
        mark_not_owned_btn.pack(side="left")
        
        # Groupe d'actions système
        system_group = ctk.CTkFrame(button_section, corner_radius=8)
        system_group.pack(side="right")
        
        system_title = ctk.CTkLabel(system_group, text="🔧 Système",
                                  font=ctk.CTkFont(size=11, weight="bold"))
        system_title.pack(pady=(8, 5))
        
        system_buttons = ctk.CTkFrame(system_group, corner_radius=6, fg_color="transparent")
        system_buttons.pack(padx=8, pady=(0, 8))
        
        refresh_btn = ctk.CTkButton(
            system_buttons, 
            text=f"🔄 Actualiser",
            command=self.charger_series,
            width=100,
            height=32,
            corner_radius=8,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            font=ctk.CTkFont(size=11)
        )
        refresh_btn.pack(side="left", padx=(0, 5))
        
        export_btn = ctk.CTkButton(
            system_buttons, 
            text=f"📤 Exporter",
            command=self.exporter_collection,
            width=100,
            height=32,
            corner_radius=8,
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            font=ctk.CTkFont(size=11)
        )
        export_btn.pack(side="left")
        
        # Initialiser les variables de filtre
        self.current_filter = "all"
        self.current_serie_data = []
        self.card_search_term = ""  # Terme de recherche pour les cartes
        self.selected_rarity = ""  # Rareté sélectionnée pour le filtre
        
        # Charger les séries automatiquement au démarrage
        self.charger_series()
    
    def filtrer_series(self, event=None):
        """Filtre les séries selon le texte de recherche"""
        search_text = self.search_entry.get().lower()
        
        # Vider la listbox
        self.series_listbox.delete(0, tk.END)
        
        # Récupérer toutes les séries
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.code_serie, s.nom_serie, COUNT(DISTINCT c.id) as nb_cartes,
                       COUNT(DISTINCT cr.id) as nb_raretes
                FROM series s
                LEFT JOIN cartes c ON s.id = c.serie_id
                LEFT JOIN carte_raretes cr ON c.id = cr.carte_id
                GROUP BY s.id, s.code_serie, s.nom_serie
                ORDER BY s.code_serie
            """)
            
            # Filtrer et ajouter les séries correspondantes
            for code_serie, nom_serie, nb_cartes, nb_raretes in cursor.fetchall():
                if search_text == "" or search_text in code_serie.lower() or search_text in nom_serie.lower():
                    display_text = f"{code_serie} ({nb_raretes} raretes)"
                    self.series_listbox.insert(tk.END, display_text)
            
            conn.close()
            
        except Exception as e:
            self.log(f"Erreur lors du filtrage des séries : {e}")
    
    def filtrer_cartes(self, filter_type):
        """Filtre les cartes selon le statut (all, owned, missing)"""
        self.current_filter = filter_type
        
        # Mettre à jour l'apparence des boutons de filtre
        self.filter_all_btn.configure(fg_color="#6B7280" if filter_type != "all" else "#1F2937")
        self.filter_owned_btn.configure(fg_color="#10B981" if filter_type != "owned" else "#059669")
        self.filter_missing_btn.configure(fg_color="#EF4444" if filter_type != "missing" else "#DC2626")
        
        # Recharger les cartes avec le filtre
        if hasattr(self, 'current_serie_name') and self.current_serie_name:
            self.charger_cartes_serie(self.current_serie_name)
    
    def rechercher_cartes(self, event=None):
        """Filtre les cartes selon le terme de recherche"""
        self.card_search_term = self.card_search_entry.get().lower()
        
        # Recharger les cartes avec le terme de recherche
        if hasattr(self, 'current_serie_name') and self.current_serie_name:
            self.charger_cartes_serie(self.current_serie_name)
    
    def effacer_recherche_cartes(self):
        """Efface le terme de recherche et recharge les cartes"""
        self.card_search_entry.delete(0, tk.END)
        self.card_search_term = ""
        
        # Recharger les cartes sans filtre de recherche
        if hasattr(self, 'current_serie_name') and self.current_serie_name:
            self.charger_cartes_serie(self.current_serie_name)
    
    def filtrer_par_rarete(self, selected_rarity):
        """Filtre les cartes selon la rareté sélectionnée"""
        if selected_rarity == "Toutes les raretés":
            self.selected_rarity = ""
        else:
            self.selected_rarity = selected_rarity
        
        # Recharger les cartes avec le filtre de rareté
        if hasattr(self, 'current_serie_name') and self.current_serie_name:
            self.charger_cartes_serie(self.current_serie_name)
    
    def charger_raretes_serie(self, code_serie):
        """Charge les raretés disponibles pour une série donnée"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT r.nom_rarete
                FROM series s
                JOIN cartes c ON s.id = c.serie_id
                JOIN carte_raretes cr ON c.id = cr.carte_id
                JOIN raretes r ON cr.rarete_id = r.id
                WHERE s.code_serie = ?
                ORDER BY r.nom_rarete
            """, (code_serie,))
            
            raretes = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # Mettre à jour le menu déroulant
            raretes_list = ["Toutes les raretés"] + raretes
            self.rarity_combobox.configure(values=raretes_list)
            self.rarity_combobox.set("Toutes les raretés")
            self.selected_rarity = ""
            
        except Exception as e:
            self.log(f"Erreur lors du chargement des raretés : {e}")
    
    def toggle_carte_status(self, event):
        """Bascule le statut possédé/non possédé d'une carte en double-cliquant"""
        selection = self.cartes_tree.selection()
        if not selection:
            return
        
        # Récupérer les données de la carte sélectionnée
        item = selection[0]
        values = self.cartes_tree.item(item, 'values')
        
        if len(values) >= 4:
            numero, nom, rarete, statut_actuel = values
            
            # Déterminer le nouveau statut
            if "Possédé" in statut_actuel:
                self.marquer_non_possede()
            else:
                self.marquer_possede()
    
    def exporter_collection(self):
        """Exporte la collection vers un fichier CSV"""
        try:
            from tkinter import filedialog
            import csv
            from datetime import datetime
            
            # Demander où sauvegarder
            filename = filedialog.asksaveasfilename(
                title="Exporter la collection",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialname=f"ma_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not filename:
                return
            
            # Récupérer toutes les cartes possédées
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.nom_serie, c.numero_carte, c.nom_carte, r.nom_rarete, cr.possedee
                FROM series s
                JOIN cartes c ON s.id = c.serie_id
                JOIN carte_raretes cr ON c.id = cr.carte_id
                JOIN raretes r ON cr.rarete_id = r.id
                WHERE cr.possedee = 1
                ORDER BY s.nom_serie, c.numero_carte, r.nom_rarete
            """)
            
            cartes_possedees = cursor.fetchall()
            conn.close()
            
            # Écrire le fichier CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Série', 'Numéro', 'Nom', 'Rareté', 'Statut'])
                
                for serie, numero, nom, rarete, possede in cartes_possedees:
                    writer.writerow([serie, numero, nom, rarete, 'Possédé'])
            
            messagebox.showinfo("Export réussi", f"Collection exportée vers :\n{filename}")
            self.log(f"Collection exportée vers {filename}")
            
        except Exception as e:
            messagebox.showerror("Erreur d'export", f"Erreur lors de l'export : {e}")
            self.log(f"Erreur lors de l'export : {e}")
    
    def lancer_convertisseur(self):
        """Lance l'interface du convertisseur"""
        try:
            convertisseur_path = Path(__file__).parent.parent / "convertisseur" / "Convertisseur_GUI.py"
            
            if convertisseur_path.exists():
                import subprocess
                subprocess.Popen([sys.executable, str(convertisseur_path)])
                self.log("🚀 Convertisseur lancé dans une nouvelle fenêtre")
            else:
                messagebox.showerror("Erreur", f"Convertisseur non trouvé :\n{convertisseur_path}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lancer le convertisseur :\n{e}")
    
    def importer_csv_fichier(self):
        """Importe un fichier CSV sélectionné par l'utilisateur"""
        fichier = filedialog.askopenfilename(
            title="Sélectionner un fichier CSV",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
        )
        
        if fichier:
            try:
                self.log(f"📥 Import de {Path(fichier).name}...")
                stats = self.importer.importer_csv(fichier)
                
                self.log(f"✅ Import terminé :")
                self.log(f"  ➕ Cartes ajoutées : {stats['cartes_ajoutees']}")
                self.log(f"  🔗 Liens créés : {stats['liens_crees']}")
                self.log(f"  ↻  Cartes existantes : {stats['cartes_existantes']}")
                
                if stats['erreurs'] > 0:
                    self.log(f"  ❌ Erreurs : {stats['erreurs']}")
                
                self.rafraichir_donnees()
                messagebox.showinfo("Import terminé", "Fichier CSV importé avec succès !")
                
            except Exception as e:
                self.log(f"❌ Erreur lors de l'import : {e}")
                messagebox.showerror("Erreur d'import", str(e))
    
    def importer_dossier_csv(self):
        """Importe tous les CSV du dossier temp"""
        try:
            self.log("📁 Import du dossier temp/...")
            resultats = self.importer.importer_dossier(str(TEMP_CSV_DIR))
            
            if resultats:
                self.log(f"✅ Import de {len(resultats)} fichiers terminé")
                
                fichiers_supprimes = 0
                for fichier, stats in resultats.items():
                    if 'erreur' in stats:
                        self.log(f"❌ {fichier} : {stats['erreur']}")
                    else:
                        message_stats = f"✅ {fichier} : {stats['cartes_ajoutees']} cartes, {stats['liens_crees']} liens"
                        if stats.get('fichier_supprime', False):
                            message_stats += " 🗑️ (supprimé)"
                            fichiers_supprimes += 1
                        self.log(message_stats)
                
                self.rafraichir_donnees()
                if fichiers_supprimes > 0:
                    messagebox.showinfo(
                        "Import terminé", 
                        f"{len(resultats)} fichiers importés !\n🗑️ {fichiers_supprimes} fichiers supprimés du dossier temp/"
                    )
                else:
                    messagebox.showinfo("Import terminé", f"{len(resultats)} fichiers importés !")
            else:
                self.log("❌ Aucun fichier CSV trouvé dans le dossier temp/")
                messagebox.showwarning("Aucun fichier", "Aucun fichier CSV trouvé dans le dossier temp/")
                
        except Exception as e:
            self.log(f"❌ Erreur lors de l'import : {e}")
            messagebox.showerror("Erreur d'import", str(e))
    
    def afficher_stats_detaillees(self):
        """Affiche une fenêtre avec des graphiques de statistiques détaillées"""
        try:
            # Créer une fenêtre popup moderne pour les statistiques
            stats_window = ctk.CTkToplevel(self.root)
            stats_window.title("📊 Statistiques Détaillées")
            stats_window.geometry("1200x800")
            stats_window.transient(self.root)
            stats_window.grab_set()
            
            # En-tête de la fenêtre
            header_frame = ctk.CTkFrame(stats_window, corner_radius=12, fg_color="#7C3AED")
            header_frame.pack(fill="x", padx=20, pady=20)
            
            header_title = ctk.CTkLabel(
                header_frame,
                text="📊 Statistiques Avancées de Collection",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="white"
            )
            header_title.pack(pady=15)
            
            # Frame principal avec scroll
            main_frame = ctk.CTkScrollableFrame(stats_window)
            main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            # Récupérer les données pour les graphiques
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # 1. Graphique d'activité d'ajout de cartes par mois
            cursor.execute("""
                SELECT DATE(date_ajout) as date, COUNT(*) as nb_cartes
                FROM cartes 
                WHERE date_ajout IS NOT NULL
                GROUP BY DATE(date_ajout)
                ORDER BY date_ajout
            """)
            ajout_data = cursor.fetchall()
            
            # 2. Graphique d'acquisition de cartes possédées par mois  
            cursor.execute("""
                SELECT DATE(cr.date_acquisition) as date, COUNT(*) as nb_cartes
                FROM carte_raretes cr
                WHERE cr.possedee = 1 AND cr.date_acquisition IS NOT NULL
                GROUP BY DATE(cr.date_acquisition)
                ORDER BY cr.date_acquisition
            """)
            acquisition_data = cursor.fetchall()
            
            # 3. Statistiques par série
            cursor.execute("""
                SELECT s.nom_serie, s.code_serie,
                       COUNT(DISTINCT c.id) as total_cartes,
                       COUNT(DISTINCT cr.id) as total_exemplaires,
                       SUM(CASE WHEN cr.possedee = 1 THEN 1 ELSE 0 END) as possedes
                FROM series s
                LEFT JOIN cartes c ON s.id = c.serie_id
                LEFT JOIN carte_raretes cr ON c.id = cr.carte_id
                GROUP BY s.id, s.nom_serie, s.code_serie
                ORDER BY possedes DESC
                LIMIT 10
            """)
            series_stats = cursor.fetchall()
            
            # 4. Statistiques par rareté
            cursor.execute("""
                SELECT r.nom_rarete,
                       COUNT(*) as total,
                       SUM(CASE WHEN cr.possedee = 1 THEN 1 ELSE 0 END) as possedes
                FROM carte_raretes cr
                JOIN raretes r ON cr.rarete_id = r.id
                GROUP BY r.nom_rarete
                ORDER BY possedes DESC
            """)
            rarity_stats = cursor.fetchall()
            
            conn.close()
            
            # Créer les graphiques
            self.creer_graphique_activite(main_frame, ajout_data, acquisition_data)
            self.creer_graphique_series(main_frame, series_stats)
            self.creer_graphique_raretes(main_frame, rarity_stats)
            
            # Bouton de fermeture
            close_btn = ctk.CTkButton(
                stats_window,
                text="✖ Fermer",
                command=stats_window.destroy,
                width=120,
                height=40,
                corner_radius=8,
                fg_color="#6B7280",
                hover_color="#4B5563",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            close_btn.pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'affichage des statistiques : {e}")
            self.log(f"Erreur statistiques : {e}")
    
    def afficher_cartes_manquantes(self):
        """Affiche la liste des cartes manquantes"""
        try:
            # Créer une fenêtre popup moderne
            popup = ctk.CTkToplevel(self.root)
            popup.title("🔍 Cartes Manquantes")
            popup.geometry("800x600")
            popup.transient(self.root)
            popup.grab_set()
            
            # En-tête de la fenêtre
            header_frame = ctk.CTkFrame(popup, corner_radius=12, fg_color="#DC2626")
            header_frame.pack(fill="x", padx=20, pady=20)
            
            header_title = ctk.CTkLabel(
                header_frame,
                text="🃏 Cartes Manquantes dans votre Collection",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            header_title.pack(pady=15)
            
            # Frame pour le contenu
            content_frame = ctk.CTkFrame(popup, corner_radius=12)
            content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            # Récupérer les cartes manquantes de la base de données
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.nom_serie, c.numero_carte, c.nom_carte, r.nom_rarete
                FROM series s
                JOIN cartes c ON s.id = c.serie_id
                JOIN carte_raretes cr ON c.id = cr.carte_id
                JOIN raretes r ON cr.rarete_id = r.id
                WHERE cr.possedee = 0
                ORDER BY s.nom_serie, c.numero_carte, r.nom_rarete
            """)
            
            cartes_manquantes = cursor.fetchall()
            conn.close()
            
            if not cartes_manquantes:
                # Aucune carte manquante - félicitations !
                congrats_frame = ctk.CTkFrame(content_frame, corner_radius=12, fg_color="#10B981")
                congrats_frame.pack(fill="both", expand=True, padx=15, pady=15)
                
                congrats_label = ctk.CTkLabel(
                    congrats_frame,
                    text="🎉 Félicitations !\nVotre collection est complète !",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="white"
                )
                congrats_label.pack(expand=True)
            else:
                # Affichage des statistiques
                stats_label = ctk.CTkLabel(
                    content_frame,
                    text=f"📊 {len(cartes_manquantes)} cartes manquantes au total",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#DC2626"
                )
                stats_label.pack(pady=(15, 10))
                
                # Treeview pour afficher les cartes manquantes
                tree_container = ctk.CTkFrame(content_frame, corner_radius=8)
                tree_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
                
                columns = ("Serie", "Numero", "Nom", "Rarete")
                missing_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15)
                
                # Configuration des colonnes
                missing_tree.heading("Serie", text="Série")
                missing_tree.heading("Numero", text="N°")
                missing_tree.heading("Nom", text="Nom de la carte")
                missing_tree.heading("Rarete", text="Rareté")
                
                missing_tree.column("Serie", width=180)
                missing_tree.column("Numero", width=80, anchor="center")
                missing_tree.column("Nom", width=300)
                missing_tree.column("Rarete", width=120)
                
                # Style pour les cartes manquantes
                style = ttk.Style()
                style.configure("Missing.Treeview",
                               background="#FEF2F2",
                               foreground="#7F1D1D",
                               rowheight=25)
                style.configure("Missing.Treeview.Heading",
                               background="#FEE2E2",
                               foreground="#991B1B",
                               font=("Segoe UI", 10, "bold"))
                
                missing_tree.configure(style="Missing.Treeview")
                
                # Scrollbar
                tree_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=missing_tree.yview)
                missing_tree.configure(yscrollcommand=tree_scroll.set)
                
                # Ajouter les cartes manquantes au treeview
                for serie, numero, nom, rarete in cartes_manquantes:
                    missing_tree.insert("", "end", values=(serie, numero, nom, rarete))
                
                missing_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
                tree_scroll.pack(side="right", fill="y", pady=5)
            
            # Bouton de fermeture
            close_btn = ctk.CTkButton(
                popup,
                text="✖ Fermer",
                command=popup.destroy,
                width=100,
                height=35,
                corner_radius=8,
                fg_color="#6B7280",
                hover_color="#4B5563"
            )
            close_btn.pack(pady=(0, 20))
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'affichage des cartes manquantes : {e}")
    
    def afficher_cartes_possedees(self):
        """Affiche la liste des cartes possédées"""
        try:
            # Créer une fenêtre popup moderne
            popup = ctk.CTkToplevel(self.root)
            popup.title("✅ Cartes Possédées")
            popup.geometry("800x600")
            popup.transient(self.root)
            popup.grab_set()
            
            # En-tête de la fenêtre
            header_frame = ctk.CTkFrame(popup, corner_radius=12, fg_color="#059669")
            header_frame.pack(fill="x", padx=20, pady=20)
            
            header_title = ctk.CTkLabel(
                header_frame,
                text="🎉 Cartes Possédées dans votre Collection",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            header_title.pack(pady=15)
            
            # Frame pour le contenu
            content_frame = ctk.CTkFrame(popup, corner_radius=12)
            content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            # Récupérer les cartes possédées de la base de données
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.nom_serie, c.numero_carte, c.nom_carte, r.nom_rarete
                FROM series s
                JOIN cartes c ON s.id = c.serie_id
                JOIN carte_raretes cr ON c.id = cr.carte_id
                JOIN raretes r ON cr.rarete_id = r.id
                WHERE cr.possedee = 1
                ORDER BY s.nom_serie, c.numero_carte, r.nom_rarete
            """)
            
            cartes_possedees = cursor.fetchall()
            conn.close()
            
            if not cartes_possedees:
                # Aucune carte possédée
                empty_frame = ctk.CTkFrame(content_frame, corner_radius=12, fg_color="#F59E0B")
                empty_frame.pack(fill="both", expand=True, padx=15, pady=15)
                
                empty_label = ctk.CTkLabel(
                    empty_frame,
                    text="📦 Votre collection est vide\nCommencez à ajouter des cartes !",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="white"
                )
                empty_label.pack(expand=True)
            else:
                # Affichage des statistiques
                stats_label = ctk.CTkLabel(
                    content_frame,
                    text=f"🎴 {len(cartes_possedees)} cartes possédées au total",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#059669"
                )
                stats_label.pack(pady=(15, 10))
                
                # Treeview pour afficher les cartes possédées
                tree_container = ctk.CTkFrame(content_frame, corner_radius=8)
                tree_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
                
                columns = ("Serie", "Numero", "Nom", "Rarete")
                owned_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15)
                
                # Configuration des colonnes
                owned_tree.heading("Serie", text="Série")
                owned_tree.heading("Numero", text="N°")
                owned_tree.heading("Nom", text="Nom de la carte")
                owned_tree.heading("Rarete", text="Rareté")
                
                owned_tree.column("Serie", width=180)
                owned_tree.column("Numero", width=80, anchor="center")
                owned_tree.column("Nom", width=300)
                owned_tree.column("Rarete", width=120)
                
                # Style pour les cartes possédées
                style = ttk.Style()
                style.configure("Owned.Treeview",
                               background="#F0FDF4",
                               foreground="#14532D",
                               rowheight=25)
                style.configure("Owned.Treeview.Heading",
                               background="#D1FAE5",
                               foreground="#166534",
                               font=("Segoe UI", 10, "bold"))
                
                owned_tree.configure(style="Owned.Treeview")
                
                # Scrollbar
                tree_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=owned_tree.yview)
                owned_tree.configure(yscrollcommand=tree_scroll.set)
                
                # Ajouter les cartes possédées au treeview
                for serie, numero, nom, rarete in cartes_possedees:
                    owned_tree.insert("", "end", values=(serie, numero, nom, rarete))
                
                owned_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
                tree_scroll.pack(side="right", fill="y", pady=5)
            
            # Bouton de fermeture
            close_btn = ctk.CTkButton(
                popup,
                text="✖ Fermer",
                command=popup.destroy,
                width=100,
                height=35,
                corner_radius=8,
                fg_color="#6B7280",
                hover_color="#4B5563"
            )
            close_btn.pack(pady=(0, 20))
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'affichage des cartes possédées : {e}")
    
    def afficher_tous_exemplaires(self):
        """Affiche la liste de tous les exemplaires (possédés et manquants)"""
        try:
            # Créer une fenêtre popup moderne
            popup = ctk.CTkToplevel(self.root)
            popup.title("📚 Tous les Exemplaires")
            popup.geometry("900x650")
            popup.transient(self.root)
            popup.grab_set()
            
            # En-tête de la fenêtre
            header_frame = ctk.CTkFrame(popup, corner_radius=12, fg_color="#2563EB")
            header_frame.pack(fill="x", padx=20, pady=20)
            
            header_title = ctk.CTkLabel(
                header_frame,
                text="📚 Tous les Exemplaires de votre Collection",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            header_title.pack(pady=15)
            
            # Frame pour le contenu
            content_frame = ctk.CTkFrame(popup, corner_radius=12)
            content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            # Récupérer tous les exemplaires de la base de données
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.nom_serie, c.numero_carte, c.nom_carte, r.nom_rarete, cr.possedee
                FROM series s
                JOIN cartes c ON s.id = c.serie_id
                JOIN carte_raretes cr ON c.id = cr.carte_id
                JOIN raretes r ON cr.rarete_id = r.id
                ORDER BY s.nom_serie, c.numero_carte, r.nom_rarete
            """)
            
            tous_exemplaires = cursor.fetchall()
            conn.close()
            
            if not tous_exemplaires:
                # Aucun exemplaire
                empty_frame = ctk.CTkFrame(content_frame, corner_radius=12, fg_color="#6B7280")
                empty_frame.pack(fill="both", expand=True, padx=15, pady=15)
                
                empty_label = ctk.CTkLabel(
                    empty_frame,
                    text="📦 Aucun exemplaire trouvé\nVeuillez importer des données !",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="white"
                )
                empty_label.pack(expand=True)
            else:
                # Calculer les statistiques
                total_exemplaires = len(tous_exemplaires)
                exemplaires_possedes = sum(1 for _, _, _, _, possede in tous_exemplaires if possede)
                exemplaires_manquants = total_exemplaires - exemplaires_possedes
                
                # Affichage des statistiques
                stats_frame = ctk.CTkFrame(content_frame, corner_radius=8)
                stats_frame.pack(fill="x", padx=15, pady=15)
                
                stats_container = ctk.CTkFrame(stats_frame, corner_radius=6, fg_color="transparent")
                stats_container.pack(fill="x", padx=10, pady=10)
                
                # Statistiques en ligne
                stats_container.grid_columnconfigure(0, weight=1)
                stats_container.grid_columnconfigure(1, weight=1)
                stats_container.grid_columnconfigure(2, weight=1)
                
                total_label = ctk.CTkLabel(
                    stats_container,
                    text=f"📚 Total: {total_exemplaires}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#2563EB"
                )
                total_label.grid(row=0, column=0, padx=5)
                
                owned_label = ctk.CTkLabel(
                    stats_container,
                    text=f"✅ Possédés: {exemplaires_possedes}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#059669"
                )
                owned_label.grid(row=0, column=1, padx=5)
                
                missing_label = ctk.CTkLabel(
                    stats_container,
                    text=f"❌ Manquants: {exemplaires_manquants}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#DC2626"
                )
                missing_label.grid(row=0, column=2, padx=5)
                
                # Treeview pour afficher tous les exemplaires
                tree_container = ctk.CTkFrame(content_frame, corner_radius=8)
                tree_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
                
                columns = ("Serie", "Numero", "Nom", "Rarete", "Statut")
                all_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15)
                
                # Configuration des colonnes
                all_tree.heading("Serie", text="Série")
                all_tree.heading("Numero", text="N°")
                all_tree.heading("Nom", text="Nom de la carte")
                all_tree.heading("Rarete", text="Rareté")
                all_tree.heading("Statut", text="Statut")
                
                all_tree.column("Serie", width=160)
                all_tree.column("Numero", width=70, anchor="center")
                all_tree.column("Nom", width=280)
                all_tree.column("Rarete", width=110)
                all_tree.column("Statut", width=100, anchor="center")
                
                # Style pour tous les exemplaires
                style = ttk.Style()
                style.configure("All.Treeview",
                               background="#F8FAFC",
                               foreground="#1E293B",
                               rowheight=25)
                style.configure("All.Treeview.Heading",
                               background="#E2E8F0",
                               foreground="#334155",
                               font=("Segoe UI", 10, "bold"))
                
                all_tree.configure(style="All.Treeview")
                
                # Tags pour différencier possédé/manquant
                all_tree.tag_configure("owned", background="#F0FDF4", foreground="#166534")
                all_tree.tag_configure("missing", background="#FEF2F2", foreground="#991B1B")
                
                # Scrollbar
                tree_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=all_tree.yview)
                all_tree.configure(yscrollcommand=tree_scroll.set)
                
                # Ajouter tous les exemplaires au treeview
                for serie, numero, nom, rarete, possede in tous_exemplaires:
                    if possede:
                        statut = "✅ Possédé"
                        tag = "owned"
                    else:
                        statut = "❌ Manquant"
                        tag = "missing"
                    
                    all_tree.insert("", "end", values=(serie, numero, nom, rarete, statut), tags=(tag,))
                
                all_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
                tree_scroll.pack(side="right", fill="y", pady=5)
            
            # Bouton de fermeture
            close_btn = ctk.CTkButton(
                popup,
                text="✖ Fermer",
                command=popup.destroy,
                width=100,
                height=35,
                corner_radius=8,
                fg_color="#6B7280",
                hover_color="#4B5563"
            )
            close_btn.pack(pady=(0, 20))
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'affichage de tous les exemplaires : {e}")
    
    def gerer_possession(self):
        """Interface de gestion des cartes possédées"""
        # TODO: Interface pour cocher/décocher les cartes possédées
        messagebox.showinfo("Gestion", "Interface de gestion en développement...")
    
    def rafraichir_donnees(self):
        """Met à jour toutes les données affichées"""
        try:
            # Récupérer les statistiques
            stats_series = self.db.get_stats_collection()
            
            # Calculer les statistiques globales
            total_series = len(stats_series)
            total_exemplaires = sum(s['total_exemplaires'] for s in stats_series)
            exemplaires_possedes = sum(s['possedes'] for s in stats_series)
            
            pourcentage_global = (exemplaires_possedes / total_exemplaires * 100) if total_exemplaires > 0 else 0
            cartes_manquantes = total_exemplaires - exemplaires_possedes
            
            # Compter les cartes uniques
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM cartes')
            total_cartes = cursor.fetchone()[0]
            conn.close()
            
            # Mettre à jour les labels de statistiques
            self.stats_labels['total_series'].configure(text=str(total_series))
            self.stats_labels['total_cartes'].configure(text=formater_nombre_cartes(total_cartes))
            self.stats_labels['total_exemplaires'].configure(text=formater_nombre_cartes(total_exemplaires))
            self.stats_labels['exemplaires_possedes'].configure(text=formater_nombre_cartes(exemplaires_possedes))
            self.stats_labels['cartes_manquantes'].configure(text=formater_nombre_cartes(cartes_manquantes))
            self.stats_labels['pourcentage_global'].configure(text=formater_pourcentage(pourcentage_global))
            
            # Mettre à jour le tableau des séries
            for item in self.series_tree.get_children():
                self.series_tree.delete(item)
            
            for stats in stats_series:
                self.series_tree.insert("", tk.END, values=(
                    stats['code_serie'],
                    stats['nom_serie'],
                    stats['total_exemplaires'],
                    stats['possedes'],
                    formater_pourcentage(stats['pourcentage_collection'])
                ))
            
            # Barre de statut
            self.stats_var.set(f"{total_series} series • {total_cartes} cartes • {exemplaires_possedes}/{total_exemplaires} exemplaires ({pourcentage_global:.1f}%)")
            
            # Charger les séries dans l'onglet collection
            self.charger_series()
            
            # Actualiser le graphique de complétion
            if hasattr(self, 'chart_wrapper'):
                self.actualiser_graphique_completion()
            
        except Exception as e:
            self.log(f"Erreur lors de la mise à jour : {e}")
    
    def rafraichir_donnees_sans_series(self):
        """Met à jour les statistiques sans recharger la liste des séries"""
        try:
            # Récupérer les statistiques
            stats_series = self.db.get_stats_collection()
            
            # Calculer les statistiques globales
            total_series = len(stats_series)
            total_exemplaires = sum(s['total_exemplaires'] for s in stats_series)
            exemplaires_possedes = sum(s['possedes'] for s in stats_series)
            
            pourcentage_global = (exemplaires_possedes / total_exemplaires * 100) if total_exemplaires > 0 else 0
            cartes_manquantes = total_exemplaires - exemplaires_possedes
            
            # Compter les cartes uniques
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM cartes')
            total_cartes = cursor.fetchone()[0]
            conn.close()
            
            # Mettre à jour les labels de statistiques
            self.stats_labels['total_series'].configure(text=str(total_series))
            self.stats_labels['total_cartes'].configure(text=formater_nombre_cartes(total_cartes))
            self.stats_labels['total_exemplaires'].configure(text=formater_nombre_cartes(total_exemplaires))
            self.stats_labels['exemplaires_possedes'].configure(text=formater_nombre_cartes(exemplaires_possedes))
            self.stats_labels['cartes_manquantes'].configure(text=formater_nombre_cartes(cartes_manquantes))
            self.stats_labels['pourcentage_global'].configure(text=formater_pourcentage(pourcentage_global))
            
            # Mettre à jour le tableau des séries
            for item in self.series_tree.get_children():
                self.series_tree.delete(item)
            
            for stats in stats_series:
                self.series_tree.insert("", tk.END, values=(
                    stats['code_serie'],
                    stats['nom_serie'],
                    stats['total_exemplaires'],
                    stats['possedes'],
                    formater_pourcentage(stats['pourcentage_collection'])
                ))
            
            # Barre de statut
            self.stats_var.set(f"{total_series} series • {total_cartes} cartes • {exemplaires_possedes}/{total_exemplaires} exemplaires ({pourcentage_global:.1f}%)")
            
        except Exception as e:
            self.log(f"Erreur lors de la mise à jour : {e}")
    
    def log(self, message):
        """Ajoute un message au journal"""
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
        print(message)  # Aussi dans la console
    
    def vider_journal(self):
        """Vide le contenu du journal d'activité"""
        if hasattr(self, 'log_text'):
            self.log_text.delete(1.0, tk.END)
            self.log("📋 Journal vidé")
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def charger_series(self):
        """Charge la liste des séries dans la listbox"""
        try:
            self.series_listbox.delete(0, tk.END)
            
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.code_serie, s.nom_serie, COUNT(DISTINCT c.id) as nb_cartes,
                       COUNT(DISTINCT cr.id) as nb_raretes
                FROM series s
                LEFT JOIN cartes c ON s.id = c.serie_id
                LEFT JOIN carte_raretes cr ON c.id = cr.carte_id
                GROUP BY s.id, s.code_serie, s.nom_serie
                ORDER BY s.code_serie
            """)
            
            for code_serie, nom_serie, nb_cartes, nb_raretes in cursor.fetchall():
                display_text = f"{code_serie} ({nb_raretes} raretes)"
                self.series_listbox.insert(tk.END, display_text)
            
            conn.close()
            self.log("Series chargees avec succes")
            
        except Exception as e:
            self.log(f"Erreur lors du chargement des series : {e}")
    
    def on_serie_select(self, event):
        """Appelée quand une série est sélectionnée"""
        selection = self.series_listbox.curselection()
        if not selection:
            return
            
        # Extraire le code de la série du texte affiché
        selected_text = self.series_listbox.get(selection[0])
        serie_code = selected_text.split(" (")[0]  # Enlever le nombre de raretés
        
        # Charger les raretés disponibles pour cette série
        self.charger_raretes_serie(serie_code)
        
        self.charger_cartes_serie(serie_code)
    
    def charger_cartes_serie(self, code_serie):
        """Charge les cartes d'une série donnée avec filtrage"""
        try:
            # Sauvegarder le code de la série actuelle
            self.current_serie_name = code_serie
            
            # Réinitialiser les sélections
            self.selected_cards.clear()
            self.all_selected = False
            self.select_all_btn.configure(text="☑️ Tout sélectionner")
            self.update_selection_count()
            
            # Vider le treeview
            for item in self.cartes_tree.get_children():
                self.cartes_tree.delete(item)
            
            # Compter les cartes pour les statistiques
            total_cartes = 0
            cartes_possedees = 0
            cartes_affichees = 0
            
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Récupérer l'ID de la série pour les opérations de sélection
            cursor.execute("SELECT id FROM series WHERE code_serie = ?", (code_serie,))
            serie_result = cursor.fetchone()
            if serie_result:
                self.current_serie_id = serie_result[0]
            else:
                self.log(f"Erreur : Série {code_serie} non trouvée")
                conn.close()
                return
            
            # Construire la requête selon le filtre
            base_query = """
                SELECT c.numero_carte, c.nom_carte, r.nom_rarete, 
                       cr.possedee, cr.id as carte_rarete_id
                FROM series s
                JOIN cartes c ON s.id = c.serie_id
                JOIN carte_raretes cr ON c.id = cr.carte_id
                JOIN raretes r ON cr.rarete_id = r.id
                WHERE s.code_serie = ?
            """
            
            # Paramètres pour la requête
            query_params = [code_serie]
            
            # Ajouter le filtre selon la sélection
            if self.current_filter == "owned":
                base_query += " AND cr.possedee = 1"
            elif self.current_filter == "missing":
                base_query += " AND cr.possedee = 0"
            
            # Ajouter le filtre de recherche par nom ou numéro de carte
            if hasattr(self, 'card_search_term') and self.card_search_term:
                # Vérifier si le terme de recherche est un numéro (contient uniquement des chiffres)
                if self.card_search_term.isdigit():
                    # Recherche par numéro de carte
                    base_query += " AND c.numero_carte LIKE ?"
                    query_params.append(f"%{self.card_search_term}%")
                else:
                    # Recherche par nom de carte ou combinaison nom/numéro
                    base_query += " AND (LOWER(c.nom_carte) LIKE ? OR c.numero_carte LIKE ?)"
                    query_params.append(f"%{self.card_search_term}%")
                    query_params.append(f"%{self.card_search_term}%")
            
            # Ajouter le filtre par rareté
            if hasattr(self, 'selected_rarity') and self.selected_rarity:
                base_query += " AND r.nom_rarete = ?"
                query_params.append(self.selected_rarity)
            
            base_query += " ORDER BY c.numero_carte, r.nom_rarete"
            
            cursor.execute(base_query, query_params)
            cartes_filtrees = cursor.fetchall()
            
            # Récupérer aussi le total pour les statistiques et le nom complet
            cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN cr.possedee = 1 THEN 1 ELSE 0 END) as possedees,
                       s.nom_serie
                FROM series s
                JOIN cartes c ON s.id = c.serie_id
                JOIN carte_raretes cr ON c.id = cr.carte_id
                WHERE s.code_serie = ?
                GROUP BY s.nom_serie
            """, (code_serie,))
            
            stats_result = cursor.fetchone()
            total_cartes = stats_result[0] if stats_result else 0
            cartes_possedees = stats_result[1] if stats_result else 0
            nom_serie_complet = stats_result[2] if stats_result else code_serie
            
            # Sauvegarder les données pour d'autres opérations
            self.current_serie_data = cartes_filtrees
            
            # Afficher les cartes selon le filtre
            for numero, nom, rarete, possedee_bool, cr_id in cartes_filtrees:
                cartes_affichees += 1
                
                # Créer un affichage visuel moderne
                if possedee_bool:
                    possede_display = "✅ Possédé"
                    tag_style = "owned"
                else:
                    possede_display = "❌ Manquant"
                    tag_style = "not_owned"
                
                # Insérer selon le mode actuel
                if self.selection_mode_active:
                    # Mode sélection : ajouter la colonne avec cercle vide
                    item = self.cartes_tree.insert("", tk.END, 
                                                   values=("⭕", numero, nom, rarete, possede_display),
                                                   tags=(cr_id, tag_style))
                else:
                    # Mode normal : sans colonne de sélection
                    item = self.cartes_tree.insert("", tk.END, 
                                                   values=(numero, nom, rarete, possede_display),
                                                   tags=(cr_id, tag_style))
            
            conn.close()
            
            # Mettre à jour les statistiques de la série
            pourcentage = (cartes_possedees / total_cartes * 100) if total_cartes > 0 else 0
            
            # Mise à jour du titre avec statistiques
            filter_info = ""
            if self.current_filter == "owned":
                filter_info = " [Possédées uniquement]"
            elif self.current_filter == "missing":
                filter_info = " [Manquantes uniquement]"
            
            # Ajouter l'info de recherche si active
            search_info = ""
            if hasattr(self, 'card_search_term') and self.card_search_term:
                if self.card_search_term.isdigit():
                    search_info = f" [Recherche N°: '{self.card_search_term}']"
                else:
                    search_info = f" [Recherche: '{self.card_search_term}']"
            
            # Ajouter l'info de filtre par rareté si active
            rarity_info = ""
            if hasattr(self, 'selected_rarity') and self.selected_rarity:
                rarity_info = f" [Rareté: {self.selected_rarity}]"
            
            self.serie_info_label.configure(
                text=f"🎯 {nom_serie_complet}{filter_info}{search_info}{rarity_info}\n"
                     f"📊 {cartes_possedees}/{total_cartes} possédées ({pourcentage:.1f}%) • "
                     f"Affichées: {cartes_affichees}"
            )
            
            # Mettre à jour la barre de progression
            self.serie_progress_bar.set(pourcentage / 100)
            
            # Mettre à jour les statistiques rapides dans l'en-tête
            cartes_manquantes = total_cartes - cartes_possedees
            self.quick_stats_label.configure(
                text=f"📚 {total_cartes} cartes • ✅ {cartes_possedees} possédées • ❌ {cartes_manquantes} manquantes"
            )
            
            self.log(f"✅ {code_serie}: {cartes_affichees} cartes affichées (filtre: {self.current_filter})")
            
        except Exception as e:
            self.log(f"Erreur lors du chargement des cartes : {e}")
    
    def marquer_possede(self):
        """Marque les cartes sélectionnées comme possédées"""
        self._modifier_possession(True)
    
    def marquer_non_possede(self):
        """Marque les cartes sélectionnées comme non possédées"""
        self._modifier_possession(False)
    
    def _modifier_possession(self, possede):
        """Modifie le statut de possession des cartes sélectionnées"""
        selected_items = self.cartes_tree.selection()
        if not selected_items:
            messagebox.showwarning("Attention", "Veuillez selectionner une ou plusieurs cartes")
            return
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cartes_modifiees = 0
            for item in selected_items:
                # Récupérer l'ID de carte_rarete depuis les tags
                cr_id = self.cartes_tree.item(item)['tags'][0]
                cursor.execute("""
                    UPDATE carte_raretes 
                    SET possedee = ? 
                    WHERE id = ?
                """, (1 if possede else 0, cr_id))
                cartes_modifiees += 1
            
            conn.commit()
            conn.close()
            
            status = "possedees" if possede else "non possedees"
            self.log(f"{cartes_modifiees} carte(s) marquee(s) comme {status}")
            
            # Sauvegarder la sélection actuelle avant de rafraîchir
            current_selection = None
            selection = self.series_listbox.curselection()
            if selection:
                selected_text = self.series_listbox.get(selection[0])
                current_selection = selected_text.split(" (")[0]
            
            # Rafraîchir les statistiques d'abord
            self.rafraichir_donnees_sans_series()
            
            # Puis recharger l'affichage de la série courante
            if current_selection:
                # Sauvegarder les éléments sélectionnés
                selected_items_values = []
                for item in selected_items:
                    values = self.cartes_tree.item(item)['values']
                    if len(values) >= 3:  # numero, nom, rarete
                        selected_items_values.append((values[0], values[1], values[2]))
                
                # Recharger après un délai minimal
                def recharger_et_reselectionner():
                    self.charger_cartes_serie(current_selection)
                    # Reselectionner les éléments
                    for child in self.cartes_tree.get_children():
                        values = self.cartes_tree.item(child)['values']
                        if len(values) >= 3:
                            item_key = (values[0], values[1], values[2])
                            if item_key in selected_items_values:
                                self.cartes_tree.selection_add(child)
                
                self.root.after(100, recharger_et_reselectionner)
            
        except Exception as e:
            self.log(f"Erreur lors de la modification : {e}")
            messagebox.showerror("Erreur", f"Impossible de modifier les cartes :\n{e}")
    
    def creer_graphique_activite(self, parent, ajout_data, acquisition_data):
        """Crée le graphique d'activité d'ajout et d'acquisition de cartes"""
        try:
            # Frame pour le graphique d'activité
            activity_frame = ctk.CTkFrame(parent, corner_radius=12)
            activity_frame.pack(fill="x", pady=(0, 20))
            
            title_label = ctk.CTkLabel(
                activity_frame,
                text="Activite d'Ajout et d'Acquisition de Cartes",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            title_label.pack(pady=(15, 10))
            
            # Nettoyer les anciens widgets s'ils existent
            for widget in activity_frame.winfo_children():
                if widget != title_label:
                    widget.destroy()
            
            # Créer la figure matplotlib avec backend non-interactif
            plt.close('all')  # Fermer toutes les figures existantes
            fig, ax = plt.subplots(figsize=(12, 6))
            fig.patch.set_facecolor('#F8F9FA')
            ax.set_facecolor('#FFFFFF')
            
            if ajout_data or acquisition_data:
                # Traiter les données d'ajout
                if ajout_data:
                    dates_ajout = [datetime.strptime(row[0], '%Y-%m-%d').date() for row in ajout_data]
                    counts_ajout = [row[1] for row in ajout_data]
                    ax.plot(dates_ajout, counts_ajout, marker='o', linewidth=2, 
                           color='#3B82F6', label='Cartes ajoutees en base', markersize=6)
                
                # Traiter les données d'acquisition
                if acquisition_data:
                    dates_acq = [datetime.strptime(row[0], '%Y-%m-%d').date() for row in acquisition_data]
                    counts_acq = [row[1] for row in acquisition_data]
                    ax.plot(dates_acq, counts_acq, marker='s', linewidth=2, 
                           color='#10B981', label='Cartes acquises/possedees', markersize=6)
                
                ax.set_xlabel('Date', fontsize=12)
                ax.set_ylabel('Nombre de cartes', fontsize=12)
                ax.legend(fontsize=11)
                ax.grid(True, alpha=0.3)
                
                # Formatage des dates sur l'axe X
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                ax.xaxis.set_major_locator(mdates.MonthLocator())
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            else:
                ax.text(0.5, 0.5, 'Aucune donnee d\'activite disponible', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
            
            plt.tight_layout()
            
            # Intégrer le graphique dans l'interface
            canvas = FigureCanvasTkAgg(fig, activity_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))
            
        except Exception as e:
            # Nettoyer en cas d'erreur
            plt.close('all')
            self.log(f"Erreur création graphique activité : {e}")
    
    def creer_graphique_series(self, parent, series_stats):
        """Crée le graphique de répartition par séries"""
        try:
            # Frame pour le graphique par séries
            series_frame = ctk.CTkFrame(parent, corner_radius=12)
            series_frame.pack(fill="x", pady=(0, 20))
            
            title_label = ctk.CTkLabel(
                series_frame,
                text="Top 10 des Series par Nombre de Cartes Possedees",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            title_label.pack(pady=(15, 10))
            
            # Nettoyer les anciens widgets s'ils existent
            for widget in series_frame.winfo_children():
                if widget != title_label:
                    widget.destroy()
            
            # Créer la figure matplotlib avec backend non-interactif
            plt.close('all')  # Fermer toutes les figures existantes
            fig, ax = plt.subplots(figsize=(12, 8))
            fig.patch.set_facecolor('#F8F9FA')
            ax.set_facecolor('#FFFFFF')
            
            if series_stats:
                series_names = [f"{row[1]}\n({row[4]}/{row[3]})" for row in series_stats]
                possedes = [row[4] for row in series_stats]
                totaux = [row[3] for row in series_stats]
                
                # Créer un graphique en barres horizontales
                y_pos = np.arange(len(series_names))
                bars1 = ax.barh(y_pos, possedes, color='#10B981', alpha=0.8, label='Possédées')
                bars2 = ax.barh(y_pos, [t-p for t, p in zip(totaux, possedes)], 
                               left=possedes, color='#EF4444', alpha=0.6, label='Manquantes')
                
                ax.set_yticks(y_pos)
                ax.set_yticklabels(series_names, fontsize=10)
                ax.set_xlabel('Nombre de cartes', fontsize=12)
                ax.legend(fontsize=11)
                ax.grid(True, alpha=0.3, axis='x')
                
                # Ajouter les pourcentages sur les barres
                for i, (p, t) in enumerate(zip(possedes, totaux)):
                    if t > 0:
                        percentage = (p / t) * 100
                        ax.text(p + (t-p)/2, i, f'{percentage:.1f}%', 
                               ha='center', va='center', fontweight='bold', color='white')
            else:
                ax.text(0.5, 0.5, 'Aucune donnée de série disponible', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
            
            plt.tight_layout()
            
            # Intégrer le graphique dans l'interface
            canvas = FigureCanvasTkAgg(fig, series_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))
            
        except Exception as e:
            # Nettoyer en cas d'erreur
            plt.close('all')
            self.log(f"Erreur création graphique séries : {e}")
    
    def creer_graphique_raretes(self, parent, rarity_stats):
        """Crée le graphique de répartition par raretés"""
        try:
            # Frame pour le graphique par raretés
            rarity_frame = ctk.CTkFrame(parent, corner_radius=12)
            rarity_frame.pack(fill="x", pady=(0, 20))
            
            title_label = ctk.CTkLabel(
                rarity_frame,
                text="Repartition par Raretes",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            title_label.pack(pady=(15, 10))
            
            # Nettoyer les anciens widgets s'ils existent
            for widget in rarity_frame.winfo_children():
                if widget != title_label:
                    widget.destroy()
            
            # Créer la figure matplotlib avec deux sous-graphiques et backend non-interactif
            plt.close('all')  # Fermer toutes les figures existantes
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            fig.patch.set_facecolor('#F8F9FA')
            
            if rarity_stats:
                rarity_names = [row[0] for row in rarity_stats]
                totaux = [row[1] for row in rarity_stats]
                possedes = [row[2] for row in rarity_stats]
                
                # Graphique en secteurs pour les totaux
                colors1 = plt.cm.Set3(np.linspace(0, 1, len(rarity_names)))
                ax1.pie(totaux, labels=rarity_names, autopct='%1.1f%%', colors=colors1, startangle=90)
                ax1.set_title('Repartition Totale par Rarete', fontsize=12, fontweight='bold')
                
                # Graphique en barres pour comparaison possédé/total
                x_pos = np.arange(len(rarity_names))
                width = 0.35
                
                ax2.bar(x_pos - width/2, possedes, width, label='Possedees', color='#10B981', alpha=0.8)
                ax2.bar(x_pos + width/2, totaux, width, label='Total', color='#6B7280', alpha=0.6)
                
                ax2.set_xlabel('Raretes', fontsize=11)
                ax2.set_ylabel('Nombre de cartes', fontsize=11)
                ax2.set_title('Possedees vs Total', fontsize=12, fontweight='bold')
                ax2.set_xticks(x_pos)
                ax2.set_xticklabels(rarity_names, rotation=45, ha='right')
                ax2.legend()
                ax2.grid(True, alpha=0.3, axis='y')
            else:
                ax1.text(0.5, 0.5, 'Aucune donnee\nde rarete disponible', 
                        ha='center', va='center', transform=ax1.transAxes, fontsize=12)
                ax2.text(0.5, 0.5, 'Aucune donnee\nde rarete disponible', 
                        ha='center', va='center', transform=ax2.transAxes, fontsize=12)
            
            plt.tight_layout()
            
            # Intégrer le graphique dans l'interface
            canvas = FigureCanvasTkAgg(fig, rarity_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))
            
        except Exception as e:
            # Nettoyer en cas d'erreur
            plt.close('all')
            self.log(f"Erreur création graphique raretés : {e}")
    
    def creer_graphique_evolution_temporelle(self, parent):
        """Crée le graphique d'évolution temporelle de la collection"""
        try:
            # Frame pour le graphique d'évolution
            evolution_frame = ctk.CTkFrame(parent, corner_radius=12)
            evolution_frame.pack(fill="x", pady=(0, 20))
            
            title_label = ctk.CTkLabel(
                evolution_frame,
                text="Evolution Temporelle de la Collection",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            title_label.pack(pady=(15, 10))
            
            # Récupérer les données d'évolution
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Données cumulatives de la collection
            cursor.execute("""
                WITH RECURSIVE dates AS (
                    SELECT MIN(date(date_ajout)) as date_point
                    FROM cartes 
                    WHERE date_ajout IS NOT NULL
                    UNION ALL
                    SELECT date(date_point, '+1 day')
                    FROM dates
                    WHERE date_point < date('now')
                ),
                daily_totals AS (
                    SELECT d.date_point,
                           COUNT(cr.id) as nouvelles_cartes,
                           (SELECT COUNT(DISTINCT cr2.id) FROM carte_raretes cr2 
                            JOIN cartes c2 ON cr2.carte_id = c2.id
                            WHERE date(c2.date_ajout) <= d.date_point 
                            AND c2.date_ajout IS NOT NULL) as total_cumule
                    FROM dates d
                    LEFT JOIN carte_raretes cr ON cr.carte_id IN (
                        SELECT c.id FROM cartes c WHERE date(c.date_ajout) = d.date_point
                    )
                    GROUP BY d.date_point
                    HAVING total_cumule > 0
                )
                SELECT date_point, nouvelles_cartes, total_cumule
                FROM daily_totals
                ORDER BY date_point
            """)
            
            evolution_data = cursor.fetchall()
            
            # Données de possession (cartes marquées comme possédées)
            cursor.execute("""
                WITH RECURSIVE dates AS (
                    SELECT MIN(date(date_acquisition)) as date_point
                    FROM carte_raretes 
                    WHERE date_acquisition IS NOT NULL AND possedee = 1
                    UNION ALL
                    SELECT date(date_point, '+1 day')
                    FROM dates
                    WHERE date_point < date('now')
                ),
                daily_owned AS (
                    SELECT d.date_point,
                           COUNT(cr.id) as nouvelles_possedees,
                           (SELECT COUNT(*) FROM carte_raretes cr2 
                            WHERE date(cr2.date_acquisition) <= d.date_point 
                            AND cr2.possedee = 1 AND cr2.date_acquisition IS NOT NULL) as total_possedees
                    FROM dates d
                    LEFT JOIN carte_raretes cr ON date(cr.date_acquisition) = d.date_point AND cr.possedee = 1
                    GROUP BY d.date_point
                    HAVING total_possedees > 0
                )
                SELECT date_point, nouvelles_possedees, total_possedees
                FROM daily_owned
                ORDER BY date_point
            """)
            
            possession_data = cursor.fetchall()
            conn.close()
            
            # Nettoyer les anciens widgets s'ils existent
            for widget in evolution_frame.winfo_children():
                if widget != title_label:
                    widget.destroy()
            
            # Créer la figure matplotlib
            plt.close('all')
            fig, ax = plt.subplots(figsize=(14, 8))
            fig.patch.set_facecolor('#F8FAFC')
            ax.set_facecolor('#FFFFFF')
            
            if evolution_data or possession_data:
                # Tracer l'évolution du total de cartes ajoutées
                if evolution_data:
                    dates_evo = [datetime.strptime(row[0], '%Y-%m-%d').date() for row in evolution_data]
                    totaux_cumules = [row[2] for row in evolution_data]
                    
                    ax.plot(dates_evo, totaux_cumules, marker='o', linewidth=3, 
                           color='#3B82F6', label='Total cartes en base', markersize=4, alpha=0.8)
                    ax.fill_between(dates_evo, totaux_cumules, alpha=0.2, color='#3B82F6')
                
                # Tracer l'évolution des cartes possédées
                if possession_data:
                    dates_poss = [datetime.strptime(row[0], '%Y-%m-%d').date() for row in possession_data]
                    totaux_possedes = [row[2] for row in possession_data]
                    
                    ax.plot(dates_poss, totaux_possedes, marker='s', linewidth=3,
                           color='#10B981', label='Total cartes possedees', markersize=4, alpha=0.8)
                    ax.fill_between(dates_poss, totaux_possedes, alpha=0.2, color='#10B981')
                
                # Configuration des axes
                ax.set_xlabel('Date', fontsize=13, fontweight='bold', color='#374151')
                ax.set_ylabel('Nombre de cartes', fontsize=13, fontweight='bold', color='#374151')
                ax.legend(fontsize=12, loc='upper left')
                ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
                
                # Formatage moderne des dates
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
                
                # Style moderne
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#E5E7EB')
                ax.spines['bottom'].set_color('#E5E7EB')
                
                # Titre avec style
                ax.set_title('Croissance de la Collection au Fil du Temps', 
                            fontsize=16, fontweight='bold', color='#1F2937', pad=20)
            else:
                ax.text(0.5, 0.5, 'Aucune donnee temporelle disponible', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
            
            plt.tight_layout()
            
            # Intégrer le graphique dans l'interface
            canvas = FigureCanvasTkAgg(fig, evolution_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))
            
        except Exception as e:
            plt.close('all')
            self.log(f"Erreur création graphique évolution : {e}")
    
    def creer_heatmap_completion(self, parent):
        """Crée une heatmap de complétion Série x Rareté"""
        try:
            # Frame pour la heatmap
            heatmap_frame = ctk.CTkFrame(parent, corner_radius=12)
            heatmap_frame.pack(fill="x", pady=(0, 20))
            
            title_label = ctk.CTkLabel(
                heatmap_frame,
                text="Heatmap de Completion: Series x Raretes",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            title_label.pack(pady=(15, 10))
            
            # Récupérer les données pour la heatmap
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.code_serie, r.nom_rarete,
                       COUNT(cr.id) as total_exemplaires,
                       SUM(CASE WHEN cr.possedee = 1 THEN 1 ELSE 0 END) as possedes,
                       CASE WHEN COUNT(cr.id) > 0 
                            THEN ROUND((CAST(SUM(CASE WHEN cr.possedee = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(cr.id)) * 100, 1)
                            ELSE 0 END as pourcentage
                FROM series s
                CROSS JOIN raretes r
                LEFT JOIN cartes c ON s.id = c.serie_id
                LEFT JOIN carte_raretes cr ON c.id = cr.carte_id AND EXISTS (
                    SELECT 1 FROM carte_raretes cr2 
                    JOIN cartes c2 ON cr2.carte_id = c2.id 
                    JOIN series s2 ON c2.serie_id = s2.id 
                    WHERE cr2.carte_id = c.id AND s2.id = s.id AND cr2.rarete = r.nom_rarete
                )
                GROUP BY s.id, s.code_serie, r.id, r.nom_rarete
                HAVING total_exemplaires > 0
                ORDER BY s.code_serie, r.nom_rarete
            """)
            
            heatmap_data = cursor.fetchall()
            conn.close()
            
            # Nettoyer les anciens widgets
            for widget in heatmap_frame.winfo_children():
                if widget != title_label:
                    widget.destroy()
            
            # Créer la figure matplotlib
            plt.close('all')
            fig, ax = plt.subplots(figsize=(16, 10))
            fig.patch.set_facecolor('#F8FAFC')
            
            if heatmap_data:
                # Organiser les données en matrice
                series_set = sorted(list(set([row[0] for row in heatmap_data])))
                raretes_set = sorted(list(set([row[1] for row in heatmap_data])))
                
                # Créer la matrice de pourcentages
                matrix = np.zeros((len(raretes_set), len(series_set)))
                
                for row in heatmap_data:
                    serie_idx = series_set.index(row[0])
                    rarete_idx = raretes_set.index(row[1])
                    matrix[rarete_idx, serie_idx] = row[4]  # pourcentage
                
                # Créer la heatmap avec une palette de couleurs moderne
                im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
                
                # Configuration des axes
                ax.set_xticks(np.arange(len(series_set)))
                ax.set_yticks(np.arange(len(raretes_set)))
                ax.set_xticklabels(series_set, rotation=45, ha='right', fontsize=11)
                ax.set_yticklabels(raretes_set, fontsize=11)
                
                # Ajouter les valeurs dans chaque cellule
                for i in range(len(raretes_set)):
                    for j in range(len(series_set)):
                        value = matrix[i, j]
                        if value > 0:
                            color = 'white' if value < 50 else 'black'
                            ax.text(j, i, f'{value:.0f}%', ha='center', va='center',
                                   color=color, fontweight='bold', fontsize=9)
                
                # Ajouter une barre de couleur
                cbar = plt.colorbar(im, ax=ax, shrink=0.8)
                cbar.set_label('Taux de Completion (%)', rotation=270, labelpad=20, fontsize=12)
                
                # Titre et labels
                ax.set_title('Completion par Serie et Rarete', 
                            fontsize=16, fontweight='bold', color='#1F2937', pad=20)
                ax.set_xlabel('Series', fontsize=13, fontweight='bold', color='#374151')
                ax.set_ylabel('Raretes', fontsize=13, fontweight='bold', color='#374151')
                
                # Style moderne
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                
            else:
                ax.text(0.5, 0.5, 'Aucune donnee pour la heatmap disponible', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=14)
            
            plt.tight_layout()
            
            # Intégrer le graphique dans l'interface
            canvas = FigureCanvasTkAgg(fig, heatmap_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))
            
        except Exception as e:
            plt.close('all')
            self.log(f"Erreur création heatmap : {e}")
    
    def creer_graphique_completion_series(self):
        """Crée le graphique moderne de complétion des séries dans l'onglet Vue d'ensemble"""
        try:
            # Récupérer les données de complétion des séries
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.code_serie, s.nom_serie,
                       COUNT(DISTINCT cr.id) as total_exemplaires,
                       SUM(CASE WHEN cr.possedee = 1 THEN 1 ELSE 0 END) as possedes
                FROM series s
                LEFT JOIN cartes c ON s.id = c.serie_id
                LEFT JOIN carte_raretes cr ON c.id = cr.carte_id
                WHERE cr.id IS NOT NULL
                GROUP BY s.id, s.code_serie, s.nom_serie
                HAVING total_exemplaires > 0
                ORDER BY (CAST(SUM(CASE WHEN cr.possedee = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(DISTINCT cr.id)) DESC
                LIMIT 15
            """)
            
            series_data = cursor.fetchall()
            conn.close()
            
            if series_data:
                # Préparer les données
                codes_series = [row[0] for row in series_data]
                pourcentages = [(row[3] / row[2]) * 100 if row[2] > 0 else 0 for row in series_data]
                possedes = [row[3] for row in series_data]
                totaux = [row[2] for row in series_data]
                
                # Créer la figure matplotlib avec un design moderne
                fig, ax = plt.subplots(figsize=(14, 8))
                fig.patch.set_facecolor('#F8FAFC')
                ax.set_facecolor('#FFFFFF')
                
                # Créer des couleurs dégradées modernes
                colors = []
                for pct in pourcentages:
                    if pct >= 80:
                        colors.append('#10B981')  # Vert pour complétion élevée
                    elif pct >= 50:
                        colors.append('#F59E0B')  # Orange pour complétion moyenne
                    elif pct >= 20:
                        colors.append('#EF4444')  # Rouge pour complétion faible
                    else:
                        colors.append('#6B7280')  # Gris pour très faible complétion
                
                # Créer le graphique en barres verticales moderne
                x_pos = np.arange(len(codes_series))
                bars = ax.bar(x_pos, pourcentages, color=colors, alpha=0.8, width=0.7)
                
                # Ajouter des effets visuels modernes
                for i, (bar, pct, poss, total) in enumerate(zip(bars, pourcentages, possedes, totaux)):
                    # Gradient effect simulé avec des barres superposées
                    ax.bar(i, pct, color=colors[i], alpha=0.3, width=0.7)
                    
                    # Ajouter le texte de pourcentage au-dessus de la barre
                    ax.text(i, pct + 2, f'{pct:.1f}%', ha='center', va='bottom', 
                           fontweight='bold', color=colors[i], fontsize=11)
                    
                    # Ajouter le nombre de cartes à l'intérieur de la barre si elle est assez haute
                    if pct > 10:
                        ax.text(i, pct/2, f'{poss}/{total}', ha='center', va='center', 
                               fontsize=9, color='white', fontweight='bold')
                    else:
                        # Sinon au-dessus
                        ax.text(i, pct + 8, f'{poss}/{total}', ha='center', va='bottom', 
                               fontsize=9, color='#6B7280')
                
                # Configuration des axes avec un style moderne
                ax.set_xticks(x_pos)
                ax.set_xticklabels(codes_series, fontsize=12, fontweight='bold', rotation=45, ha='right')
                ax.set_ylabel('Taux de Complétion (%)', fontsize=13, fontweight='bold', color='#374151')
                ax.set_ylim(0, 110)
                
                # Grille moderne et subtile
                ax.grid(True, alpha=0.2, axis='y', linestyle='-', linewidth=0.8)
                ax.set_axisbelow(True)
                
                # Ligne de référence à 100%
                ax.axhline(y=100, color='#10B981', linestyle='--', alpha=0.5, linewidth=2)
                
                # Supprimer les bordures pour un look plus moderne
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#E5E7EB')
                ax.spines['bottom'].set_color('#E5E7EB')
                
                # Titre avec style moderne
                ax.set_title('Progression de Collection par Série', 
                            fontsize=16, fontweight='bold', color='#1F2937', pad=20)
                
                plt.tight_layout()
                
            else:
                # Cas où il n'y a pas de données
                fig, ax = plt.subplots(figsize=(14, 6))
                fig.patch.set_facecolor('#F8FAFC')
                ax.set_facecolor('#FFFFFF')
                ax.text(0.5, 0.5, 'Aucune donnée de série disponible\n\nImportez des cartes pour voir les statistiques', 
                       ha='center', va='center', transform=ax.transAxes, 
                       fontsize=16, color='#6B7280', fontweight='bold')
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
            
            # Nettoyer le widget existant s'il y en a un
            for widget in self.chart_wrapper.winfo_children():
                widget.destroy()
            
            # Nettoyer l'ancien canvas s'il existe
            if hasattr(self, 'completion_canvas'):
                try:
                    self.completion_canvas.get_tk_widget().destroy()
                    plt.close(self.completion_canvas.figure)
                except:
                    pass
            
            # Intégrer le graphique dans l'interface CustomTkinter
            canvas = FigureCanvasTkAgg(fig, self.chart_wrapper)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
            # Stocker la référence pour pouvoir l'actualiser
            self.completion_canvas = canvas
            
            # Fermer la figure pour libérer la mémoire
            plt.close(fig)
            
        except Exception as e:
            self.log(f"Erreur création graphique complétion : {e}")
            # Nettoyer les widgets existants
            for widget in self.chart_wrapper.winfo_children():
                widget.destroy()
            # Afficher un message d'erreur dans le container
            error_label = ctk.CTkLabel(
                self.chart_wrapper,
                text=f"Erreur lors de la création du graphique\n{str(e)}",
                font=ctk.CTkFont(size=12),
                text_color="#EF4444"
            )
            error_label.pack(expand=True, fill="both")
            # Fermer toutes les figures matplotlib ouvertes
            plt.close('all')
    
    def actualiser_graphique_completion(self):
        """Actualise le graphique de complétion des séries"""
        try:
            self.creer_graphique_completion_series()
            self.log("📊 Graphique de complétion actualisé")
        except Exception as e:
            self.log(f"Erreur actualisation graphique : {e}")
    
    def actualiser_vue_ensemble_complete(self):
        """Actualise toutes les données et graphiques de la vue d'ensemble"""
        try:
            self.log("🔄 Actualisation complète de la vue d'ensemble en cours...")
            
            # 1. Actualiser les données et statistiques générales
            self.rafraichir_donnees()
            
            # 2. Recréer tous les graphiques compacts (grille 2x2)
            if hasattr(self, 'graphs_container') and self.graphs_container:
                # Nettoyer les graphiques existants
                for widget in self.graphs_container.winfo_children():
                    widget.destroy()
                
                # Reconfigurer la grille
                self.graphs_container.grid_columnconfigure(0, weight=1)
                self.graphs_container.grid_columnconfigure(1, weight=1)
                
                # Recréer tous les graphiques avec la nouvelle disposition
                self.creer_graphique_progression_series_compact(self.graphs_container, row=0, column=0)
                self.creer_heatmap_completion_compact(self.graphs_container, row=0, column=1)
                self.creer_graphique_objectifs_compact(self.graphs_container, row=1, column=0)
                self.creer_graphique_repartition_raretes_compact(self.graphs_container, row=1, column=1)
                
                self.log("📊 Tous les graphiques de la grille actualisés")
            else:
                self.log("⚠️ Container des graphiques non trouvé")
            
            self.log("✅ Vue d'ensemble entièrement actualisée")
            
        except Exception as e:
            self.log(f"❌ Erreur lors de l'actualisation complète : {e}")
            import traceback
            self.log(f"Détails de l'erreur : {traceback.format_exc()}")
    
    def run(self):
        """Lance l'interface"""
        self.root.mainloop()

    def creer_graphique_evolution_temporelle_compact(self, parent, row, column):
        """Crée le graphique d'évolution temporelle compact pour la grille"""
        try:
            # Frame pour le graphique d'évolution (plus compact)
            evolution_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color="#F1F5F9")
            evolution_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
            
            # En-tête avec style moderne (plus compact)
            header_frame = ctk.CTkFrame(evolution_frame, corner_radius=8, fg_color="#0F766E")
            header_frame.pack(fill="x", padx=10, pady=(10, 8))
            
            title_label = ctk.CTkLabel(
                header_frame,
                text="📈 Évolution Collection",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white"
            )
            title_label.pack(pady=8)
            
            # Récupérer les données d'évolution (derniers 6 mois pour un affichage compact)
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Données cumulatives des 6 derniers mois
            cursor.execute("""
                WITH RECURSIVE dates AS (
                    SELECT date('now', '-6 months') as date_point
                    UNION ALL
                    SELECT date(date_point, '+1 week')
                    FROM dates
                    WHERE date_point < date('now')
                ),
                weekly_totals AS (
                    SELECT d.date_point,
                           (SELECT COUNT(DISTINCT cr2.id) FROM carte_raretes cr2 
                            JOIN cartes c2 ON cr2.carte_id = c2.id
                            WHERE date(c2.date_ajout) <= d.date_point 
                            AND c2.date_ajout IS NOT NULL) as total_cumule,
                           (SELECT COUNT(*) FROM carte_raretes cr3 
                            WHERE date(cr3.date_acquisition) <= d.date_point 
                            AND cr3.possedee = 1 AND cr3.date_acquisition IS NOT NULL) as total_possedees
                    FROM dates d
                )
                SELECT date_point, total_cumule, total_possedees
                FROM weekly_totals
                WHERE total_cumule > 0 OR total_possedees > 0
                ORDER BY date_point
            """)
            
            evolution_data = cursor.fetchall()
            conn.close()
            
            # Créer la figure matplotlib compacte (taille réduite)
            plt.close('all')
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('#F1F5F9')
            ax.set_facecolor('#FFFFFF')
            
            if evolution_data:
                dates = [datetime.strptime(row[0], '%Y-%m-%d').date() for row in evolution_data]
                totaux_cumules = [row[1] for row in evolution_data]
                totaux_possedes = [row[2] for row in evolution_data]
                
                # Courbes avec style moderne
                ax.plot(dates, totaux_cumules, marker='o', linewidth=3, 
                       color='#3B82F6', label='Total en base', markersize=3, alpha=0.9)
                ax.fill_between(dates, totaux_cumules, alpha=0.15, color='#3B82F6')
                
                ax.plot(dates, totaux_possedes, marker='s', linewidth=3,
                       color='#10B981', label='Possédées', markersize=3, alpha=0.9)
                ax.fill_between(dates, totaux_possedes, alpha=0.15, color='#10B981')
                
                # Configuration moderne et épurée (tailles de police réduites)
                ax.set_ylabel('Nombre de cartes', fontsize=10, fontweight='bold', color='#374151')
                ax.legend(fontsize=9, loc='upper left', frameon=False)
                ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
                
                # Formatage des dates (compact)
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%y'))
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)
                
                # Style épuré
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#E5E7EB')
                ax.spines['bottom'].set_color('#E5E7EB')
                
            else:
                ax.text(0.5, 0.5, 'Commencez à ajouter\ndes cartes !', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEF3C7", alpha=0.8))
            
            plt.tight_layout()
            
            # Intégrer le graphique (padding réduit)
            canvas = FigureCanvasTkAgg(fig, evolution_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
        except Exception as e:
            plt.close('all')
            self.log(f"Erreur création graphique évolution overview : {e}")
    
    def creer_heatmap_completion_compact(self, parent, row, column):
        """Crée une heatmap compacte pour la grille"""
        try:
            # Frame pour la heatmap (plus compact)
            heatmap_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color="#F1F5F9")
            heatmap_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
            
            # En-tête avec style moderne (plus compact)
            header_frame = ctk.CTkFrame(heatmap_frame, corner_radius=8, fg_color="#7C2D12")
            header_frame.pack(fill="x", padx=10, pady=(10, 8))
            
            title_label = ctk.CTkLabel(
                header_frame,
                text="🔥 Heatmap Complétion",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white"
            )
            title_label.pack(pady=8)
            
            # Récupérer les données pour la heatmap (top 6 séries pour un affichage plus compact)
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                WITH top_series AS (
                    SELECT s.id, s.code_serie, COUNT(cr.id) as total_cartes
                    FROM series s
                    LEFT JOIN cartes c ON s.id = c.serie_id
                    LEFT JOIN carte_raretes cr ON c.id = cr.carte_id
                    GROUP BY s.id, s.code_serie
                    HAVING total_cartes > 0
                    ORDER BY total_cartes DESC
                    LIMIT 6
                )
                SELECT ts.code_serie, r.nom_rarete,
                       COUNT(cr.id) as total_exemplaires,
                       SUM(CASE WHEN cr.possedee = 1 THEN 1 ELSE 0 END) as possedes,
                       CASE WHEN COUNT(cr.id) > 0 
                            THEN ROUND((CAST(SUM(CASE WHEN cr.possedee = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(cr.id)) * 100, 1)
                            ELSE 0 END as pourcentage
                FROM top_series ts
                CROSS JOIN raretes r
                LEFT JOIN cartes c ON ts.id = c.serie_id
                LEFT JOIN carte_raretes cr ON c.id = cr.carte_id AND cr.rarete_id = r.id
                GROUP BY ts.id, ts.code_serie, r.id, r.nom_rarete
                HAVING total_exemplaires > 0
                ORDER BY ts.code_serie, r.nom_rarete
            """)
            
            heatmap_data = cursor.fetchall()
            conn.close()
            
            # Créer la figure matplotlib compacte (taille réduite)
            plt.close('all')
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('#F1F5F9')
            
            if heatmap_data:
                # Organiser les données en matrice
                series_set = sorted(list(set([row[0] for row in heatmap_data])))
                raretes_set = sorted(list(set([row[1] for row in heatmap_data])))
                
                # Créer la matrice de pourcentages
                matrix = np.zeros((len(raretes_set), len(series_set)))
                
                for row in heatmap_data:
                    serie_idx = series_set.index(row[0])
                    rarete_idx = raretes_set.index(row[1])
                    matrix[rarete_idx, serie_idx] = row[4]  # pourcentage
                
                # Créer la heatmap avec une palette moderne
                im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
                
                # Configuration des axes (tailles réduites)
                ax.set_xticks(np.arange(len(series_set)))
                ax.set_yticks(np.arange(len(raretes_set)))
                ax.set_xticklabels(series_set, rotation=45, ha='right', fontsize=9, fontweight='bold')
                ax.set_yticklabels(raretes_set, fontsize=9, fontweight='bold')
                
                # Ajouter les valeurs dans chaque cellule (plus petites)
                for i in range(len(raretes_set)):
                    for j in range(len(series_set)):
                        value = matrix[i, j]
                        if value > 0:
                            color = 'white' if value < 50 else 'black'
                            ax.text(j, i, f'{value:.0f}%', ha='center', va='center',
                                   color=color, fontweight='bold', fontsize=8)
                
                # Ajouter une barre de couleur moderne (plus compacte)
                cbar = plt.colorbar(im, ax=ax, shrink=0.6)
                cbar.set_label('Complétion (%)', rotation=270, labelpad=12, fontsize=9)
                cbar.ax.tick_params(labelsize=8)
                
                # Labels avec style moderne (plus petits)
                ax.set_xlabel('Séries', fontsize=10, fontweight='bold', color='#374151')
                ax.set_ylabel('Raretés', fontsize=10, fontweight='bold', color='#374151')
                
                # Style épuré
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                
            else:
                ax.text(0.5, 0.5, 'Ajoutez plus de cartes\npour l\'analyse !', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEF3C7", alpha=0.8))
            
            plt.tight_layout()
            
            # Intégrer le graphique (padding réduit)
            canvas = FigureCanvasTkAgg(fig, heatmap_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
        except Exception as e:
            plt.close('all')
            self.log(f"Erreur création heatmap overview : {e}")
    
    def creer_graphique_repartition_raretes_compact(self, parent, row, column):
        """Crée un graphique compact de répartition des raretés"""
        try:
            # Frame pour le graphique
            rarity_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color="#F1F5F9")
            rarity_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
            
            # En-tête
            header_frame = ctk.CTkFrame(rarity_frame, corner_radius=8, fg_color="#DC2626")
            header_frame.pack(fill="x", padx=10, pady=(10, 8))
            
            title_label = ctk.CTkLabel(
                header_frame,
                text="⭐ Répartition Raretés",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white"
            )
            title_label.pack(pady=8)
            
            # Récupérer les données
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.nom_rarete,
                       COUNT(cr.id) as total,
                       SUM(CASE WHEN cr.possedee = 1 THEN 1 ELSE 0 END) as possedes
                FROM raretes r
                LEFT JOIN carte_raretes cr ON r.id = cr.rarete_id
                GROUP BY r.id, r.nom_rarete
                HAVING total > 0
                ORDER BY total DESC
            """)
            
            rarity_data = cursor.fetchall()
            conn.close()
            
            # Créer le graphique optimisé pour les barres horizontales
            plt.close('all')
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('#F1F5F9')
            ax.set_facecolor('#FFFFFF')
            
            if rarity_data:
                rarity_names = [row[0] for row in rarity_data]
                possedes = [row[2] for row in rarity_data]
                
                # Filtrer les raretés avec des cartes possédées
                filtered_data = [(name, count) for name, count in zip(rarity_names, possedes) if count > 0]
                
                if filtered_data:
                    filtered_names, filtered_counts = zip(*filtered_data)
                    
                    # Couleurs modernes pour les raretés
                    colors = ['#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#F97316']
                    colors = colors[:len(filtered_names)]
                    
                    # Alternative: Graphique en barres horizontales (plus lisible dans un espace compact)
                    y_pos = np.arange(len(filtered_names))
                    bars = ax.barh(y_pos, filtered_counts, color=colors, alpha=0.8, height=0.6)
                    
                    # Configuration des axes
                    ax.set_yticks(y_pos)
                    ax.set_yticklabels(filtered_names, fontsize=9, fontweight='bold')
                    ax.set_xlabel('Cartes possédées', fontsize=10, fontweight='bold', color='#374151')
                    
                    # Ajouter les valeurs sur les barres
                    for i, (bar, count) in enumerate(zip(bars, filtered_counts)):
                        ax.text(count + max(filtered_counts) * 0.01, i, str(count), 
                               ha='left', va='center', fontweight='bold', fontsize=9, color='#374151')
                    
                    # Grille subtile
                    ax.grid(True, alpha=0.2, axis='x', linestyle='-', linewidth=0.5)
                    ax.set_axisbelow(True)
                    
                    # Style épuré
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['left'].set_color('#E5E7EB')
                    ax.spines['bottom'].set_color('#E5E7EB')
                    
                    # Inverser l'ordre pour avoir les plus grandes valeurs en haut
                    ax.invert_yaxis()
                else:
                    ax.text(0.5, 0.5, 'Aucune carte\npossédée', 
                           ha='center', va='center', transform=ax.transAxes, fontsize=10,
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEF3C7", alpha=0.8))
                
            else:
                ax.text(0.5, 0.5, 'Aucune donnée\nde rareté', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEF3C7", alpha=0.8))
            
            plt.tight_layout()
            
            # Intégrer le graphique
            canvas = FigureCanvasTkAgg(fig, rarity_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
        except Exception as e:
            plt.close('all')
            self.log(f"Erreur création graphique raretés compact : {e}")
    
    def creer_graphique_objectifs_compact(self, parent, row, column):
        """Crée un graphique compact des objectifs de collection"""
        try:
            # Frame pour le graphique
            objectifs_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color="#F1F5F9")
            objectifs_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
            
            # En-tête
            header_frame = ctk.CTkFrame(objectifs_frame, corner_radius=8, fg_color="#7C3AED")
            header_frame.pack(fill="x", padx=10, pady=(10, 8))
            
            title_label = ctk.CTkLabel(
                header_frame,
                text="🎯 Progression Globale",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white"
            )
            title_label.pack(pady=8)
            
            # Récupérer les statistiques globales
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT cr.id) as total_cartes,
                    SUM(CASE WHEN cr.possedee = 1 THEN 1 ELSE 0 END) as cartes_possedees,
                    COUNT(DISTINCT c.serie_id) as total_series,
                    COUNT(DISTINCT CASE WHEN EXISTS(
                        SELECT 1 FROM carte_raretes cr2 
                        WHERE cr2.carte_id IN (
                            SELECT c2.id FROM cartes c2 WHERE c2.serie_id = c.serie_id
                        ) AND cr2.possedee = 1
                    ) THEN c.serie_id END) as series_avec_cartes
                FROM carte_raretes cr
                JOIN cartes c ON cr.carte_id = c.id
            """)
            
            stats = cursor.fetchone()
            conn.close()
            
            # Créer le graphique de progression
            plt.close('all')
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 5))
            fig.patch.set_facecolor('#F1F5F9')
            
            if stats and stats[0] > 0:
                total_cartes, possedees, total_series, series_avec_cartes = stats
                
                # Graphique 1: Progression des cartes
                progression_cartes = (possedees / total_cartes) * 100 if total_cartes > 0 else 0
                
                ax1.pie([possedees, total_cartes - possedees], 
                       labels=['Possédées', 'Manquantes'],
                       colors=['#10B981', '#EF4444'],
                       autopct='%1.0f%%',
                       startangle=90,
                       textprops={'fontsize': 8})
                ax1.set_title('Cartes', fontsize=10, fontweight='bold', pad=10)
                
                # Graphique 2: Progression des séries
                ax2.pie([series_avec_cartes, total_series - series_avec_cartes], 
                       labels=['Entamées', 'Vides'],
                       colors=['#3B82F6', '#6B7280'],
                       autopct='%1.0f%%',
                       startangle=90,
                       textprops={'fontsize': 8})
                ax2.set_title('Séries', fontsize=10, fontweight='bold', pad=10)
                
            else:
                ax1.text(0.5, 0.5, 'Aucune\ndonnée', ha='center', va='center', 
                        transform=ax1.transAxes, fontsize=9)
                ax2.text(0.5, 0.5, 'Aucune\ndonnée', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=9)
            
            plt.tight_layout()
            
            # Intégrer le graphique
            canvas = FigureCanvasTkAgg(fig, objectifs_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
        except Exception as e:
            plt.close('all')
            self.log(f"Erreur création graphique objectifs compact : {e}")

    def creer_graphique_progression_series_compact(self, parent, row, column):
        """Crée le graphique de progression par série compact pour la grille"""
        try:
            # Frame pour le graphique
            progression_frame = ctk.CTkFrame(parent, corner_radius=12)
            progression_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
            
            # Titre
            title_label = ctk.CTkLabel(
                progression_frame,
                text="📊 Progression par Série",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#1E293B"
            )
            title_label.pack(pady=(10, 5))
            
            # Récupérer les données de progression par série
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.code_serie, s.nom_serie,
                       COUNT(cr.id) as total_cartes,
                       SUM(CASE WHEN cr.possedee = 1 THEN 1 ELSE 0 END) as cartes_possedees
                FROM series s
                LEFT JOIN cartes c ON s.id = c.serie_id
                LEFT JOIN carte_raretes cr ON c.id = cr.carte_id
                GROUP BY s.id, s.code_serie, s.nom_serie
                HAVING total_cartes > 0
                ORDER BY (CAST(SUM(CASE WHEN cr.possedee = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(cr.id)) DESC
                LIMIT 8
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            if results:
                # Préparer les données
                series_names = []
                percentages = []
                colors = []
                
                for code, nom, total, possedees in results:
                    pourcentage = (possedees / total * 100) if total > 0 else 0
                    series_names.append(code)
                    percentages.append(pourcentage)
                    
                    # Couleurs selon le pourcentage
                    if pourcentage >= 80:
                        colors.append('#10B981')  # Vert
                    elif pourcentage >= 50:
                        colors.append('#F59E0B')  # Orange
                    elif pourcentage >= 25:
                        colors.append('#EF4444')  # Rouge
                    else:
                        colors.append('#6B7280')  # Gris
                
                # Créer le graphique
                fig, ax = plt.subplots(figsize=(4, 3), facecolor='white')
                fig.patch.set_facecolor('white')
                
                # Graphique en barres horizontales
                bars = ax.barh(range(len(series_names)), percentages, color=colors, alpha=0.8)
                
                # Configuration
                ax.set_yticks(range(len(series_names)))
                ax.set_yticklabels(series_names, fontsize=8)
                ax.set_xlabel('Complétion (%)', fontsize=9)
                ax.set_xlim(0, 100)
                
                # Ajouter les pourcentages sur les barres
                for i, (bar, percentage) in enumerate(zip(bars, percentages)):
                    if percentage > 15:  # Si assez de place
                        ax.text(percentage/2, i, f'{percentage:.1f}%', 
                               ha='center', va='center', fontweight='bold', 
                               color='white', fontsize=8)
                    else:
                        ax.text(percentage + 2, i, f'{percentage:.1f}%', 
                               ha='left', va='center', fontweight='bold', 
                               color='black', fontsize=8)
                
                ax.grid(axis='x', alpha=0.3)
                ax.set_axisbelow(True)
                
                # Style moderne
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#E5E7EB')
                ax.spines['bottom'].set_color('#E5E7EB')
                
                plt.tight_layout()
                
            else:
                # Pas de données
                fig, ax = plt.subplots(figsize=(4, 3), facecolor='white')
                ax.text(0.5, 0.5, 'Aucune\ndonnée\ndisponible', 
                       ha='center', va='center', transform=ax.transAxes, 
                       fontsize=10, color='#6B7280')
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
            
            # Intégrer le graphique
            canvas = FigureCanvasTkAgg(fig, progression_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
        except Exception as e:
            plt.close('all')
            self.log(f"Erreur création graphique progression séries compact : {e}")

    def setup_tree_columns(self, with_selection=False):
        """Configure les colonnes du treeview selon le mode"""
        try:
            if with_selection:
                # Configuration avec colonne de sélection
                self.cartes_tree.heading("select", text="⭕ Sél.")
                self.cartes_tree.heading("numero", text="🔢 N°")
                self.cartes_tree.heading("nom", text="🃏 Nom de la carte")
                self.cartes_tree.heading("rarete", text="⭐ Rareté")
                self.cartes_tree.heading("possede", text="📊 Statut")
                
                self.cartes_tree.column("select", width=50, anchor="center")
                self.cartes_tree.column("numero", width=80, anchor="center")
                self.cartes_tree.column("nom", width=220)
                self.cartes_tree.column("rarete", width=110, anchor="center")
                self.cartes_tree.column("possede", width=90, anchor="center")
            else:
                # Configuration sans colonne de sélection
                self.cartes_tree.heading("numero", text="🔢 N°")
                self.cartes_tree.heading("nom", text="🃏 Nom de la carte")
                self.cartes_tree.heading("rarete", text="⭐ Rareté")
                self.cartes_tree.heading("possede", text="📊 Statut")
                
                self.cartes_tree.column("numero", width=80, anchor="center")
                self.cartes_tree.column("nom", width=280)
                self.cartes_tree.column("rarete", width=110, anchor="center")
                self.cartes_tree.column("possede", width=90, anchor="center")
                
        except Exception as e:
            self.log(f"Erreur configuration colonnes : {e}")
    
    def toggle_selection_mode(self):
        """Active/désactive le mode sélection"""
        try:
            self.selection_mode_active = not self.selection_mode_active
            
            if self.selection_mode_active:
                # Activer le mode sélection
                self.toggle_selection_btn.configure(
                    text="❌ Désactiver Sélection",
                    fg_color="#EF4444",
                    hover_color="#DC2626"
                )
                
                # Afficher les outils de sélection
                self.selection_tools_frame.pack(side="left", padx=(5, 0), pady=8)
                
                # Reconfigurer le treeview avec la colonne de sélection
                self.cartes_tree.configure(columns=self.selection_columns)
                self.setup_tree_columns(True)
                
                # Recharger les cartes avec la colonne de sélection
                if hasattr(self, 'current_serie_name') and self.current_serie_name:
                    self.charger_cartes_serie(self.current_serie_name)
                    
            else:
                # Désactiver le mode sélection
                self.toggle_selection_btn.configure(
                    text="🎯 Activer Sélection",
                    fg_color="#6366F1",
                    hover_color="#4F46E5"
                )
                
                # Cacher les outils de sélection
                self.selection_tools_frame.pack_forget()
                
                # Réinitialiser les sélections
                self.selected_cards.clear()
                self.all_selected = False
                
                # Reconfigurer le treeview sans la colonne de sélection
                self.cartes_tree.configure(columns=self.base_columns)
                self.setup_tree_columns(False)
                
                # Recharger les cartes sans la colonne de sélection
                if hasattr(self, 'current_serie_name') and self.current_serie_name:
                    self.charger_cartes_serie(self.current_serie_name)
                    
        except Exception as e:
            self.log(f"Erreur toggle mode sélection : {e}")
    
    def on_tree_click(self, event):
        """Gère les clics sur le treeview pour la sélection multiple"""
        try:
            if not self.selection_mode_active:
                return
                
            # Identifier l'élément cliqué
            item = self.cartes_tree.identify_row(event.y)
            
            # Si on clique sur une ligne valide, peu importe la colonne
            if item:
                self.toggle_card_selection(item)
                return "break"  # Empêche la sélection par défaut du treeview
                
        except Exception as e:
            self.log(f"Erreur lors du clic sur le treeview : {e}")
    
    def toggle_card_selection(self, item):
        """Bascule la sélection d'une carte avec des cercles et couleur bleue"""
        try:
            # Récupérer les tags actuels pour récupérer le cr_id et le statut
            current_tags = self.cartes_tree.item(item, "tags")
            cr_id = current_tags[0] if current_tags else None  # Le cr_id est toujours le premier tag
            is_owned = any("owned" in str(tag) for tag in current_tags if not "selection" in str(tag))
            
            if item in self.selected_cards:
                # Désélectionner : enlever la sélection
                self.selected_cards.remove(item)
                # Mettre à jour l'affichage : cercle vide
                values = list(self.cartes_tree.item(item, "values"))
                values[0] = "⭕"  # Cercle vide
                self.cartes_tree.item(item, values=values)
                
                # Restaurer les couleurs normales en gardant le cr_id
                if is_owned:
                    self.cartes_tree.item(item, tags=(cr_id, "owned"))
                else:
                    self.cartes_tree.item(item, tags=(cr_id, "not_owned"))
            else:
                # Sélectionner : ajouter la sélection
                self.selected_cards.add(item)
                # Mettre à jour l'affichage : cercle plein
                values = list(self.cartes_tree.item(item, "values"))
                values[0] = "🔴"  # Cercle plein rouge
                self.cartes_tree.item(item, values=values)
                
                # Appliquer les couleurs bleues de sélection en gardant le cr_id
                if is_owned:
                    self.cartes_tree.item(item, tags=(cr_id, "owned_selection_active"))
                else:
                    self.cartes_tree.item(item, tags=(cr_id, "not_owned_selection_active"))
            
            # Mettre à jour le compteur
            self.update_selection_count()
            
        except Exception as e:
            self.log(f"Erreur lors de la sélection de carte : {e}")
    
    def toggle_select_all(self):
        """Sélectionne ou désélectionne toutes les cartes visibles"""
        try:
            children = self.cartes_tree.get_children()
            
            if not self.all_selected:
                # Sélectionner toutes les cartes
                self.selected_cards.clear()
                for item in children:
                    self.selected_cards.add(item)
                    values = list(self.cartes_tree.item(item, "values"))
                    values[0] = "🔴"  # Cercle plein
                    self.cartes_tree.item(item, values=values)
                    
                    # Appliquer les couleurs bleues de sélection en conservant le cr_id
                    current_tags = self.cartes_tree.item(item, "tags")
                    cr_id = current_tags[0] if current_tags else None
                    is_owned = any("owned" in str(tag) for tag in current_tags if not "selection" in str(tag))
                    if is_owned:
                        self.cartes_tree.item(item, tags=(cr_id, "owned_selection_active"))
                    else:
                        self.cartes_tree.item(item, tags=(cr_id, "not_owned_selection_active"))
                
                self.select_all_btn.configure(text="⭕ Tout désélectionner")
                self.all_selected = True
            else:
                # Désélectionner toutes les cartes
                self.selected_cards.clear()
                for item in children:
                    values = list(self.cartes_tree.item(item, "values"))
                    values[0] = "⭕"  # Cercle vide
                    self.cartes_tree.item(item, values=values)
                    
                    # Restaurer les couleurs normales en conservant le cr_id
                    current_tags = self.cartes_tree.item(item, "tags")
                    cr_id = current_tags[0] if current_tags else None
                    is_owned = any("owned" in str(tag) for tag in current_tags if not "selection" in str(tag))
                    if is_owned:
                        self.cartes_tree.item(item, tags=(cr_id, "owned"))
                    else:
                        self.cartes_tree.item(item, tags=(cr_id, "not_owned"))
                
                self.select_all_btn.configure(text="⭕ Tout sélectionner")
                self.all_selected = False
            
            self.update_selection_count()
            
        except Exception as e:
            self.log(f"Erreur lors de la sélection globale : {e}")
    
    def update_selection_count(self):
        """Met à jour le compteur de cartes sélectionnées"""
        try:
            count = len(self.selected_cards)
            if count == 0:
                self.selection_count_label.configure(text="Aucune carte sélectionnée")
            elif count == 1:
                self.selection_count_label.configure(text="1 carte sélectionnée")
            else:
                self.selection_count_label.configure(text=f"{count} cartes sélectionnées")
                
            # Réinitialiser le bouton "Tout sélectionner" si besoin
            if count == 0:
                self.all_selected = False
                self.select_all_btn.configure(text="☑️ Tout sélectionner")
                
        except Exception as e:
            self.log(f"Erreur lors de la mise à jour du compteur : {e}")
    
    def ajouter_cartes_selectionnees(self):
        """Ajoute les cartes sélectionnées à la collection (les marque comme possédées)"""
        try:
            if not self.selected_cards:
                self.log("Aucune carte sélectionnée pour ajout")
                return
            
            count_updated = 0
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            for item in self.selected_cards:
                # Récupérer l'ID de carte_raretes depuis les tags de l'élément
                tags = self.cartes_tree.item(item, "tags")
                if tags:
                    carte_rarete_id = tags[0]  # Le premier tag contient toujours l'ID cr_id
                    
                    # Ajouter à la collection (marquer comme possédée)
                    cursor.execute("""
                        UPDATE carte_raretes 
                        SET possedee = 1, date_acquisition = CURRENT_DATE
                        WHERE id = ?
                    """, (carte_rarete_id,))
                    count_updated += 1
            
            conn.commit()
            conn.close()
            
            # Actualiser l'affichage
            self.charger_cartes_serie(self.current_serie_name)
            self.selected_cards.clear()
            self.update_selection_count()
            
            self.log(f"➕ {count_updated} carte(s) ajoutée(s) à la collection")
            
        except Exception as e:
            self.log(f"Erreur lors de l'ajout des cartes : {e}")
    
    def supprimer_cartes_selectionnees(self):
        """Supprime les cartes sélectionnées de la collection (les marque comme non possédées)"""
        try:
            if not self.selected_cards:
                self.log("Aucune carte sélectionnée pour suppression")
                return
            
            count_updated = 0
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            for item in self.selected_cards:
                # Récupérer l'ID de carte_raretes depuis les tags de l'élément
                tags = self.cartes_tree.item(item, "tags")
                if tags:
                    carte_rarete_id = tags[0]  # Le premier tag contient toujours l'ID cr_id
                    
                    # Supprimer de la collection (marquer comme non possédée)
                    cursor.execute("""
                        UPDATE carte_raretes 
                        SET possedee = 0, date_acquisition = NULL
                        WHERE id = ?
                    """, (carte_rarete_id,))
                    count_updated += 1
            
            conn.commit()
            conn.close()
            
            # Actualiser l'affichage
            self.charger_cartes_serie(self.current_serie_name)
            self.selected_cards.clear()
            self.update_selection_count()
            
            self.log(f"➖ {count_updated} carte(s) supprimée(s) de la collection")
            
        except Exception as e:
            self.log(f"Erreur lors de la suppression des cartes : {e}")
    
    def supprimer_cartes_definitivement(self):
        """Supprime définitivement les cartes sélectionnées de la base de données"""
        try:
            if not self.selected_cards:
                self.log("Aucune carte sélectionnée pour suppression définitive")
                return
            
            # Demander confirmation avec un dialog personnalisé
            import tkinter.messagebox as msgbox
            
            count_cards = len(self.selected_cards)
            message = f"⚠️ ATTENTION ⚠️\n\n"
            message += f"Vous êtes sur le point de supprimer DÉFINITIVEMENT {count_cards} carte(s) de la base de données.\n\n"
            message += "Cette action est IRRÉVERSIBLE !\n"
            message += "Les cartes seront complètement supprimées et ne pourront pas être récupérées.\n\n"
            message += "Êtes-vous absolument certain de vouloir continuer ?"
            
            response = msgbox.askyesno(
                "Confirmation de suppression définitive", 
                message,
                icon="warning"
            )
            
            if not response:
                self.log("Suppression définitive annulée par l'utilisateur")
                return
            
            count_deleted = 0
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            for item in self.selected_cards:
                # Récupérer l'ID de carte_raretes depuis les tags de l'élément
                tags = self.cartes_tree.item(item, "tags")
                if tags:
                    carte_rarete_id = tags[0]  # Le premier tag contient toujours l'ID cr_id
                    
                    # Supprimer définitivement de la base de données
                    cursor.execute("""
                        DELETE FROM carte_raretes 
                        WHERE id = ?
                    """, (carte_rarete_id,))
                    count_deleted += 1
            
            conn.commit()
            conn.close()
            
            # Actualiser l'affichage
            self.charger_cartes_serie(self.current_serie_name)
            self.selected_cards.clear()
            self.update_selection_count()
            
            self.log(f"🗑️ {count_deleted} carte(s) supprimée(s) DÉFINITIVEMENT de la base de données")
            
        except Exception as e:
            self.log(f"Erreur lors de la suppression définitive des cartes : {e}")

def main():
    """Fonction principale"""
    app = CollectionManagerGUI()
    app.run()

if __name__ == "__main__":
    main()
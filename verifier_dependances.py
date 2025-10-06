#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification et d'installation des dépendances
pour le Convertisseur Yu-Gi-Oh V2
"""

import sys
import subprocess
import importlib.util

def verifier_module(nom_module, nom_package=None):
    """Vérifie si un module est installé"""
    if nom_package is None:
        nom_package = nom_module
    
    spec = importlib.util.find_spec(nom_module)
    if spec is None:
        print(f"❌ {nom_module} non installé")
        return False
    else:
        print(f"✅ {nom_module} installé")
        return True

def installer_package(nom_package):
    """Installe un package via pip"""
    try:
        print(f"📦 Installation de {nom_package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", nom_package])
        print(f"✅ {nom_package} installé avec succès")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Erreur lors de l'installation de {nom_package}")
        return False

def main():
    print("🔧 VÉRIFICATION DES DÉPENDANCES")
    print("=" * 50)
    
    # Modules requis
    modules_requis = [
        ("requests", "requests"),
        ("selenium", "selenium"),
        ("webdriver_manager", "webdriver-manager"),
        ("tkinter", None),  # Tkinter est généralement inclus avec Python
    ]
    
    modules_manquants = []
    
    print("\n📋 Vérification des modules...")
    for module, package in modules_requis:
        if module == "tkinter":
            # Vérification spéciale pour tkinter
            try:
                import tkinter
                print("✅ tkinter installé")
            except ImportError:
                print("❌ tkinter non disponible")
                print("💡 Tkinter devrait être inclus avec Python")
                modules_manquants.append(("tkinter", "python-tk"))
        else:
            if not verifier_module(module):
                modules_manquants.append((module, package))
    
    # Installation des modules manquants
    if modules_manquants:
        print(f"\n🔧 Installation de {len(modules_manquants)} modules manquants...")
        
        for module, package in modules_manquants:
            if package and package != "python-tk":
                installer_package(package)
        
        print("\n🔄 Nouvelle vérification...")
        for module, package in modules_manquants:
            if module != "tkinter":
                verifier_module(module)
    
    else:
        print("\n🎉 Toutes les dépendances sont installées!")
    
    print("\n" + "=" * 50)
    print("✨ Vérification terminée")
    
    # Test rapide de l'interface
    try:
        print("\n🧪 Test rapide de l'interface...")
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Cache la fenêtre
        root.destroy()
        print("✅ Interface graphique fonctionnelle")
        
    except Exception as e:
        print(f"❌ Problème avec l'interface : {e}")
        print("💡 Redémarrez votre terminal et réessayez")
    
    input("\n👆 Appuyez sur Entrée pour fermer...")

if __name__ == "__main__":
    main()
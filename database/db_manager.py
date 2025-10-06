#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire de base de données SQLite pour la collection Yu-Gi-Oh
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = "database/collection.db"):
        """
        Initialise le gestionnaire de base de données
        
        Args:
            db_path (str): Chemin vers le fichier de base de données
        """
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """S'assure que la base de données et ses tables existent"""
        # Créer le dossier database s'il n'existe pas
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Créer/initialiser la base de données
        if not os.path.exists(self.db_path):
            print(f"🗄️ Création de la base de données : {self.db_path}")
            self.create_database()
        else:
            print(f"✅ Base de données trouvée : {self.db_path}")
    
    def create_database(self):
        """Crée la structure de base de données à partir du schema SQL"""
        schema_path = os.path.join(os.path.dirname(__file__), "database_schema.sql")
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Exécuter le schema
            cursor.executescript(schema_sql)
            conn.commit()
            conn.close()
            
            print("✅ Base de données créée avec succès")
            
        except FileNotFoundError:
            print(f"❌ Fichier schema non trouvé : {schema_path}")
            # Créer une version basique si le schema n'existe pas
            self.create_basic_schema()
        except Exception as e:
            print(f"❌ Erreur lors de la création : {e}")
    
    def create_basic_schema(self):
        """Crée un schema de base si le fichier SQL n'existe pas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tables basiques
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_serie VARCHAR(10) NOT NULL UNIQUE,
                nom_serie VARCHAR(100) NOT NULL,
                url_source TEXT,
                date_ajout DATETIME DEFAULT CURRENT_TIMESTAMP,
                nb_cartes_total INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cartes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_carte VARCHAR(20) NOT NULL UNIQUE,
                nom_carte VARCHAR(200) NOT NULL,
                serie_id INTEGER NOT NULL,
                date_ajout DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (serie_id) REFERENCES series (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS raretes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_rarete VARCHAR(50) NOT NULL UNIQUE,
                ordre_tri INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carte_raretes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                carte_id INTEGER NOT NULL,
                rarete_id INTEGER NOT NULL,
                possedee BOOLEAN DEFAULT FALSE,
                date_acquisition DATE,
                condition VARCHAR(20) DEFAULT 'NM',
                prix_achat DECIMAL(10,2),
                notes TEXT,
                FOREIGN KEY (carte_id) REFERENCES cartes (id),
                FOREIGN KEY (rarete_id) REFERENCES raretes (id),
                UNIQUE (carte_id, rarete_id)
            )
        ''')
        
        # Raretés de base
        raretes_base = [
            ('Common', 1), ('Rare', 2), ('Super Rare', 3), ('Ultra Rare', 4),
            ('Secret Rare', 5), ('Ultimate Rare', 6), ('Ghost Rare', 7),
            ('Starlight Rare', 8), ('Collector\'s Rare', 9),
            ('Platinum Secret Rare', 10), ('Quarter Century Secret Rare', 11)
        ]
        
        cursor.executemany(
            'INSERT OR IGNORE INTO raretes (nom_rarete, ordre_tri) VALUES (?, ?)',
            raretes_base
        )
        
        conn.commit()
        conn.close()
        print("✅ Schema basique créé")
    
    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    
    def ajouter_serie(self, code_serie: str, nom_serie: str, url_source: str = None) -> int:
        """
        Ajoute une nouvelle série à la base de données
        
        Args:
            code_serie (str): Code de la série (BLMM, RA02, etc.)
            nom_serie (str): Nom complet de la série
            url_source (str, optional): URL Yugipedia source
        
        Returns:
            int: ID de la série créée
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO series (code_serie, nom_serie, url_source)
                VALUES (?, ?, ?)
            ''', (code_serie, nom_serie, url_source))
            
            serie_id = cursor.lastrowid
            conn.commit()
            
            print(f"✅ Série ajoutée : {code_serie} - {nom_serie}")
            return serie_id
            
        except sqlite3.IntegrityError:
            # Série existe déjà, vérifier et mettre à jour l'URL et le nom si nécessaire
            cursor.execute('SELECT id, nom_serie, url_source FROM series WHERE code_serie = ?', (code_serie,))
            result = cursor.fetchone()
            if result:
                serie_id, nom_existant, url_existante = result
                
                # Préparer les mises à jour
                mises_a_jour = []
                params = []
                
                # Mettre à jour l'URL si elle est fournie et (différente OU si l'existante est NULL/vide)
                if url_source and (not url_existante or url_source != url_existante):
                    mises_a_jour.append("url_source = ?")
                    params.append(url_source)
                
                # Mettre à jour le nom si le nom existant est générique et qu'on a un nom plus complet
                nom_generique = f"Série {code_serie}"
                if nom_existant == nom_generique and nom_serie != nom_generique:
                    mises_a_jour.append("nom_serie = ?")
                    params.append(nom_serie)
                
                # Exécuter les mises à jour si nécessaire
                if mises_a_jour:
                    params.append(code_serie)  # Pour la clause WHERE
                    cursor.execute(f'''
                        UPDATE series SET {", ".join(mises_a_jour)} WHERE code_serie = ?
                    ''', params)
                    conn.commit()
                    
                    # Messages informatifs
                    if url_source and (not url_existante or url_source != url_existante):
                        if not url_existante:
                            print(f"🔗 URL ajoutée pour {code_serie} : {url_source}")
                        else:
                            print(f"🔗 URL mise à jour pour {code_serie} : {url_source}")
                    
                    if nom_existant == nom_generique and nom_serie != nom_generique:
                        print(f"📝 Nom mis à jour pour {code_serie} : {nom_serie}")
                
                else:
                    if url_existante and nom_existant != nom_generique:
                        print(f"ℹ️  Série existante : {code_serie} (déjà complète)")
                    else:
                        print(f"ℹ️  Série existante : {code_serie}")
                return serie_id
            raise
        finally:
            conn.close()
    
    def get_serie_id(self, code_serie: str) -> Optional[int]:
        """Retourne l'ID d'une série par son code"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM series WHERE code_serie = ?', (code_serie,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def get_rarete_id(self, nom_rarete: str) -> Optional[int]:
        """Retourne l'ID d'une rareté par son nom"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM raretes WHERE nom_rarete = ?', (nom_rarete,))
        result = cursor.fetchone()
        
        if not result:
            # Créer la rareté si elle n'existe pas
            cursor.execute('''
                INSERT INTO raretes (nom_rarete, ordre_tri) 
                VALUES (?, (SELECT COALESCE(MAX(ordre_tri), 0) + 1 FROM raretes))
            ''', (nom_rarete,))
            conn.commit()
            rarete_id = cursor.lastrowid
            print(f"➕ Nouvelle rareté créée : {nom_rarete}")
        else:
            rarete_id = result[0]
        
        conn.close()
        return rarete_id
    
    def ajouter_carte(self, numero_carte: str, nom_carte: str, serie_id: int) -> int:
        """Ajoute une carte à la base de données"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO cartes (numero_carte, nom_carte, serie_id)
                VALUES (?, ?, ?)
            ''', (numero_carte, nom_carte, serie_id))
            
            carte_id = cursor.lastrowid
            conn.commit()
            return carte_id
            
        except sqlite3.IntegrityError:
            # Carte existe déjà
            cursor.execute('SELECT id FROM cartes WHERE numero_carte = ?', (numero_carte,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()
    
    def lier_carte_rarete(self, carte_id: int, rarete_id: int) -> bool:
        """Crée une liaison entre une carte et une rareté"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO carte_raretes (carte_id, rarete_id, possedee)
                VALUES (?, ?, FALSE)
            ''', (carte_id, rarete_id))
            
            conn.commit()
            return True
            
        except sqlite3.IntegrityError:
            # Liaison existe déjà
            return False
        finally:
            conn.close()
    
    def marquer_carte_possedee(self, numero_carte: str, nom_rarete: str, possedee: bool = True,
                              date_acquisition: str = None, condition: str = 'NM', 
                              prix_achat: float = None, notes: str = None) -> bool:
        """Marque une carte comme possédée ou non"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE carte_raretes 
                SET possedee = ?, date_acquisition = ?, condition = ?, 
                    prix_achat = ?, notes = ?
                WHERE carte_id = (SELECT id FROM cartes WHERE numero_carte = ?)
                AND rarete_id = (SELECT id FROM raretes WHERE nom_rarete = ?)
            ''', (possedee, date_acquisition, condition, prix_achat, notes, 
                  numero_carte, nom_rarete))
            
            if cursor.rowcount > 0:
                conn.commit()
                status = "possédée" if possedee else "non possédée"
                print(f"✅ {numero_carte} ({nom_rarete}) marquée comme {status}")
                return True
            else:
                print(f"❌ Carte/rareté non trouvée : {numero_carte} - {nom_rarete}")
                return False
                
        finally:
            conn.close()
    
    def get_stats_collection(self) -> List[Dict]:
        """Retourne les statistiques de collection par série"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                s.code_serie,
                s.nom_serie,
                COUNT(cr.id) as total_exemplaires,
                SUM(CASE WHEN cr.possedee THEN 1 ELSE 0 END) as possedes,
                ROUND(
                    (SUM(CASE WHEN cr.possedee THEN 1 ELSE 0 END) * 100.0) / COUNT(cr.id), 
                    2
                ) as pourcentage_collection
            FROM series s
            LEFT JOIN cartes c ON s.id = c.serie_id
            LEFT JOIN carte_raretes cr ON c.id = cr.carte_id
            GROUP BY s.id, s.code_serie, s.nom_serie
            ORDER BY s.code_serie
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        stats = []
        for row in results:
            stats.append({
                'code_serie': row[0],
                'nom_serie': row[1],
                'total_exemplaires': row[2] or 0,
                'possedes': row[3] or 0,
                'pourcentage_collection': row[4] or 0.0
            })
        
        return stats
    
    def get_cartes_manquantes(self, code_serie: str = None) -> List[Dict]:
        """Retourne les cartes manquantes (optionnellement filtrées par série)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                s.code_serie,
                c.numero_carte,
                c.nom_carte,
                r.nom_rarete
            FROM carte_raretes cr
            JOIN cartes c ON cr.carte_id = c.id
            JOIN series s ON c.serie_id = s.id  
            JOIN raretes r ON cr.rarete_id = r.id
            WHERE cr.possedee = FALSE
        '''
        
        params = []
        if code_serie:
            query += ' AND s.code_serie = ?'
            params.append(code_serie)
        
        query += ' ORDER BY s.code_serie, c.numero_carte, r.ordre_tri'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        manquantes = []
        for row in results:
            manquantes.append({
                'code_serie': row[0],
                'numero_carte': row[1], 
                'nom_carte': row[2],
                'nom_rarete': row[3]
            })
        
        return manquantes

# Test rapide si exécuté directement
if __name__ == "__main__":
    print("🧪 Test du gestionnaire de base de données")
    
    # Créer une instance de test
    db = DatabaseManager("database/test_collection.db")
    
    # Test d'ajout de série
    serie_id = db.ajouter_serie("TEST", "Test Serie", "http://example.com")
    print(f"ID série créée : {serie_id}")
    
    # Afficher les stats (vides pour l'instant)
    stats = db.get_stats_collection()
    print("📊 Statistiques :", stats)
    
    print("✅ Test terminé !")
-- 🎯 Schema SQLite pour Collection Yu-Gi-Oh
-- Base de données: collection.db

-- Table des séries Yu-Gi-Oh
CREATE TABLE series (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_serie VARCHAR(10) NOT NULL UNIQUE,           -- BLMM, RA02, CYAC
    nom_serie VARCHAR(100) NOT NULL,                  -- "Monster Mayhem", "25th Anniversary"
    url_source TEXT,                                  -- URL Yugipedia
    date_ajout DATETIME DEFAULT CURRENT_TIMESTAMP,
    nb_cartes_total INTEGER DEFAULT 0                 -- Compteur automatique
);

-- Table des cartes
CREATE TABLE cartes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_carte VARCHAR(20) NOT NULL UNIQUE,        -- BLMM-FR001, RA02-FR001
    nom_carte VARCHAR(200) NOT NULL,                 -- "Dragon Blanc aux Yeux Bleus"
    serie_id INTEGER NOT NULL,                       -- Référence vers series.id
    date_ajout DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (serie_id) REFERENCES series (id),
    INDEX idx_numero (numero_carte),
    INDEX idx_serie (serie_id)
);

-- Table des raretés
CREATE TABLE raretes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_rarete VARCHAR(50) NOT NULL UNIQUE,          -- "Secret Rare", "Ultra Rare"
    couleur_hex VARCHAR(7),                          -- Couleur d'affichage (optionnel)
    ordre_tri INTEGER DEFAULT 0                      -- Pour trier par valeur
);

-- Table de liaison cartes-raretés (many-to-many)
CREATE TABLE carte_raretes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carte_id INTEGER NOT NULL,
    rarete_id INTEGER NOT NULL,
    possedee BOOLEAN DEFAULT FALSE,                  -- ★ GESTION COLLECTION ★
    date_acquisition DATE,                           -- Quand obtenue
    condition VARCHAR(20) DEFAULT 'NM',             -- Near Mint, Light Play, etc.
    prix_achat DECIMAL(10,2),                       -- Prix payé (optionnel)
    notes TEXT,                                      -- Commentaires
    
    FOREIGN KEY (carte_id) REFERENCES cartes (id),
    FOREIGN KEY (rarete_id) REFERENCES raretes (id),
    UNIQUE (carte_id, rarete_id),                   -- Une carte-rareté unique
    INDEX idx_possession (possedee),
    INDEX idx_carte_rarete (carte_id, rarete_id)
);

-- Vues pratiques pour les requêtes

-- Vue collection complète
CREATE VIEW vue_collection AS
SELECT 
    s.code_serie,
    s.nom_serie,
    c.numero_carte,
    c.nom_carte,
    r.nom_rarete,
    cr.possedee,
    cr.date_acquisition,
    cr.condition,
    cr.prix_achat
FROM carte_raretes cr
JOIN cartes c ON cr.carte_id = c.id
JOIN series s ON c.serie_id = s.id  
JOIN raretes r ON cr.rarete_id = r.id
ORDER BY s.code_serie, c.numero_carte, r.ordre_tri;

-- Vue statistiques par série
CREATE VIEW vue_stats_series AS
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
ORDER BY s.code_serie;

-- Insertion des raretés standards
INSERT INTO raretes (nom_rarete, ordre_tri) VALUES 
('Common', 1),
('Rare', 2),
('Super Rare', 3),
('Ultra Rare', 4),
('Secret Rare', 5),
('Ultimate Rare', 6),
('Ghost Rare', 7),
('Starlight Rare', 8),
('Collector''s Rare', 9),
('Platinum Secret Rare', 10),
('Quarter Century Secret Rare', 11);

-- Triggers pour maintenir les compteurs
CREATE TRIGGER update_nb_cartes_insert 
AFTER INSERT ON cartes 
BEGIN
    UPDATE series SET nb_cartes_total = (
        SELECT COUNT(*) FROM cartes WHERE serie_id = NEW.serie_id
    ) WHERE id = NEW.serie_id;
END;

CREATE TRIGGER update_nb_cartes_delete 
AFTER DELETE ON cartes 
BEGIN
    UPDATE series SET nb_cartes_total = (
        SELECT COUNT(*) FROM cartes WHERE serie_id = OLD.serie_id
    ) WHERE id = OLD.serie_id;
END;
"""
Gestion de la base de données SQLite
RGPD : minimisation des données, durées de conservation
"""

import sqlite3
from datetime import datetime, timedelta
from flask import g
from werkzeug.security import generate_password_hash

DATABASE = "ensa_ia.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


def init_db():
    """Création des tables et de l'utilisateur admin par défaut."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")

    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT    NOT NULL UNIQUE,
            password_hash TEXT   NOT NULL,
            role         TEXT    NOT NULL DEFAULT 'etudiant',
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS requests (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL,
            prompt_preview   TEXT,
            prompt_full      TEXT,
            response_preview TEXT,
            response_full    TEXT,
            model_used       TEXT    DEFAULT 'local',
            is_flagged       INTEGER DEFAULT 0,
            flag_reason      TEXT    DEFAULT '',
            created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS idx_requests_user_id   ON requests(user_id);
        CREATE INDEX IF NOT EXISTS idx_requests_created_at ON requests(created_at);
        CREATE INDEX IF NOT EXISTS idx_requests_flagged    ON requests(is_flagged);
    """)

    # Compte admin par défaut
    existing = db.execute("SELECT id FROM users WHERE username='admin'").fetchone()
    if not existing:
        db.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
            ("admin", generate_password_hash("Admin@ENSA2025"), "admin")
        )

    db.commit()
    db.close()
    print("[DB] Base de données initialisée.")


def purge_old_data():
    """
    RGPD Art. 5(1)(e) — Limitation de la conservation.
    Supprime les requêtes de plus de 6 mois.
    À appeler via un cron job ou au démarrage.
    """
    db = sqlite3.connect(DATABASE)
    cutoff = datetime.utcnow() - timedelta(days=180)
    cursor = db.execute(
        "DELETE FROM requests WHERE created_at < ?", (cutoff,)
    )
    deleted = cursor.rowcount
    db.commit()
    db.close()
    if deleted:
        print(f"[PURGE] {deleted} requêtes supprimées (antérieures à {cutoff.date()})")
    return deleted


def migrate_db():
    """Ajoute les nouvelles colonnes pour les actions admin."""
    db = sqlite3.connect(DATABASE)
    migrations = [
        "ALTER TABLE requests ADD COLUMN admin_action TEXT DEFAULT NULL",
        "ALTER TABLE requests ADD COLUMN admin_note   TEXT DEFAULT NULL",
        "ALTER TABLE requests ADD COLUMN admin_at     TEXT DEFAULT NULL",
        "ALTER TABLE users    ADD COLUMN is_blocked   INTEGER DEFAULT 0",
        "ALTER TABLE users    ADD COLUMN blocked_reason TEXT DEFAULT NULL",
        """CREATE TABLE IF NOT EXISTS warnings (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            req_id     INTEGER,
            reason     TEXT,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""",
    ]
    for sql in migrations:
        try:
            db.execute(sql)
            print(f"[MIGRATE] OK : {sql[:50]}...")
        except Exception as e:
            print(f"[MIGRATE] Déjà existant : {e}")
    db.commit()
    db.close()

# Système IA Responsable — ENSA Béni Mellal
### Assistant Pédagogique Intelligent & Conforme RGPD / Loi 09-08

---

## Description du Projet

Ce système est une **application web d'assistance pédagogique par intelligence artificielle**, conçue et développée dans le cadre du module Éthique et Droit du Numérique (EDN) de la filière IACS à l'ENSA de Béni Mellal.

L'objectif est de démontrer qu'il est possible de déployer un système IA utile tout en respectant rigoureusement les principes du RGPD, la loi marocaine 09-08 sur la protection des données personnelles, et les exigences éthiques de gouvernance IA.

### Ce qui la distingue

Contrairement à un simple chatbot, ce système intègre dès sa conception (Privacy by Design) l'ensemble des mécanismes de conformité RGPD : filtrage automatique des données personnelles, journalisation complète des actions, supervision humaine obligatoire, et gestion des droits des personnes.

---

## Architecture du Projet

```
ensa_ia/
├── app.py              # Application Flask — routes, authentification, logique RGPD
├── database.py         # Base SQLite — schéma, initialisation, migration, purge automatique
├── ai_service.py       # Service IA — API Groq (Llama 3.1) + fallback local ENSA-BM
├── compliance.py       # Moteur de conformité RGPD — détection données personnelles
├── requirements.txt    # Dépendances Python
├── .env.example        # Modèle de configuration (à copier en .env)
├── ensa_ia.db          # Base SQLite (générée automatiquement au premier lancement)
├── audit.log           # Journal d'audit RGPD (généré automatiquement)
└── templates/
    ├── base.html           # Template de base — navbar, design, footer légal
    ├── login.html          # Page de connexion sécurisée
    ├── register.html       # Inscription avec acceptation de la politique
    ├── dashboard.html      # Tableau de bord — statistiques et accès rapides
    ├── ask.html            # Interface de requête IA avec notice de transparence
    ├── history.html        # Historique paginé des requêtes
    ├── history_detail.html # Détail complet d'une requête
    ├── my_data.html        # Portail RGPD — accès, export, effacement
    ├── admin.html          # Panneau de supervision humaine
    ├── admin_users.html    # Gestion des utilisateurs et comptes bloqués
    ├── legal.html          # Mentions légales et information RGPD
    └── politique.html      # Politique d'utilisation du système
```

## Installation et Lancement

### Prérequis
- Python 3.9 ou supérieur
- pip

### Étape 1 — Préparation
```powershell
# Windows PowerShell
cd ensa_ia

# Créer l'environnement virtuel
python -m venv venv
venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt
pip install python-dotenv
```

### Étape 2 — Configuration
```powershell
# Copier le fichier de config
copy .env.example .env

# Ouvrir et éditer .env
notepad .env
```

Contenu du fichier `.env` :
```
SECRET_KEY=votre_cle_secrete_ici
GROQ_API_KEY=gsk_votre_cle_groq_ici
FLASK_ENV=development
FLASK_DEBUG=1
```

Obtenir une clé Groq gratuite : **https://console.groq.com** → API Keys → Create

### Étape 3 — Migration de la base
```powershell
python -c "from database import migrate_db; migrate_db()"
```

### Étape 4 — Lancement
```powershell
python app.py
```

Application accessible sur :
- Local : **http://127.0.0.1:5000**
- Réseau : **http://[votre-ip]:5000**

---

## Comptes par défaut

| Identifiant | Mot de passe | Rôle |
|-------------|--------------|------|
| `admin` | `Admin@ENSA2025` | Administrateur |

> ⚠️ **Changez ce mot de passe immédiatement en production !**

Pour créer un compte étudiant ou personnel : `/register`

---

## Guide de Test Rapide

| Question à soumettre | Résultat attendu |
|---------------------|------------------|
| `Présente l'ENSA de Béni Mellal` | 4 filières + coordinateurs |
| `C'est quoi la filière IACS ?` |  IA/Cybersécurité |
| `Explique le machine learning` | Réponse complète via Groq |
| `Mon email est test@gmail.com` | Bloqué — données personnelles |
| `Parle des maladies cardiaques` | Signalé dans /admin |
| `Comment intégrer l'ENSA ?` | Concours national, 200 places |

---

## Conformité RGPD — Checklist

| Critère | Implémentation | Statut |
|---------|----------------|--------|
| Bases légales identifiées | Mission d'intérêt public (Art. 6.1.e) | ✅ |
| Droits des personnes garantis | Portail /my-data complet | ✅ |
| Mesures de sécurité | PBKDF2, sessions, rate limit | ✅ |
| Responsabilité attribuée | Rôles admin/DPO définis | ✅ |
| Risques éthiques analysés | Matrice des risques dans le rapport | ✅ |
| Supervision humaine | Panneau admin avec 4 actions | ✅ |
| Transparence assurée | Notice IA sur chaque requête | ✅ |
| Durées de conservation | Purge 6 mois automatique | ✅ |
| Journalisation | audit.log complet | ✅ |
| Filtre données personnelles | compliance.py — 7 patterns | ✅ |

---

## Stack Technique

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| Backend | Python Flask | Framework léger, open source |
| Base de données | SQLite | Pas de serveur requis, portable |
| IA | Llama 3.1 via Groq API | Gratuit, performant, open source |
| Hachage mots de passe | PBKDF2-SHA256 (Werkzeug) | Standard de sécurité éprouvé |
| Frontend | HTML/CSS vanilla | Pas de dépendance JS externe |
| Configuration | python-dotenv | Séparation code/configuration |

Toutes les technologies utilisées sont **open source**, conformément aux exigences du projet.

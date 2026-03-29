# Système IA Responsable — ENSA Béni Mellal
### Conforme RGPD / Loi marocaine 09-08 / Éthique IA

Projet pédagogique — Module Éthique et Droit du Numérique  
Filière : Intelligence Artificielle et Cybersécurité

---

## Structure du projet

```
ensa_ia/
├── app.py              # Application Flask principale (routes, auth, RGPD)
├── database.py         # Gestion SQLite + purge automatique RGPD
├── ai_service.py       # Service de génération IA (Anthropic API + fallback local)
├── compliance.py       # Filtre RGPD : détection données personnelles
├── requirements.txt    # Dépendances Python
├── .env.example        # Variables d'environnement (copier en .env)
├── ensa_ia.db          # Base de données SQLite (générée automatiquement)
├── audit.log           # Journal d'audit (généré automatiquement)
└── templates/
    ├── base.html       # Template de base (navbar, design, footer)
    ├── login.html      # Page de connexion
    ├── register.html   # Page d'inscription
    ├── dashboard.html  # Tableau de bord
    ├── ask.html        # Formulaire de requête IA
    ├── history.html    # Historique paginé
    ├── history_detail.html  # Détail d'une requête
    ├── my_data.html    # Droits RGPD (accès, export, effacement)
    ├── admin.html      # Panneau d'administration
    ├── legal.html      # Mentions légales
    └── politique.html  # Politique d'utilisation
```

---

## Installation et lancement

### 1. Prérequis
- Python 3.9+
- pip

### 2. Installation

```bash
# Cloner / copier le dossier ensa_ia
cd ensa_ia

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copier le fichier de configuration
cp .env.example .env

# Éditer .env et renseigner :
#   - SECRET_KEY (générer avec : python -c "import secrets; print(secrets.token_hex(32))")
#   - ANTHROPIC_API_KEY (optionnel — obtenir sur https://console.anthropic.com)
```

### 4. Lancement

```bash
python app.py
```

L'application est accessible sur : **http://localhost:5000**

### 5. Compte administrateur par défaut

| Identifiant | Mot de passe     |
|-------------|------------------|
| `admin`     | `Admin@ENSA2025` |

> ⚠️ **Changez ce mot de passe immédiatement en production !**

---

## Fonctionnalités

### Conformité RGPD
- ✅ Authentification sécurisée (bcrypt)
- ✅ Journalisation de toutes les actions (audit.log)
- ✅ Filtre automatique des données personnelles
- ✅ Droits RGPD : accès, export JSON, effacement
- ✅ Purge automatique après 6 mois
- ✅ Mentions légales et politique d'utilisation
- ✅ Notice de transparence IA obligatoire

### Gouvernance IA
- ✅ Aucune décision automatisée (Art. 22 RGPD)
- ✅ Disclaimer sur chaque réponse IA
- ✅ Panneau admin de supervision humaine
- ✅ Rate limiting (30 requêtes/heure/utilisateur)
- ✅ Signalement automatique des contenus sensibles

### Interface
- ✅ Design sombre professionnel
- ✅ Tableau de bord avec statistiques
- ✅ Historique paginé avec détails
- ✅ Export des données (portabilité)

---

## Modes de fonctionnement

### Mode avec API Anthropic (recommandé)
Configurez `ANTHROPIC_API_KEY` dans `.env`. Le système utilise Claude claude-haiku-4-5-20251001.

### Mode hors-ligne (sans clé API)
Le système fonctionne avec une logique locale simple — idéal pour les démos et les tests.

---

## Conformité RGPD — Checklist

| Critère | Statut |
|---------|--------|
| Bases légales identifiées | ✅ |
| Droits des personnes garantis | ✅ |
| Mesures de sécurité définies | ✅ |
| Responsabilité clairement attribuée | ✅ |
| Risques éthiques analysés | ✅ |
| Supervision humaine prévue | ✅ |
| Transparence assurée | ✅ |
| Durées de conservation respectées | ✅ |

---

## Auteurs

Filière Intelligence Artificielle et Cybersécurité  
ENSA Béni Mellal — Université Sultan Moulay Slimane  
Module : Éthique et Droit du Numérique — Pr. TOUIL

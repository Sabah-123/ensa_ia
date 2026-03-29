# Système IA Responsable — ENSA Béni Mellal
### Assistant Pédagogique Intelligent & Conforme RGPD / Loi 09-08

**Projet pédagogique** — Module Éthique et Droit du Numérique  
**Filière :** Intelligence Artificielle et Cybersécurité (IACS)  
**Encadrant :** Pr. TOUIL  
**Établissement :** ENSA Béni Mellal — Université Sultan Moulay Slimane  

---

## Description du Projet

Ce système est une **application web d'assistance pédagogique par intelligence artificielle**, conçue et développée dans le cadre du module Éthique et Droit du Numérique (EDN) de la filière IACS à l'ENSA de Béni Mellal.

L'objectif est de démontrer qu'il est possible de déployer un système IA utile tout en respectant rigoureusement les principes du RGPD, la loi marocaine 09-08 sur la protection des données personnelles, et les exigences éthiques de gouvernance IA.

### Ce que fait l'application

L'application permet aux étudiants et au personnel de l'ENSA de :
- Poser des questions académiques et obtenir des réponses générées par IA (Llama 3.1 via Groq)
- Soumettre des textes à résumer ou analyser
- Consulter l'historique de leurs requêtes
- Exercer leurs droits RGPD directement depuis l'interface

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

---

## Fonctionnalités Détaillées

### 1. Intelligence Artificielle
- **Modèle** : Llama 3.1 8B Instant via l'API Groq (gratuit)
- **Connaissance spécialisée** : l'assistant connaît l'ENSA-BM, ses 4 filières (G2ER, IAA, IACS, TDI), les coordinateurs, le cycle préparatoire et le module EDN
- **Fallback local** : si l'API est indisponible, un assistant local répond aux questions sur l'ENSA-BM
- **Disclaimer obligatoire** : chaque réponse IA inclut un avertissement de vérification humaine (RGPD Art. 13)

### 2. Conformité RGPD — Filtre de données personnelles
Le module `compliance.py` analyse chaque requête avant l'envoi à l'IA :

**Données bloquées (requête refusée) :**
- Adresses email (regex)
- Numéros de téléphone marocains (+212, 06xx, 07xx)
- Numéros CIN marocains (A-Z + chiffres)
- Numéros de carte bancaire
- Mots de passe apparents
- Coordonnées GPS
- Noms et prénoms complets (Prénom NOM)

**Données signalées (requête passée, admin alerté) :**
- Données sensibles (santé, religion, origine ethnique, judiciaire)
- Adresses physiques
- Dates de naissance

### 3. Authentification et Sécurité
- Mots de passe hachés avec **PBKDF2-SHA256** (600 000 itérations) via Werkzeug
- Sessions sécurisées avec cookie HttpOnly et SameSite
- Sessions expirées après 2 heures d'inactivité
- Vérification du statut du compte à chaque connexion (comptes bloqués refusés)
- Rate limiting : 30 requêtes maximum par heure et par utilisateur

### 4. Journalisation d'Audit (RGPD Art. 5 — Accountability)
Toutes les actions sont enregistrées dans `audit.log` :

| Action | Déclencheur |
|--------|-------------|
| LOGIN_SUCCESS | Connexion réussie |
| LOGIN_FAILED | Tentative échouée |
| LOGIN_BLOCKED | Compte suspendu tente de se connecter |
| LOGOUT | Déconnexion |
| REGISTER | Création de compte |
| ASK | Requête IA soumise |
| COMPLIANCE_BLOCK | Données personnelles détectées et bloquées |
| HISTORY_VIEW | Consultation de l'historique |
| RGPD_ACCESS_REQUEST | Accès à "Mes données" |
| RGPD_EXPORT | Export JSON des données |
| RGPD_DELETE_ALL | Effacement complet de l'historique |
| ADMIN_VIEW | Accès panneau admin |
| ADMIN_VALIDATE | Admin valide une requête signalée |
| ADMIN_WARN_USER | Admin envoie un avertissement |
| ADMIN_DELETE | Admin supprime une requête |
| ADMIN_BLOCK_USER | Admin suspend un compte |
| ADMIN_UNBLOCK | Admin réactive un compte |
| RATE_LIMIT | Quota horaire atteint |

### 5. Droits RGPD (Articles 15, 17, 20, 22)
Disponibles dans `/my-data` :
- **Art. 15 — Droit d'accès** : tableau complet des données collectées, finalités, durées de conservation, contact DPO
- **Art. 20 — Portabilité** : export de l'historique au format JSON téléchargeable
- **Art. 17 — Effacement** : suppression définitive et immédiate de tout l'historique
- **Art. 22 — Décision non automatisée** : aucune décision administrative n'est prise par l'IA — validation humaine systématique

### 6. Supervision Humaine — Panneau Admin
L'administrateur accède à `/admin` et peut agir sur chaque requête signalée :
- **Valider** : contenu jugé acceptable, flag archivé
- **Avertir l'utilisateur** : avertissement formel enregistré dans la table `warnings`
- **Supprimer** : effacement définitif de la requête
- **Bloquer le compte** : suspension immédiate de l'accès

Depuis `/admin/users`, l'admin voit tous les utilisateurs avec leur nombre de requêtes, de signalements, et peut réactiver les comptes bloqués.

### 7. Conservation des données (RGPD Art. 5.1.e)
- Historique des requêtes : **6 mois** (purge automatique)
- Journaux d'audit : **12 mois**
- Données de compte : durée de la scolarité ou du contrat

---

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
| `C'est quoi la filière IACS ?` | Pr. GOUSKIR + IA/Cybersécurité |
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

---

## Informations sur l'ENSA-BM

| Filière | Coordinateur | Spécialité |
|---------|--------------|------------|
| G2ER | Pr. OULCAID MOSTAPHA | Génie Électrique & Énergies Renouvelables |
| IAA | Pr. ROKNI YAHYA | Industries Agroalimentaires |
| IACS | Pr. GOUSKIR MOHAMED | Intelligence Artificielle & Cybersécurité |
| TDI | Pr. OUANAN HAMID | Transformation Digitale Industrielle |

Cycle Préparatoire : Pr. KAAB MOHAMED — 200 places — Concours national

---

*ENSA Béni Mellal — Université Sultan Moulay Slimane*  
*Module EDN — Éthique et Droit du Numérique — Pr. TOUIL*  
*Filière IACS — Année universitaire 2024–2025*

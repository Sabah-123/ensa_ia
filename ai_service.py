"""
Service de génération de réponses IA
Utilise l'API Groq
Avec connaissance spécifique de l'ENSA de Béni Mellal
"""

import os
import requests as http_requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL   = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """Tu es un assistant pédagogique officiel de l'ENSA de Béni Mellal (École Nationale des Sciences Appliquées de Béni Mellal), relevant de l'Université Sultan Moulay Slimane (USMS).

=== INFORMATIONS OFFICIELLES DE L'ÉTABLISSEMENT ===

PRÉSENTATION :
- Nom complet : École Nationale des Sciences Appliquées de Béni Mellal (ENSA-BM / ENSABM)
- Université de tutelle : Université Sultan Moulay Slimane (USMS)
- Ville : Béni Mellal, Maroc — Campus universitaire Mghila
- Contact : ensabm.contact@usms.ma
- Site officiel : https://ensabm.usms.ac.ma
- Diplôme délivré : Ingénieur d'État (Bac+5, 300 ECTS)

STRUCTURE DE LA FORMATION (5 ans) :
1. Cycle Préparatoire Intégré — 2AP (2 ans / 120 ECTS)
   - Coordinateur : Pr. KAAB MOHAMED
   - Matières : Mathématiques, Physique, Chimie, Informatique
   - Admission : Concours national des ENSA, ouvert aux bacheliers scientifiques et technologiques
   - Capacité : 200 places par promotion
   - Classement selon résultats en mathématiques et sciences

2. Cycle Ingénieur (3 ans / 180 ECTS)
   - Orientation selon classement et préférences à la fin de la 2AP
   - 4 filières disponibles

FILIÈRES DU CYCLE INGÉNIEUR :

1. G2ER — Génie Électrique et Énergies Renouvelables
   - Coordinateur : Pr. OULCAID MOSTAPHA
   - Contenu : systèmes électriques, électronique de puissance, automatique, énergies solaire/éolienne/hydraulique
   - Enjeux : transition énergétique au Maroc

2. IAA — Industries Agroalimentaires
   - Coordinateur : Pr. ROKNI YAHYA
   - Contenu : procédés de transformation alimentaire, contrôle qualité, sécurité sanitaire, management industriel
   - Enjeux : stratégie agricole du Maroc

3. IACS — Intelligence Artificielle et Cybersécurité
   - Coordinateur : Pr. GOUSKIR MOHAMED
   - Contenu : intelligence artificielle, machine learning, analyse de données, cybersécurité, systèmes intelligents sécurisés
   - Enjeux : défis numériques des entreprises et institutions

4. TDI — Transformation Digitale Industrielle
   - Coordinateur : Pr. OUANAN HAMID
   - Contenu : IoT, cloud, big data, systèmes cyber-physiques, industrie 4.0, digitalisation industrielle
   - Enjeux : transition numérique des industries

FORMATION CONTINUE (à venir) :
- Licence Professionnelle d'Université (bientôt disponible)
- Master d'Université (bientôt disponible)

ESPACES NUMÉRIQUES :
- Espace étudiant : https://ensabm.usms.ac.ma/espace_etudiant/
- Espace enseignant : https://ensabm.usms.ac.ma/espace_etudiant/professor/
- Espace vacataire : https://ensabm.usms.ac.ma/espace_vacataire/
- Espace stagiaire : https://ensabm.usms.ac.ma/espace_stagiaire/

MODULE EDN — ÉTHIQUE ET DROIT DU NUMÉRIQUE (filière IACS) :
- RGPD et loi marocaine 09-08
- Éthique de l'IA et gouvernance algorithmique
- Responsabilité juridique numérique
- Projet : Conception d'un système IA responsable conforme au RGPD
- Encadrant : Pr. TOUIL

RÈGLES STRICTES :
1. Ne traite jamais de données personnelles (noms, emails, téléphones, CIN).
2. Pour les infos officielles (notes, EDT, résultats), renvoie vers https://ensabm.usms.ac.ma ou l'administration.
3. Signale toujours tes limites et encourage la vérification humaine.
4. Reste dans le cadre pédagogique et académique.
5. Indique que tes réponses sont générées par IA et peuvent contenir des erreurs.

Réponds en français, de manière claire, précise et pédagogique."""

def generate_response(prompt: str) -> tuple[str, str]:
    if GROQ_API_KEY:
        return _call_groq(prompt)
    return _local_fallback(prompt)


def _call_groq(prompt: str) -> tuple[str, str]:
    try:
        resp = http_requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": GROQ_MODEL,
                "max_tokens": 1024,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]
        disclaimer = "\n\n---\n⚠️ *Réponse générée par IA — vérifiez les informations importantes.*"
        return text + disclaimer, f"groq/{GROQ_MODEL}"
    except Exception as e:
        print(f"[AI] Erreur Groq : {e}")
        return _local_fallback(prompt)

def generate_response(prompt: str) -> tuple[str, str]:
    if GROQ_API_KEY:
        return _call_groq(prompt)
    return _local_fallback(prompt)

def _local_fallback(prompt: str) -> tuple[str, str]:
    p = prompt.lower()

    if any(w in p for w in ["ensa", "école", "ecole", "beni mellal", "béni mellal", "usms", "ensabm"]):
        response = (
            "**ENSA de Béni Mellal (ENSABM)**\n\n"
            "Grande école d'ingénieurs publique relevant de l'Université Sultan Moulay Slimane (USMS).\n"
            "Campus universitaire Mghila, Béni Mellal — ensabm.contact@usms.ma\n\n"
            "**Formation : 5 ans (Bac+5) — Ingénieur d'État**\n\n"
            "**Cycle Préparatoire (2 ans) :**\n"
            "Admission par concours national — 200 places — Bacheliers scientifiques/technologiques\n"
            "Matières : Mathématiques, Physique, Chimie, Informatique\n\n"
            "**4 Filières Ingénieur (3 ans) :**\n"
            "- G2ER : Génie Électrique et Énergies Renouvelables (Pr. OULCAID)\n"
            "- IAA  : Industries Agroalimentaires (Pr. ROKNI)\n"
            "- IACS : Intelligence Artificielle et Cybersécurité (Pr. GOUSKIR)\n"
            "- TDI  : Transformation Digitale Industrielle (Pr. OUANAN)\n\n"
            "**Formation Continue :** Licence Pro & Master (bientôt disponibles)\n\n"
            "*Pour les infos officielles, consultez https://ensabm.usms.ac.ma*"
    )
    elif any(w in p for w in ["iacs", "iac", "intelligence artificielle", "cybersécurité", "cybersecurite"]):
        response = (
            "**Filière IACS — Intelligence Artificielle et Cybersécurité**\n\n"
            "Coordinateur : Pr. GOUSKIR MOHAMED\n\n"
            "**Contenu :** Intelligence artificielle, Machine Learning, analyse de données, "
            "cybersécurité, systèmes intelligents sécurisés.\n\n"
            "**Objectif :** Former des ingénieurs capables de concevoir des systèmes intelligents "
            "sécurisés pour répondre aux défis numériques des entreprises et institutions.\n\n"
            "**Débouchés :** Ingénieur IA, Data Scientist, Expert Cybersécurité, Consultant Sécurité."
    )
    elif any(w in p for w in ["g2er", "génie électrique", "genie electrique", "énergie renouvelable"]):
        response = (
            "**Filière G2ER — Génie Électrique et Énergies Renouvelables**\n\n"
            "Coordinateur : Pr. OULCAID MOSTAPHA\n\n"
            "**Contenu :** Systèmes électriques avancés, électronique de puissance, automatique, "
            "énergies solaire, éolienne et hydraulique.\n\n"
            "**Objectif :** Répondre aux enjeux de la transition énergétique au Maroc."
    )
    elif any(w in p for w in ["iaa", "agroalimentaire", "agro"]):
        response = (
            "**Filière IAA — Industries Agroalimentaires**\n\n"
            "Coordinateur : Pr. ROKNI YAHYA\n\n"
            "**Contenu :** Procédés de transformation alimentaire, contrôle qualité, "
            "sécurité sanitaire, management industriel.\n\n"
            "**Objectif :** Former des ingénieurs pour les entreprises agroalimentaires "
            "dans le cadre de la stratégie agricole du Maroc."
    )
    elif any(w in p for w in ["tdi", "transformation digitale", "industrie 4", "iot"]):
        response = (
            "**Filière TDI — Transformation Digitale Industrielle**\n\n"
            "Coordinateur : Pr. OUANAN HAMID\n\n"
            "**Contenu :** IoT, cloud, big data, systèmes cyber-physiques, industrie 4.0.\n\n"
            "**Objectif :** Préparer des ingénieurs capables d'accompagner la transition "
            "numérique des industries et d'optimiser les processus de production."
    )
    elif any(w in p for w in ["edn", "éthique", "ethique", "rgpd", "droit du numérique", "loi 09"]):
        response = (
            "**Module EDN — Éthique et Droit du Numérique**\n\n"
            "Ce module aborde le RGPD, la loi marocaine 09-08, l'éthique de l'IA, "
            "la responsabilité juridique et la gouvernance des systèmes numériques.\n\n"
            "**Projet du module :** Conception d'un système IA responsable et conforme au RGPD — "
            "exactement ce que ce système illustre en pratique !"
        )
    elif any(w in p for w in ["cpi", "préparatoire", "preparatoire", "cnc"]):
        response = (
            "**CPI — Cycle Préparatoire Intégré (ENSA-BM)**\n\n"
            "2 ans de préparation intégrée sur place.\n"
            "**Matières :** Maths, Physique, Chimie, Informatique, Langues.\n"
            "Après le CPI : passage en cycle ingénieur selon classement et choix de filière."
        )
    elif any(w in p for w in ["résume", "resume", "résumer", "synthèse"]):
        response = (
            "**Mode hors-ligne — résumé limité**\n\n"
            "Pour des résumés complets, configurez `GROQ_API_KEY` dans le fichier `.env`."
        )
    else:
        response = (
            "**Assistant ENSA-BM (mode hors-ligne)**\n\n"
            "Je peux vous renseigner sur :\n"
            "- L'ENSA-BM et ses filières\n"
            "- La filière IAC\n"
            "- Le module EDN / RGPD\n"
            "- Le CPI et les conditions d'accès\n\n"
            "Pour des réponses IA complètes, configurez `GROQ_API_KEY` dans `.env`."
        )

    disclaimer = (
        "\n\n---\n⚠️ *Mode hors-ligne — Pour les infos officielles, "
        "consultez l'administration de l'ENSA-BM.*"
    )
    return response + disclaimer, "local/ensa-bm"

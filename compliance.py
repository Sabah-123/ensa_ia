"""
Module de vérification de conformité RGPD
Filtre les données personnelles et sensibles (Art. 5 & 9 RGPD)
"""

import re

# ─── Patterns de détection de données personnelles ───────────────────────────

PATTERNS_BLOCKED = {
    "numéro CIN marocain":     r"\b[A-Z]{1,2}\d{5,7}\b",
    "numéro de téléphone":     r"\b(?:(?:\+|00)212|0)[5-7]\d{8}\b",
    "adresse e-mail":          r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b",
    "numéro de carte bancaire":r"\b(?:\d[ -]?){13,19}\b",
    "mot de passe apparent":   r"(?i)\bpassword\s*[:=]\s*\S+",
    "coordonnées GPS":         r"\b-?\d{1,3}\.\d{4,},\s*-?\d{1,3}\.\d{4,}\b",
    "numéro de sécurité sociale": r"\b[12]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}\b",
    "prénom + nom complet":     r"\b[A-Z][a-zéèêëàâîïôùûü]{2,} [A-Z]{2,}\b",
}

PATTERNS_WARNED = {
    "adresse physique":        r"(?i)\b(?:rue|avenue|bd|boulevard|quartier|hay)\s+\w+",
    "date de naissance":       r"\b(?:né|née|naissance)[^\n]*\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}",
}

KEYWORDS_BLOCKED = [
    "mon mot de passe", "my password", "code secret", "code pin",
    "numéro cin", "numéro cni", "numéro passeport",
]

KEYWORDS_SENSITIVE = [
    "santé", "maladie", "handicap", "religion", "politique", "sexualité",
    "origine ethnique", "condamnation", "judiciaire",
]


def check_compliance(text: str) -> dict:
    """
    Analyse le texte pour détecter des données personnelles ou sensibles.
    
    Retourne :
      - blocked  (bool)  : True si la saisie doit être bloquée
      - warned   (bool)  : True si une alerte non-bloquante est émise
      - reason   (str)   : Raison du blocage
      - warning  (str)   : Message d'avertissement
    """
    result = {"blocked": False, "warned": False, "reason": "", "warning": ""}

    # 1. Mots-clés bloquants
    text_lower = text.lower()
    for kw in KEYWORDS_BLOCKED:
        if kw in text_lower:
            result["blocked"] = True
            result["reason"]  = f"Mot-clé sensible détecté : « {kw} »"
            return result

    # 2. Patterns bloquants (données personnelles directes)
    for label, pattern in PATTERNS_BLOCKED.items():
        if re.search(pattern, text):
            result["blocked"] = True
            result["reason"]  = f"Donnée personnelle détectée : {label}"
            return result

    # 3. Données sensibles (catégories spéciales Art. 9 RGPD)
    for kw in KEYWORDS_SENSITIVE:
        if kw in text_lower:
            result["warned"]  = True
            result["warning"] = (
                f"Votre message semble contenir des données sensibles (« {kw} »). "
                "Assurez-vous de ne pas divulguer d'informations personnelles confidentielles."
            )
            return result

    # 4. Patterns d'avertissement (données indirectes)
    for label, pattern in PATTERNS_WARNED.items():
        if re.search(pattern, text):
            result["warned"]  = True
            result["warning"] = (
                f"Attention : votre texte pourrait contenir {label}. "
                "Ne saisissez pas de données personnelles identifiables."
            )
            return result

    return result


def anonymize_text(text: str) -> str:
    """
    Anonymise un texte en remplaçant les données personnelles détectées.
    Utilisé pour les logs d'audit (principe de minimisation).
    """
    for label, pattern in PATTERNS_BLOCKED.items():
        text = re.sub(pattern, f"[{label.upper()} MASQUÉ]", text)
    return text

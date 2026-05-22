"""Filtre de vocabulaire AMF (apprentissage #3).

Détecte les termes promettant un résultat, déconseillés dans une communication
financière conforme AMF. À enrichir avec le contenu de SPEC.md (section 7).
"""

import re

TERMES_DECONSEILLES = [
    "garantir",
    "garanti",
    "sécuriser",
    "optimiser le rendement",
]


def detecter_termes(texte: str) -> list[str]:
    """Retourne la liste des termes déconseillés trouvés dans le texte."""
    trouves = []
    minuscule = texte.lower()
    for terme in TERMES_DECONSEILLES:
        if re.search(rf"\b{re.escape(terme)}\b", minuscule):
            trouves.append(terme)
    return trouves


def est_conforme(texte: str) -> bool:
    return not detecter_termes(texte)

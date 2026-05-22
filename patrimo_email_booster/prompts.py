"""Construction du prompt système (règles métier + date courante).

Implémente les apprentissages #1 (réponse explicite à l'objection) et #2
(injection de la date courante). Le contenu détaillé sera finalisé avec
SPEC.md (section 6).
"""

from datetime import date

from .models import ParamsGeneration, Prospect


def construire_prompt_systeme(aujourd_hui: date | None = None) -> str:
    aujourd_hui = aujourd_hui or date.today()
    # TODO (post-SPEC) : rédiger le prompt système complet.
    #  - injecter la date : {aujourd_hui.isoformat()}
    #  - imposer reformulation + réponse spécifique à l'objection
    #  - interdire le vocabulaire AMF déconseillé (voir compliance.py)
    raise NotImplementedError


def construire_prompt_utilisateur(prospect: Prospect, params: ParamsGeneration) -> str:
    # TODO (post-SPEC) : assembler les données prospect + paramètres.
    raise NotImplementedError

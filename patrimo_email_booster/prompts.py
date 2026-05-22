"""Construction des prompts (système commun + prompt utilisateur par variante).

Découpage (cf. SPEC §6 et §8) :
- Le prompt **système** est identique aux 3 appels API : rôle, règles métier,
  date courante, interdits AMF, forme et format de sortie attendu.
- Le prompt **utilisateur** porte ce qui varie d'une variante à l'autre :
  fiche prospect, angle (A/B/C), ton effectif, longueur et signature.
"""

from datetime import date
from enum import Enum

from .compliance import TERMES_DECONSEILLES
from .models import ParamsGeneration, Prospect


class Variante(Enum):
    """Les trois angles de relance (SPEC §5)."""

    A = "objection"
    B = "situation"
    C = "situation_empathie"


# Repères de longueur donnés au modèle (SPEC §4), en nombre de mots du corps.
LONGUEURS = {
    "court": "environ 80 à 120 mots",
    "moyen": "environ 150 à 200 mots",
    "long": "environ 250 à 300 mots",
}


def construire_prompt_systeme(aujourd_hui: date | None = None) -> str:
    """Prompt système commun aux 3 variantes (règles métier SPEC §6 et §7)."""
    aujourd_hui = aujourd_hui or date.today()
    interdits = ", ".join(f"« {t} »" for t in TERMES_DECONSEILLES)

    return f"""Tu es un assistant de rédaction pour un conseiller en gestion de \
patrimoine (CGP) français. Tu rédiges des emails de relance personnalisés à \
destination de ses prospects. Tu écris exclusivement en français, au \
vouvoiement.

RÈGLES IMPÉRATIVES :

1. Personnalisation obligatoire. Appuie-toi sur les champs de la fiche prospect \
(nom, situation, objection). Ne produis jamais un email générique qui pourrait \
s'appliquer à n'importe qui.

2. Date courante : nous sommes le {aujourd_hui.isoformat()}. Calcule le temps \
écoulé depuis le dernier contact à partir de cette date. N'invente aucune date \
et ne fais aucune supposition temporelle qui ne découle pas de ce repère.

3. Conformité AMF. Une communication financière ne doit promettre aucun \
résultat ni employer de langage trompeur. N'emploie jamais les termes suivants \
ni leurs équivalents promettant un rendement ou une absence de risque : \
{interdits}.

4. Forme : objet d'email explicite, vouvoiement, appel à l'action mesuré \
(proposer un échange, jamais forcer ni mettre la pression). Termine par la \
signature qui te sera fournie.

FORMAT DE SORTIE — réponds STRICTEMENT selon ce gabarit, sans texte autour :

OBJET: <objet de l'email>
CORPS:
<corps de l'email, signature comprise>
"""


def construire_prompt_utilisateur(
    prospect: Prospect, params: ParamsGeneration, variante: Variante
) -> str:
    """Prompt utilisateur d'une variante : fiche prospect + consigne d'angle."""
    longueur = LONGUEURS.get(params.longueur, LONGUEURS["moyen"])

    fiche = (
        "FICHE PROSPECT :\n"
        f"- Nom : {prospect.nom}\n"
        f"- Situation : {prospect.situation}\n"
        f"- Dernier contact : {prospect.dernier_contact}\n"
        f"- Objection exprimée : {prospect.objection}"
    )

    return (
        f"{fiche}\n\n"
        f"{_consigne_angle(variante, prospect, params)}\n\n"
        f"Longueur attendue du corps : {longueur}.\n"
        f"Signe l'email avec : {params.signature}"
    )


def _consigne_angle(
    variante: Variante, prospect: Prospect, params: ParamsGeneration
) -> str:
    """Consigne spécifique à l'angle (SPEC §5)."""
    if variante is Variante.A:
        objection = params.objection or prospect.objection
        return (
            "ANGLE — Accroche par l'objection.\n"
            f"Reformule explicitement l'objection suivante : « {objection} », "
            "puis réponds-y de front. Ne l'évite pas, ne la minimise pas et ne "
            "la contourne pas.\n"
            f"Ton : {params.ton}."
        )

    if variante is Variante.B:
        return (
            "ANGLE — Accroche par la situation.\n"
            "Accroche sur le contexte patrimonial et le moment de vie du "
            f"prospect (« {prospect.situation} ») pour montrer que tu comprends "
            "sa situation.\n"
            f"Ton : {params.ton}."
        )

    # Variante.C
    return (
        "ANGLE — Accroche par la situation, registre empathique renforcé.\n"
        "Reprends la même accroche situationnelle que la variante B (« "
        f"{prospect.situation} »), mais dans un registre nettement plus "
        "chaleureux et empathique. C'est la variante au plus fort contraste "
        "émotionnel du lot : l'empathie prime sur tout autre ton."
    )

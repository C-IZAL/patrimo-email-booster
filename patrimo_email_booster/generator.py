"""Appel au SDK Anthropic et production des 3 variantes d'email.

Découplé de l'interface : réutilisable par la CLI et la future UI Streamlit.
Décision SPEC §8 : une génération API par variante (3 appels), chacune avec son
prompt d'angle dédié.
"""

import re

import anthropic
from anthropic import Anthropic

from .compliance import detecter_termes
from .config import get_api_key, get_model
from .models import ParamsGeneration, Prospect, Variante, VarianteGeneree
from .prompts import TITRES, construire_prompt_systeme, construire_prompt_utilisateur

# Marge suffisante pour la variante la plus longue (~300 mots + objet).
MAX_TOKENS = 1024

# Capture "OBJET: ...\nCORPS:\n..." en tolérant casse et espaces (SPEC §5).
_GABARIT = re.compile(
    r"OBJET\s*:\s*(.+?)\s*CORPS\s*:\s*(.*)", re.DOTALL | re.IGNORECASE
)


class ErreurGeneration(RuntimeError):
    """Échec d'un appel au SDK Anthropic, enveloppé avec son contexte."""


class FormatReponseError(ValueError):
    """La réponse du modèle ne respecte pas le gabarit OBJET:/CORPS:."""


def parser_sortie(texte: str) -> tuple[str, str]:
    """Extrait (objet, corps) du gabarit imposé. Lève FormatReponseError sinon."""
    correspondance = _GABARIT.search(texte.strip())
    if not correspondance:
        raise FormatReponseError(
            "Réponse du modèle hors gabarit : marqueurs OBJET:/CORPS: introuvables."
        )
    objet = correspondance.group(1).strip()
    corps = correspondance.group(2).strip()
    if not objet or not corps:
        raise FormatReponseError("Objet ou corps vide après parsing de la réponse.")
    return objet, corps


def _extraire_texte(message: anthropic.types.Message) -> str:
    """Concatène les blocs texte de la réponse SDK."""
    return "".join(bloc.text for bloc in message.content if bloc.type == "text")


def generer_variante(
    client: Anthropic,
    modele: str,
    prompt_systeme: str,
    prospect: Prospect,
    params: ParamsGeneration,
    variante: Variante,
) -> VarianteGeneree:
    """Un appel API + parsing + contrôle de conformité pour une variante."""
    prompt_utilisateur = construire_prompt_utilisateur(prospect, params, variante)
    try:
        message = client.messages.create(
            model=modele,
            max_tokens=MAX_TOKENS,
            system=prompt_systeme,
            messages=[{"role": "user", "content": prompt_utilisateur}],
        )
    except anthropic.APIError as e:
        raise ErreurGeneration(
            f"Échec de génération (variante {variante.name}) : {e}"
        ) from e

    objet, corps = parser_sortie(_extraire_texte(message))
    termes = detecter_termes(f"{objet}\n{corps}")
    return VarianteGeneree(
        variante=variante,
        titre=TITRES[variante],
        objet=objet,
        corps=corps,
        termes_non_conformes=termes,
    )


def generer_variantes(
    prospect: Prospect,
    params: ParamsGeneration,
    *,
    client: Anthropic | None = None,
) -> list[VarianteGeneree]:
    """Génère les 3 variantes d'email de relance (boucle sur l'enum Variante)."""
    client = client or Anthropic(api_key=get_api_key())
    modele = get_model()
    prompt_systeme = construire_prompt_systeme()
    return [
        generer_variante(client, modele, prompt_systeme, prospect, params, variante)
        for variante in Variante
    ]

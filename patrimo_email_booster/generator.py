"""Appel au SDK Anthropic et production des 3 variantes d'email.

Découplé de l'interface : réutilisable par la CLI et la future UI Streamlit.
Le détail (format de sortie, parsing des 3 variantes) sera finalisé avec
SPEC.md (section 5).
"""

from .models import ParamsGeneration, Prospect


def generer_variantes(prospect: Prospect, params: ParamsGeneration) -> list[str]:
    """Génère 3 variantes d'email de relance pour le prospect."""
    # TODO (post-SPEC) : appeler le client Anthropic et retourner 3 variantes.
    raise NotImplementedError

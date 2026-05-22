"""Chargement de la configuration depuis l'environnement (.env)."""

import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "claude-sonnet-4-6"


def get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY manquante. Copiez .env.example en .env et "
            "renseignez votre clé."
        )
    return key


def get_model() -> str:
    return os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)

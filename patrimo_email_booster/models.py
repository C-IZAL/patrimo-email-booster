"""Structures de données partagées entre la CLI et la future UI Streamlit."""

from dataclasses import dataclass
from enum import Enum


class Variante(Enum):
    """Les trois angles de relance (SPEC §5)."""

    A = "objection"
    B = "situation"
    C = "situation_empathie"


@dataclass
class Prospect:
    nom: str
    situation: str
    dernier_contact: str
    objection: str


@dataclass
class ParamsGeneration:
    ton: str = "professionnel"
    longueur: str = "moyen"
    objection: str | None = None  # objection à traiter (défaut : celle du prospect)
    signature: str = "[Votre nom]"


@dataclass
class VarianteGeneree:
    """Résultat d'une variante : objet, corps et contrôle de conformité (SPEC §5)."""

    variante: Variante
    titre: str
    objet: str
    corps: str
    termes_non_conformes: list[str]

    @property
    def est_conforme(self) -> bool:
        return not self.termes_non_conformes

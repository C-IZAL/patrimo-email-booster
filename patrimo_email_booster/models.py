"""Structures de données partagées entre la CLI et la future UI Streamlit."""

from dataclasses import dataclass


@dataclass
class Prospect:
    nom: str
    situation: str
    dernier_contact: str
    objection: str


@dataclass
class ParamsGeneration:
    ton: str = "professionnel"
    longueur: str = "moyenne"
    objection: str | None = None  # objection à traiter (défaut : celle du prospect)

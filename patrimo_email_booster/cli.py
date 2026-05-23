"""Point d'entrée CLI : lit un prospect YAML, génère et affiche 3 variantes."""

import argparse
import sys
from datetime import date
from pathlib import Path

import yaml

from .generator import ErreurGeneration, FormatReponseError, generer_variantes
from .models import ParamsGeneration, Prospect, VarianteGeneree
from .prompts import LONGUEURS, TONS

SEPARATEUR = "=" * 70


class ProspectInvalide(ValueError):
    """Fiche prospect YAML mal formée (champ manquant, date non ISO, etc.)."""


def charger_prospect(chemin: Path) -> Prospect:
    """Charge et valide une fiche prospect YAML (SPEC §3)."""
    donnees = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    if not isinstance(donnees, dict):
        raise ProspectInvalide(
            f"{chemin} : le fichier ne contient pas un dictionnaire YAML."
        )

    requis = ["nom", "situation", "dernier_contact", "objection"]
    manquants = [c for c in requis if c not in donnees]
    if manquants:
        raise ProspectInvalide(
            f"{chemin} : champs obligatoires manquants — {', '.join(manquants)}."
        )

    # PyYAML désérialise une date ISO en datetime.date — on revalide explicitement
    # pour produire un message FR clair et garantir le format AAAA-MM-JJ.
    try:
        date.fromisoformat(str(donnees["dernier_contact"]))
    except ValueError:
        raise ProspectInvalide(
            f"{chemin} : 'dernier_contact' = {donnees['dernier_contact']!r} "
            "n'est pas une date ISO (AAAA-MM-JJ)."
        ) from None

    return Prospect(
        nom=donnees["nom"],
        situation=donnees["situation"],
        dernier_contact=str(donnees["dernier_contact"]),
        objection=donnees["objection"],
    )


def construire_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Génère 3 variantes d'email de relance pour un prospect CGP."
    )
    parser.add_argument("prospect", type=Path, help="Fichier YAML du prospect.")
    parser.add_argument(
        "--ton",
        choices=TONS,
        default="professionnel",
        help="Ton des variantes A et B (défaut : professionnel).",
    )
    parser.add_argument(
        "--longueur",
        choices=list(LONGUEURS),
        default="moyen",
        help="Longueur du corps des emails (défaut : moyen).",
    )
    parser.add_argument(
        "--objection",
        default=None,
        help="Objection à traiter pour la variante A (défaut : celle du prospect).",
    )
    parser.add_argument(
        "--signature",
        default="[Votre nom]",
        help="Signature des emails (défaut : '[Votre nom]').",
    )
    return parser


def afficher_variante(variante: VarianteGeneree) -> None:
    print(SEPARATEUR)
    print(variante.titre)
    print(f"Objet : {variante.objet}\n")
    print(variante.corps)
    statut = (
        "conforme"
        if variante.est_conforme
        else f"NON conforme : {variante.termes_non_conformes}"
    )
    print(f"\n[AMF : {statut}]")


def main(argv: list[str] | None = None) -> int:
    args = construire_parser().parse_args(argv)
    try:
        prospect = charger_prospect(args.prospect)
        params = ParamsGeneration(
            ton=args.ton,
            longueur=args.longueur,
            objection=args.objection,
            signature=args.signature,
        )
        for variante in generer_variantes(prospect, params):
            afficher_variante(variante)
        print(SEPARATEUR)
        return 0
    except (
        FileNotFoundError,
        yaml.YAMLError,
        ProspectInvalide,
        RuntimeError,
        ErreurGeneration,
        FormatReponseError,
    ) as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Point d'entrée CLI : lit un prospect YAML, génère et affiche 3 variantes."""

import argparse
from pathlib import Path

import yaml

from .models import ParamsGeneration, Prospect


def charger_prospect(chemin: Path) -> Prospect:
    donnees = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    return Prospect(**donnees)


def construire_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Génère 3 variantes d'email de relance pour un prospect CGP."
    )
    parser.add_argument("prospect", type=Path, help="Fichier YAML du prospect.")
    parser.add_argument("--ton", default="professionnel")
    parser.add_argument("--longueur", default="moyenne")
    parser.add_argument("--objection", default=None, help="Objection à traiter.")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = construire_parser().parse_args(argv)
    prospect = charger_prospect(args.prospect)
    params = ParamsGeneration(
        ton=args.ton, longueur=args.longueur, objection=args.objection
    )
    # TODO (post-SPEC) : appeler generator.generer_variantes(prospect, params)
    #  puis afficher les 3 variantes.
    raise NotImplementedError


if __name__ == "__main__":
    main()

# patrimo-email-booster

Générateur d'emails de relance personnalisés pour conseillers en gestion de
patrimoine (CGP) français. Pour chaque prospect, le système produit **3 variantes**
d'email contrôlables (ton, longueur, objection à traiter), avec une conformité
AMF de base intégrée.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # puis renseignez ANTHROPIC_API_KEY
```

## Utilisation (CLI)

```bash
python -m patrimo_email_booster.cli prospects/exemple.yaml --ton chaleureux --longueur courte
```

Un prospect est décrit dans un fichier **YAML** :

```yaml
nom: Marie Durand
situation: cliente depuis 3 ans, profil prudent
dernier_contact: 2026-02-10
objection: "Je n'ai pas le temps de m'en occuper en ce moment."
```

## Modèle

Le modèle est configurable via `ANTHROPIC_MODEL` dans `.env` :
- **Haiku** pour itérer rapidement et à moindre coût,
- **Sonnet** pour la qualité de la version finale.

## Roadmap

1. CLI (actuel)
2. Interface Streamlit
3. Déploiement Streamlit Cloud

## Licence

MIT — voir [LICENSE](LICENSE).

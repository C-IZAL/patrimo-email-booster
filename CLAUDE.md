# CLAUDE.md — patrimo-email-booster

## Contexte projet
Générateur d'emails de relance personnalisés pour conseillers en gestion de
patrimoine (CGP) français. Pour chaque prospect (fichier YAML : nom, situation,
dernier_contact, objection), le système génère **3 variantes** d'email
contrôlables par des paramètres (ton, longueur, objection à traiter).
C'est le premier livrable portfolio d'une reconversion vers le métier d'AI
Growth Engineer spécialisé CGP : la qualité de code compte, mais **sans
sur-ingénierie**.

## Niche CGP
Les CGP sont des conseillers indépendants qui accompagnent des particuliers sur
l'épargne, l'investissement, la transmission et l'optimisation patrimoniale.
La relation est longue, fondée sur la confiance ; les emails de relance doivent
être personnalisés, respectueux du rythme du prospect, et jamais agressifs
commercialement. Vocabulaire métier : assurance-vie, SCPI, PER, allocation,
profil de risque, arbitrage, succession.

## Stack & structure
- Python 3.12, SDK Anthropic, python-dotenv, pyyaml.
- CLI d'abord, interface Streamlit ensuite, déploiement Streamlit Cloud à terme.
- Carte des modules (`patrimo_email_booster/`) :
  - `cli.py`        — point d'entrée argparse (lecture prospect + paramètres).
  - `config.py`     — chargement `.env`, modèle, constantes.
  - `models.py`     — dataclasses `Prospect` et `ParamsGeneration`.
  - `prompts.py`    — construction du prompt système (règles métier + date).
  - `compliance.py` — filtre vocabulaire AMF (testable unitairement).
  - `generator.py`  — appel SDK Anthropic, production des 3 variantes.
- La logique métier (`generator`, `models`, `prompts`, `compliance`) est
  découplée de l'interface : Streamlit réutilisera ces modules sans toucher au
  CLI.

## Conventions
- Contenu métier (prompts, emails, exemples) rédigé **en français**.
- Structures de données via `@dataclass`.
- Secrets uniquement via `.env` (jamais en dur, jamais commités).
- Format prospect : **YAML uniquement**.
- Modèle configurable via `ANTHROPIC_MODEL` : Haiku pour itérer, Sonnet pour la
  qualité finale.

## Conformité AMF
Principe : pas de promesse de rendement, pas de langage trompeur. Trois
apprentissages issus d'un sandbox précédent, à respecter dès le départ :
1. **Réponse explicite à l'objection** — le prompt système impose de reformuler
   l'objection du prospect puis d'y répondre spécifiquement. Jamais de
   contournement ou d'évitement de l'objection.
2. **Injection de la date courante** dans le prompt pour éviter les
   hallucinations temporelles (calcul du temps écoulé depuis le dernier contact).
3. **Filtre de vocabulaire AMF** — éviter les termes « garantir », « sécuriser »,
   « optimiser le rendement » et formulations équivalentes promettant un
   résultat. Implémenté dans `compliance.py`.

## Documentation externe (vault)
L'utilisateur maintient un second cerveau wiki LLM dans `~/vault/`. Les notes de
jalon vivent dans `~/vault/raw/notes/`.
- À chaque **fin de session substantielle**, suggérer un **titre + structure**
  de note à créer dans `~/vault/raw/notes/`.
- **Ne jamais écrire directement dans `~/vault/`** depuis ce projet.

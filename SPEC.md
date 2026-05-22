# SPEC — patrimo-email-booster

> Spécification fonctionnelle et technique du générateur d'emails de relance
> pour conseillers en gestion de patrimoine (CGP). Version 0 (CLI).

## 1. Objectif & périmètre

Générer, à partir de la fiche d'un prospect CGP, **trois variantes** d'email de
relance personnalisées, prêtes à être relues, ajustées et envoyées par le
conseiller. L'outil produit le texte ; il ne l'envoie pas.

**Dans le périmètre (v0) :** lecture d'une fiche prospect au format YAML,
génération de 3 variantes via le SDK Anthropic, contrôle de conformité AMF en
sortie, affichage structuré en ligne de commande.

**Hors périmètre (v0) :** envoi d'emails, intégration CRM, traitement par lots
de plusieurs prospects, interface graphique (prévue en v1 Streamlit).

## 2. Utilisateurs cibles

Conseillers en gestion de patrimoine indépendants et petits cabinets, qui font
leurs relances à la main. Leur problème : la relance personnalisée de qualité
prend du temps, et la tentation de copier-coller un modèle générique nuit à la
relation. L'outil leur fait gagner du temps **sans** sacrifier la
personnalisation ni la conformité.

## 3. Entrées — format prospect (YAML)

Une fiche prospect = un fichier YAML. Champs :

```yaml
nom: Jean-Marc Dubois
situation: A cédé son entreprise pour 2,3 M€, cherche à diversifier
dernier_contact: 2026-03-15        # date ISO (AAAA-MM-JJ)
objection: Préfère attendre les élections avant d'investir
```

- `nom` — identité du prospect (chaîne).
- `situation` — contexte patrimonial et moment de vie (chaîne libre).
- `dernier_contact` — date du dernier échange, au format ISO `AAAA-MM-JJ`.
- `objection` — le frein exprimé par le prospect lors du dernier contact.

Tous les champs sont obligatoires en v0. Validation au chargement (champ
manquant ou date mal formée → erreur explicite).

## 4. Paramètres de génération

Réglés par l'utilisateur, appliqués à la génération :

| Paramètre   | Valeurs                          | Défaut          | Portée                          |
|-------------|----------------------------------|-----------------|---------------------------------|
| `ton`       | `direct`, `professionnel`, `chaleureux` | `professionnel` | Variantes A et B (C force l'empathie) |
| `longueur`  | `court`, `moyen`, `long`         | `moyen`         | Les 3 variantes                 |
| `objection` | texte libre (override)           | celle du prospect | Variante A                    |
| `signature` | texte libre (nom du conseiller)  | `[Votre nom]`   | Les 3 variantes                 |

## 5. Sortie — les 3 variantes

L'outil produit **3 variantes**, chacune avec un **objet** et un **corps** :

- **Variante A — Accroche par l'objection.** Reformule l'objection du prospect
  et y répond de front, sans la contourner. Ton = paramètre `ton`.
- **Variante B — Accroche par la situation / l'événement de vie.** Accroche sur
  le contexte patrimonial du prospect (cession, héritage, retraite…) pour
  montrer une compréhension du moment de vie. Ton = paramètre `ton`.
- **Variante C — Variante empathique.** S'appuie sur l'accroche situationnelle
  (comme B), mais dans un registre **nettement plus chaleureux et empathique**
  que A et B. C'est la variante au plus fort contraste émotionnel du lot.

Chaque variante générée passe le filtre de conformité AMF (section 7) ; un
terme déconseillé détecté est signalé à l'utilisateur.

Format de sortie v0 : affichage structuré sur la sortie standard (un bloc par
variante : titre, objet, corps).

## 6. Prompt système & règles métier

Le prompt système encadre **toutes** les générations. Règles :

1. **Personnalisation obligatoire** à partir des champs de la fiche (nom,
   situation, objection) — jamais d'email générique.
2. **Traitement de l'objection (variante A)** — reformuler puis répondre
   spécifiquement à l'objection. Interdiction de l'éviter ou de la minimiser.
3. **Injection de la date courante** — la date du jour est fournie au modèle
   pour calculer le temps écoulé depuis `dernier_contact` et éviter toute
   hallucination temporelle (pas de date inventée).
4. **Respect du ton et de la longueur** demandés ; pour la variante C, l'empathie
   prime sur le paramètre `ton`.
5. **Conformité AMF** (section 7) — aucune promesse de rendement, aucun langage
   trompeur.
6. **Forme** — vouvoiement, objet d'email explicite, signature reprenant le
   paramètre `signature`, appel à l'action mesuré (proposer un échange, jamais
   forcer).

## 7. Conformité AMF

**Principe.** Une communication financière ne doit pas promettre de résultat ni
employer un langage trompeur. Le **contrôle principal est le prompt système**
(règle 5 ci-dessus) qui interdit ces formulations à la source. Le filtre en
sortie (`compliance.py`) n'est qu'un **filet de sécurité** qui rattrape ce qui
passe entre les mailles.

**Termes déconseillés (v0).** `garantir`, `garanti`, `sécuriser`, `optimiser le
rendement`, et formulations équivalentes promettant un résultat.

**Limite connue.** Une liste noire de mots est incomplète par nature (« garantir »
mais pas « garantie »). Évolution prévue : passage en *stem matching*
(`garanti\w*`) plutôt qu'énumération de variantes.

## 8. Architecture technique

Flux de données :

```
cli.py  →  config.py   (charge .env, modèle, signature)
        →  charge la fiche prospect YAML  →  models.Prospect
        →  models.ParamsGeneration  (depuis les arguments CLI)
        →  prompts.py   (construit le prompt système + le prompt de chaque variante)
        →  generator.py (appelle le SDK Anthropic → 1 génération par variante)
        →  compliance.py (vérifie chaque variante)
        →  affichage structuré (stdout)
```

**Décision v0 : une génération API par variante** (3 appels), chacune avec son
prompt d'angle dédié. Plus clair à déboguer et plus contrôlable qu'un seul appel
produisant les 3 ; le surcoût est négligeable en itérant avec Haiku.

Modèle configurable via `ANTHROPIC_MODEL` (Haiku pour itérer, Sonnet pour la
qualité finale).

## 9. Roadmap

1. **v0 — CLI** : génération des 3 variantes depuis un fichier YAML (présent jalon).
2. **Itération qualité** : test sur les 5 cas CGP de référence, ajustement des
   prompts jusqu'à des emails satisfaisants et conformes.
3. **v1 — Streamlit** : interface web réutilisant `generator`, `models`,
   `prompts`, `compliance` sans toucher au CLI.
4. **Déploiement** : Streamlit Cloud, démo publique liée au portfolio.
5. **Futur** : import de plusieurs prospects, connexion CRM / envoi.

## 10. Limites connues & hors-périmètre

- Pas d'envoi d'email ni d'intégration CRM en v0.
- Un seul prospect à la fois (pas de traitement par lots).
- Le filtre AMF n'est pas exhaustif (cf. section 7).
- La qualité finale dépend du modèle et de la qualité de la fiche prospect.
- Contenu en français uniquement.

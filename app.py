"""Interface Streamlit V1 du PATRIMO Email Booster.

Formulaire de saisie d'un prospect + paramètres de génération, puis affichage
des 3 variantes d'email produites par le moteur (`generer_variantes`) sous
forme d'onglets, avec indicateur de conformité AMF par variante.

Lancement : `streamlit run app.py` depuis la racine du projet.
"""

import html
from datetime import date

import streamlit as st

from patrimo_email_booster.config import get_api_key
from patrimo_email_booster.generator import (
    ErreurGeneration,
    FormatReponseError,
    generer_variantes,
)
from patrimo_email_booster.models import ParamsGeneration, Prospect
from patrimo_email_booster.prompts import LONGUEURS, TONS


st.set_page_config(page_title="Patrimo Email Booster", layout="centered")


def rendu_corps_email(corps: str) -> None:
    """Affiche le corps d'un email dans une carte stylée PATRIMO + bouton Copier.

    Le corps n'est injecté qu'à un seul endroit (le <pre>, échappé via
    html.escape). Le bouton lit le texte depuis le DOM (innerText) plutôt
    que de le ré-injecter dans un littéral JS, ce qui éviterait toute
    erreur sur guillemet/apostrophe/backtick et tout second point d'injection.
    Chaque appel st.iframe crée sa propre iframe : l'id fixe ne collisionne
    pas entre variantes.
    """
    corps_echappe = html.escape(corps)
    st.iframe(
        f"""
        <style>
          .patrimo-card {{
            background: #E7ECF2;
            color: #001233;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-size: 15px;
            line-height: 1.5;
            padding: 16px 20px;
            border-radius: 8px;
            max-height: 300px;
            overflow-y: auto;
            margin: 0 0 12px 0;
            white-space: pre-wrap;
            word-wrap: break-word;
          }}
          .patrimo-btn {{
            background: #023E7D;
            color: #ffffff;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            cursor: pointer;
          }}
          .patrimo-btn:hover {{ background: #002855; }}
          .patrimo-feedback {{
            margin-left: 12px;
            color: #023E7D;
            font-size: 14px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          }}
        </style>
        <pre id="corps-email" class="patrimo-card">{corps_echappe}</pre>
        <button class="patrimo-btn" onclick="copierCorpsEmail()">Copier</button>
        <span id="feedback-copie" class="patrimo-feedback"></span>
        <script>
          function copierCorpsEmail() {{
            const texte = document.getElementById('corps-email').innerText;
            navigator.clipboard.writeText(texte).then(() => {{
              const fb = document.getElementById('feedback-copie');
              fb.textContent = 'Copié ✓';
              setTimeout(() => {{ fb.textContent = ''; }}, 1500);
            }});
          }}
        </script>
        """,
        height=400,
    )

st.title("Patrimo Email Booster")
st.caption(
    "Génère 3 variantes d'email de relance personnalisé pour un prospect CGP."
)

# Fail-fast si la clé API est absente : on n'affiche pas le formulaire dans ce cas.
try:
    get_api_key()
except RuntimeError as e:
    st.error(str(e))
    st.stop()

with st.form("formulaire_prospect"):
    st.subheader("Fiche prospect")
    nom = st.text_input("Nom du prospect")
    situation = st.text_area(
        "Situation patrimoniale",
        placeholder="Ex. : Entrepreneur tech, 38 ans, exit récent, 1,8 M€ de liquidités",
        height=100,
    )
    dernier_contact = st.date_input(
        "Date du dernier contact",
        value=date.today(),
    )
    objection = st.text_area(
        "Objection exprimée",
        placeholder="Ex. : Vos frais sont trop élevés, je gère seul via une banque en ligne.",
        height=80,
    )

    st.subheader("Paramètres de génération")
    ton = st.selectbox("Ton", TONS, index=TONS.index("professionnel"))
    longueur = st.selectbox(
        "Longueur",
        list(LONGUEURS.keys()),
        index=list(LONGUEURS).index("moyen"),
    )
    signature = st.text_input("Signature", value="[Votre nom]")

    submitted = st.form_submit_button("Générer les 3 variantes")

if submitted:
    if not nom.strip() or not situation.strip() or not objection.strip():
        st.warning("Veuillez remplir tous les champs obligatoires (nom, situation, objection).")
        st.stop()

    prospect = Prospect(
        nom=nom.strip(),
        situation=situation.strip(),
        dernier_contact=dernier_contact.isoformat(),
        objection=objection.strip(),
    )
    params = ParamsGeneration(
        ton=ton,
        longueur=longueur,
        objection=None,
        signature=signature.strip() or "[Votre nom]",
    )

    with st.spinner("Génération des 3 variantes en cours…"):
        try:
            variantes = generer_variantes(prospect, params)
        except (ErreurGeneration, FormatReponseError, RuntimeError) as e:
            st.error(f"Erreur lors de la génération : {e}")
            st.stop()

    onglets = st.tabs([v.titre for v in variantes])
    for onglet, variante in zip(onglets, variantes):
        with onglet:
            st.markdown(f"**Objet** : {variante.objet}")
            if variante.est_conforme:
                st.success("Conforme AMF")
            else:
                st.warning(
                    "Termes problématiques : "
                    + ", ".join(variante.termes_non_conformes)
                )
            rendu_corps_email(variante.corps)

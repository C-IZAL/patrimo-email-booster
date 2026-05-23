"""Interface Streamlit V1 du PATRIMO Email Booster.

Formulaire de saisie d'un prospect + paramètres de génération, puis affichage
des 3 variantes d'email produites par le moteur (`generer_variantes`) sous
forme d'onglets, avec indicateur de conformité AMF par variante.

Lancement : `streamlit run app.py` depuis la racine du projet.
"""

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
            st.text_area(
                "Corps de l'email",
                value=variante.corps,
                height=320,
                disabled=True,
                label_visibility="collapsed",
                key=f"corps_{variante.variante.name}",
            )

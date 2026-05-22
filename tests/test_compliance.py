from patrimo_email_booster.compliance import detecter_termes, est_conforme


def test_detecte_termes_deconseilles():
    texte = "Nous pouvons garantir et sécuriser votre capital."
    trouves = detecter_termes(texte)
    assert "garantir" in trouves
    assert "sécuriser" in trouves


def test_detecte_optimiser_le_rendement():
    assert "optimiser le rendement" in detecter_termes(
        "Notre stratégie vise à optimiser le rendement de votre épargne."
    )


def test_insensible_a_la_casse():
    assert detecter_termes("GARANTIR un résultat") == ["garantir"]


def test_texte_conforme():
    texte = "Je reste disponible pour faire un point sur votre situation."
    assert est_conforme(texte)
    assert detecter_termes(texte) == []

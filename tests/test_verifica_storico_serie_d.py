from tools.verifica_storico_serie_d import reconcile


def row(home="A", hg="2", ag="1"):
    return {"LeagueId": "Italy_SerieD_GironeA", "MatchDate": "2026-09-06",
            "Home": home, "Away": "B", "HG": hg, "AG": ag}


def test_reconcile_new_existing_conflict_and_unscored():
    proposal = [row(), row("C"), row("D"), row("E")]
    existing = [row("C"), row("D", "1", "1"), row("E", "", "")]
    report, missing = reconcile(proposal, existing)
    assert [r["Esito"] for r in report] == [
        "NUOVA", "GIA_PRESENTE", "CONFLITTO_RISULTATO",
        "ESISTENTE_SENZA_RISULTATO"]
    assert missing == [proposal[0]]


def test_duplicate_proposal_not_added_twice():
    report, missing = reconcile([row(), row()], [])
    assert [r["Esito"] for r in report] == ["NUOVA", "PROPOSTA_DUPLICATA"]
    assert len(missing) == 1


def test_existing_duplicate_reported():
    report, missing = reconcile([row()], [row(), row()])
    assert [r["Esito"] for r in report] == ["GIA_PRESENTE", "ESISTENTE_DUPLICATO"]
    assert not missing

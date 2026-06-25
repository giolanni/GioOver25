from gioover25.aliases import get_league_id


def test_obos():
    league = get_league_id(
        "Diretta",
        "Norvegia",
        "OBOS-ligaen"
    )

    assert league == "Norway_OBOSLigaen_2026"


def test_division3():
    league = get_league_id(
        "Diretta",
        "Norvegia",
        "Division 3 - Group 1"
    )

    assert league == "Norway_Division3_Group1_2026"


def test_print():
    print(
        get_league_id(
            "Diretta",
            "Norvegia",
            "Division 3 - Group 1"
        )
    )
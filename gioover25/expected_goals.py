"""Stima descrittiva dei gol totali, indipendente dagli engine di ranking."""


def estimate_expected_goals(*, histories, home, away, home_source, away_source,
                            match_date, include_all_histories, normalize_team,
                            match_date_of, match_goals):
    """Usa soltanto risultati precedenti a MatchDate; None se campione insufficiente."""
    if match_date is None:
        return None

    def observations(team, source):
        matches = (match for games in histories.values() for match in games) if include_all_histories else iter(histories.get(source, []))
        key = normalize_team(source, team)
        rows = []
        seen = set()
        for match in matches:
            day = match_date_of(match)
            goals = match_goals(match)
            if day is None or day >= match_date or goals is None:
                continue
            h = normalize_team(source, getattr(match, "home", ""))
            a = normalize_team(source, getattr(match, "away", ""))
            if key not in (h, a):
                continue
            identity = (day, h, a, goals)
            if identity in seen:
                continue
            seen.add(identity)
            is_home = key == h
            gf, ga = goals if is_home else goals[::-1]
            rows.append((day, gf, ga, is_home))
        return sorted(rows, key=lambda item: item[0])

    home_rows = observations(home, home_source)
    away_rows = observations(away, away_source)
    if len(home_rows) < 3 or len(away_rows) < 3:
        return None

    def rates(rows, venue):
        recent = rows[-5:]
        venue_rows = [r for r in rows if r[3] == venue][-5:]
        def mean(items, index):
            return sum(r[index] for r in items) / len(items)
        gf, ga = mean(recent, 1), mean(recent, 2)
        if len(venue_rows) >= 3:
            gf = 0.7 * gf + 0.3 * mean(venue_rows, 1)
            ga = 0.7 * ga + 0.3 * mean(venue_rows, 2)
        return gf, ga

    hgf, hga = rates(home_rows, True)
    agf, aga = rates(away_rows, False)
    return round((hgf + aga) / 2 + (agf + hga) / 2, 2)

from pathlib import Path
import csv


ROOT = Path(__file__).resolve().parents[1]

CLASSIFICHE_DIR = ROOT / "data" / "storico" / "classifiche_calcolate"
REGISTRY_FILE = ROOT / "data" / "league_registry.csv"
LOG_FILE = ROOT / "data" / "check_classifiche.log"
EXCEPTIONS_FILE = ROOT / "data" / "check_classifiche_exceptions.csv"
RESET_LOG_FILE = ROOT / "data" / "storico" / "aggregati_reset" / "reset_log.csv"


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def load_registry():
    rows = read_csv(REGISTRY_FILE)

    registry = {}

    for row in rows:
        league_id = row["LeagueId"].strip()

        if not league_id:
            continue

        try:
            teams = int(row["Teams"].strip())
        except (ValueError, TypeError):
            print(
                f"⚠ Registry: numero squadre non valido "
                f"per {league_id}: {row['Teams']!r}"
            )
            continue

        registry[league_id] = teams

    return registry


def load_reset_leagues():
    """Restituisce i LeagueId presenti nello storico dei reset."""
    if not RESET_LOG_FILE.exists():
        return set()

    return {
        row.get("LeagueId", "").strip()
        for row in read_csv(RESET_LOG_FILE)
        if row.get("LeagueId", "").strip()
    }


def load_exceptions():
    if not EXCEPTIONS_FILE.exists():
        return []
    return read_csv(EXCEPTIONS_FILE)


def is_league_played_exception(exceptions, league_id):
    return any(
        item.get("LeagueID", "").strip() == league_id
        and item.get("Check", "").strip().upper() == "LEAGUE_PLAYED"
        for item in exceptions
    )


def is_played_exception(exceptions, league_id, row, played):
    team = str(row.get("Team", "")).strip()
    for item in exceptions:
        if item.get("LeagueID", "").strip() != league_id:
            continue
        if item.get("Check", "").strip().upper() != "TEAM_PLAYED":
            continue
        if item.get("Team", "").strip() != team:
            continue
        expected = item.get("ExpectedValue", "").strip()
        if not expected:
            return True
        try:
            return played == int(float(expected))
        except ValueError:
            return False
    return False


def get_played(row):
    """
    Cerca la colonna delle partite giocate.
    Le classifiche GioOver normalmente usano Played.
    """
    for column in ("Played", "played", "PG", "Partite"):
        if column in row:
            value = str(row[column]).strip()

            if not value:
                return None

            try:
                return int(float(value))
            except ValueError:
                return None

    return None


def main():
    registry = load_registry()
    exceptions = load_exceptions()
    reset_leagues = load_reset_leagues()

    print(f"Leghe caricate dal registry: {len(registry)}")
    print(f"Leghe presenti nello storico reset: {len(reset_leagues)}")

    files = sorted(CLASSIFICHE_DIR.glob("*.csv"))

    print(f"Classifiche trovate: {len(files)}")
    print()

    log_lines = []
    alert_count = 0

    for path in files:
        league_id = path.stem

        # ---------------------------------------------------------
        # Verifica presenza nel registry
        # ---------------------------------------------------------

        if league_id not in registry:
            message = (
                f"{league_id}: "
                f"⚠ NON TROVATA NEL LEAGUE REGISTRY"
            )

            print(message)
            log_lines.append(message)
            alert_count += 1
            continue

        rows = read_csv(path)

        if not rows:
            message = f"{league_id}: 🚨 CLASSIFICA VUOTA"

            print(message)
            log_lines.append(message)
            alert_count += 1
            continue

        expected_teams = registry[league_id]
        actual_teams = len(rows)

        alerts = []

        # ---------------------------------------------------------
        # 1. Numero squadre
        # ---------------------------------------------------------

        # Teams=0 nel registry significa che il numero di squadre non è
        # configurato: in quel caso il controllo non deve generare alert.
        if expected_teams > 0 and actual_teams != expected_teams:
            alerts.append(
                f"🚨 ALERT SQUADRE: "
                f"attese={expected_teams} trovate={actual_teams}"
            )

        # ---------------------------------------------------------
        # 2. Disparità partite giocate
        # ---------------------------------------------------------

        played_values = []
        if (
            league_id not in reset_leagues
            and not is_league_played_exception(exceptions, league_id)
        ):
            for row in rows:
                played = get_played(row)
                if played is None:
                    continue
                if is_played_exception(exceptions, league_id, row, played):
                    continue
                played_values.append(played)

        if played_values:
            min_played = min(played_values)
            max_played = max(played_values)
            diff = max_played - min_played

            if diff > 3:
                alerts.append(
                    f"🚨🚨 ALERT FORTE PARTITE: "
                    f"min={min_played} "
                    f"max={max_played} "
                    f"diff={diff}"
                )

            elif diff > 2:
                alerts.append(
                    f"⚠ ALERT PARTITE: "
                    f"min={min_played} "
                    f"max={max_played} "
                    f"diff={diff}"
                )

        # ---------------------------------------------------------
        # Output solo anomalie
        # ---------------------------------------------------------

        if alerts:
            alert_count += 1

            print(league_id)
            log_lines.append(league_id)

            for alert in alerts:
                print(f"  {alert}")
                log_lines.append(f"  {alert}")

            print()
            log_lines.append("")

    # -------------------------------------------------------------
    # Log
    # -------------------------------------------------------------

    LOG_FILE.write_text(
        "\n".join(log_lines),
        encoding="utf-8",
    )

    print("----------------------------------------")
    print(f"Leghe nel registry       : {len(registry)}")
    print(f"Classifiche controllate  : {len(files)}")
    print(f"Classifiche con alert    : {alert_count}")
    print(f"Log                      : {LOG_FILE}")
    print("----------------------------------------")


if __name__ == "__main__":
    main()

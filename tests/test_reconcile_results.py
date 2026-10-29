import csv
from datetime import date
from pathlib import Path

from gioover25 import ranking_history as rh
from gioover25.reconcile_results import reconcile_unresolved_matches


def write(path, rows, fields=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]), delimiter=';')
        w.writeheader()
        w.writerows(rows)


def row(home, day='2026-10-24', **extra):
    return dict(LeagueId='Test', Round='1', MatchDate=day, PredictionDate=day,
                Home=home, Away='Away', MatchStatus='SCHEDULED', Score='78', Band='ALTA', **extra)


def test_reconcile_and_repeat(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rows = [row('Missing'), row('Known'), row('OtherEngine'), row('Older', '2026-10-23'),
            row('Today', '2026-10-29'), row('Future', '2026-10-30')]
    rh._write_history('v26', rows)
    other = row('OtherEngine', HG='1', AG='1')
    other['MatchStatus'] = 'FINAL'
    rh._write_history('retired', [other])
    write('data/output_ranking/v26/old_ranking/ranking_test.csv', rows)
    known = row('Known', HG='2', AG='1')
    write('data/storico/risultati/Test.csv', [known])
    # A different returned event establishes the date being imported.
    write('input.csv', [row('Provider', HG='3', AG='0')])
    result = reconcile_unresolved_matches(['v26', 'retired'], 'input.csv', date(2026,10,29))
    assert result == dict(repaired=2, not_found=1, unresolved=1)
    actual = {r['Home']:r for r in rh._read_history('v26')}
    assert actual['Missing']['MatchStatus'] == 'POSTPONED'
    assert actual['Known']['BTTS'] == 'OK'
    assert actual['OtherEngine']['BTTS'] == 'OK'
    for name in ['Older', 'Today', 'Future']:
        assert actual[name]['MatchStatus'] == 'SCHEDULED'
    assert all(r['Score']=='78' and r['Band']=='ALTA' for r in actual.values())
    again = reconcile_unresolved_matches(['v26', 'retired'], 'input.csv', date(2026,10,29))
    assert again == dict(repaired=0, not_found=0, unresolved=1)
    assert len(list(csv.DictReader(Path('data/storico/partite_posticipate.csv').open(encoding='utf-8-sig'), delimiter=';'))) == 1


def test_empty_input_and_conflicting_finals(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rh._write_history('v26', [row('Missing'), row('Conflict')])
    a, b = row('Conflict', HG='1', AG='1'), row('Conflict', HG='0', AG='0')
    a['MatchStatus'] = b['MatchStatus'] = 'FINAL'
    rh._write_history('old', [a, b])
    write('input.csv', [], ['LeagueId','MatchDate','Home','Away'])
    result = reconcile_unresolved_matches(['v26','old'], 'input.csv', date(2026,10,29))
    assert result == dict(repaired=0, not_found=0, unresolved=2)
    assert 'CONFLICTING_RESULTS' in Path('data/debug/risultati_non_riconciliati.csv').read_text(encoding='utf-8-sig')
    assert not Path('data/storico/partite_posticipate.csv').exists()


def test_not_found_recovery_and_future_fixture(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from gioover25 import append_results as ar
    assert 'NOT_FOUND' in ar.POSTPONED_STATUSES
    rh._write_history('v26', [row('Same'), row('Same', '2026-11-01')])
    ar._write_postponed([{**row('Same'), 'Status':'NOT_FOUND', 'Notes':'presunto'}])
    rh.sync_postponed_statuses('v26')
    rows = rh._read_history('v26')
    assert rows[0]['MatchStatus'] == 'POSTPONED'
    assert rows[1]['MatchStatus'] == 'SCHEDULED'
    from gioover25.history import MatchResult
    rh.update_finished_matches('v26', [('Test', MatchResult('', '', 1, '2026-10-28', 'Same', 'Away', 2, 1))])
    rows = rh._read_history('v26')
    assert rows[0]['MatchStatus'] == 'FINAL'
    assert rows[0]['BTTS'] == 'OK'
    assert rows[1]['MatchStatus'] == 'SCHEDULED'

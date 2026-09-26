import copy
import json
from pathlib import Path
import pandas as pd
import pytest
from sports_dependency_engine.io import CachedClient
from sports_dependency_engine.sports.mlb.ingestion import schedule
from sports_dependency_engine.sports.mlb.player_games import player_rows, STAT_FIELDS
from sports_dependency_engine.reports.diagnostics import validate


def fixture():
    stats = {key:0 for key in STAT_FIELDS.values()}
    stats.update(plateAppearances=1, atBats=1, hits=1, homeRuns=1, runs=1, rbi=1)
    teams = {}
    for side,pid in [('home',1),('away',2)]:
        teams[side] = {'team':{'name':side},'batters':[pid], 'players':{f'ID{pid}':{'person':{'fullName':side},'stats':{'batting':dict(stats)}}},'teamStats':{'batting':dict(stats)}}
    return {'gamePk':1,'officialDate':'2015-04-05','season':'2015'}, {'teams':teams}


def test_normalization_and_reconciliation():
    game, box = fixture()
    rows, exclusions = player_rows(game,box)
    assert not exclusions
    assert rows[0]['total_bases'] == 4
    assert rows[0]['hits_plus_runs_plus_RBI'] == 3
    assert validate(pd.DataFrame(rows))['games'] == 1
    box['teams']['home']['teamStats']['batting']['hits'] = 2
    with pytest.raises(ValueError,match='player sum'):
        player_rows(game,box)


def test_missing_not_imputed_and_duplicates_rejected():
    game, box = fixture()
    del box['teams']['home']['players']['ID1']['stats']['batting']['rbi']
    with pytest.raises(ValueError,match='missing'):
        player_rows(game,box)
    game, box = fixture()
    rows,_ = player_rows(game,box)
    with pytest.raises(ValueError,match='Duplicate'):
        validate(pd.DataFrame(rows+rows))


def test_schedule_exclusions_and_doubleheaders():
    class FakeClient:
        def get(self,*args):
            base = {'officialDate':'2015-04-05','gameType':'R','status':{'abstractGameState':'Final','codedGameState':'F'}}
            return {'dates':[{'date':'2015-04-05','games':[
                {**base,'gamePk':1}, {**base,'gamePk':2},
                {**base,'gamePk':3,'status':{'abstractGameState':'Preview','detailedState':'Postponed'}},
                {**base,'gamePk':1}]}]}
    games, excluded = schedule(FakeClient(),'2015-04-05','2015-04-05')
    assert [g['gamePk'] for g in games] == [1,2]
    assert len(excluded) == 2


def test_offline_cache_miss(tmp_path):
    with pytest.raises(FileNotFoundError):
        CachedClient(tmp_path,offline=True).get('https://example.com/data')


def test_real_mlb_fixture():
    payload = json.loads((Path(__file__).parent/'fixtures/mlb_game.json').read_text())
    rows, exclusions = player_rows(payload['game'],payload['boxscore'])
    info = validate(pd.DataFrame(rows))
    assert info['games'] == 1
    assert info['rows'] > 18
    assert not any(info['identity_violations'].values())


def test_end_to_end_offline_replay(tmp_path, monkeypatch):
    import sports_dependency_engine.cli as cli
    payload = json.loads((Path(__file__).parent/'fixtures/mlb_game.json').read_text())
    game, box = payload['game'], payload['boxscore']
    monkeypatch.setattr(cli,'schedule',lambda *_: ([game], []))
    monkeypatch.setattr(cli,'boxscore',lambda *_: box)
    output = cli.run('2015-04-05','2015-04-05',tmp_path,offline=True)
    first = (output/'all_pairs.csv').read_bytes()
    cli.run('2015-04-05','2015-04-05',tmp_path,offline=True)
    assert first == (output/'all_pairs.csv').read_bytes()
    manifest = json.loads((output/'manifest.json').read_text())
    assert manifest['analysis_rows'] > 0
    assert manifest['source_sha256']
    assert (output/'research_report.md').exists()

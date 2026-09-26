import json
import numpy as np
import pandas as pd
import pytest
from sports_dependency_engine.backtest.historical import freeze_candidates, evaluate_holdout, read_frozen
from sports_dependency_engine.backtest.uncertainty import clustered_intervals
from sports_dependency_engine.dependency.combo_search import Combo, ComboConfig
from sports_dependency_engine.sports.mlb.props import Prop


def make_frame(start: str, first_game: int, failures: bool = False) -> pd.DataFrame:
    rows = []
    for g, date in enumerate(pd.date_range(start,periods=5)):
        for player in range(10):
            hits = int(player % 2 == 0)
            runs = 0 if failures else hits
            rows.append(dict(game_id=first_game+g, date=date.strftime('%Y-%m-%d'), player_id=player,
                             player_name=f'Player {player}', team='A', opponent='B', season=2015,
                             plate_appearances=4, at_bats=4, hits=hits, singles=hits, doubles=0,
                             triples=0, home_runs=0, total_bases=hits, runs=runs, RBI=0,
                             hits_plus_runs_plus_RBI=hits+runs, walks=0, strikeouts=0, stolen_bases=0))
    return pd.DataFrame(rows)


def freeze_example(tmp_path):
    train = tmp_path/'train.parquet'
    make_frame('2015-04-01',1).to_parquet(train,index=False)
    props = [Prop('hits',1),Prop('runs',1),Prop('total_bases',1)]
    return freeze_candidates(train,tmp_path/'frozen',ComboConfig(min_anchor=2,min_guard=2,min_conditional_lower=0),props)


def test_frozen_selection_survives_holdout_failures_and_zero_anchors(tmp_path):
    frozen = freeze_example(tmp_path)
    original = frozen.read_bytes()
    test = tmp_path/'test.parquet'
    make_frame('2015-05-01',101,True).to_parquet(test,index=False)
    output = evaluate_holdout(frozen,test,tmp_path/'results',replicates=100)
    results = pd.read_csv(output/'holdout_combos.csv')
    payload, candidates, _ = read_frozen(frozen)
    assert list(results.candidate_id) == [c.candidate_id for c in candidates]
    assert frozen.read_bytes() == original
    assert results.test_n_anchor.eq(0).any()
    assert results.test_n_violations.gt(0).any()
    assert results.test_P_guard_given_anchor.isna().any()
    assert len(results) == len(payload['train_statistics'])
    assert not results.loc[results.type.eq('EMPIRICAL_CANDIDATE'),'test_screen_pass'].any()
    replay = evaluate_holdout(frozen,test,tmp_path/'replay',replicates=100)
    assert (output/'holdout_combos.csv').read_bytes() == (replay/'holdout_combos.csv').read_bytes()
    with pytest.raises(FileExistsError):
        evaluate_holdout(frozen,test,output,replicates=100)


def test_overlap_and_checksum_fail_closed(tmp_path):
    frozen = freeze_example(tmp_path)
    path = tmp_path/'test.parquet'
    make_frame('2015-04-05',100).to_parquet(path,index=False)
    with pytest.raises(ValueError,match='strictly later'):
        evaluate_holdout(frozen,path,tmp_path/'out')
    make_frame('2015-05-01',1).to_parquet(path,index=False)
    with pytest.raises(ValueError,match='overlap'):
        evaluate_holdout(frozen,path,tmp_path/'out')
    bundle = json.loads(frozen.read_text())
    bundle['payload']['train_end'] = '2015-03-01'
    frozen.write_text(json.dumps(bundle))
    with pytest.raises(ValueError,match='checksum'):
        read_frozen(frozen)


def test_rule_semantics_drift_rejected(tmp_path,monkeypatch):
    import sports_dependency_engine.backtest.historical as historical
    frozen = freeze_example(tmp_path)
    hashes = historical.source_hashes()
    hashes['sports/mlb/rules.py'] = 'changed'
    monkeypatch.setattr(historical,'source_hashes',lambda:hashes)
    with pytest.raises(ValueError,match='semantics changed'):
        read_frozen(frozen)


def test_bootstrap_reproducibility_and_degenerate_perfection():
    frame = make_frame('2015-04-01',1)
    combo = Combo(Prop('hits',1),(Prop('runs',1),))
    a = clustered_intervals(frame,[combo],'game_id',replicates=100)
    b = clustered_intervals(frame,[combo],'game_id',replicates=100)
    pd.testing.assert_frame_equal(a,b)
    assert a.iloc[0].game_id_conditional_low == 1
    assert a.iloc[0].game_id_leakage_high == 0
    # Entire anchor-free player samples are reported, rather than coerced to zero.
    frame['hits'] = 0
    frame['runs'] = 0
    zero = clustered_intervals(frame,[combo],'player_id',replicates=100).iloc[0]
    assert zero.player_id_bootstrap_valid == 0
    assert np.isnan(zero.player_id_conditional_low)
    with pytest.raises(ValueError,match='two clusters'):
        clustered_intervals(frame.loc[frame.game_id.eq(1)],[combo],'game_id',replicates=100)


def test_no_candidates_is_valid_output(tmp_path):
    train, test = tmp_path/'train.parquet', tmp_path/'test.parquet'
    make_frame('2015-04-01',1).to_parquet(train,index=False)
    make_frame('2015-05-01',101).to_parquet(test,index=False)
    frozen = freeze_candidates(train,tmp_path/'frozen',ComboConfig(min_anchor=1000))
    output = evaluate_holdout(frozen,test,tmp_path/'result',replicates=100)
    assert pd.read_csv(output/'holdout_combos.csv').empty
    assert 'No candidates' in (output/'research_report.md').read_text()

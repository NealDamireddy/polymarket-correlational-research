import math
import pandas as pd
import pytest
from sports_dependency_engine.config import ResearchConfig
from sports_dependency_engine.dependency.metrics import pair_metrics, wilson
from sports_dependency_engine.dependency.pair_search import search_pairs
from sports_dependency_engine.reports.rankings import rank_pairs
from sports_dependency_engine.sports.mlb.props import Prop


def test_known_contingency_table():
    m = pair_metrics(100,40,50,30)
    assert m['P_anchor'] == .4
    assert m['P_guard'] == .5
    assert m['joint_prob'] == .3
    assert m['P_guard_given_anchor'] == .75
    assert m['P_anchor_given_guard'] == .6
    assert m['dependency_ratio'] == pytest.approx(1.5)
    assert m['conditional_lift'] == pytest.approx(1.5)
    assert m['P_guard_given_anchor_ci_low'] < .75 < m['P_guard_given_anchor_ci_high']


def test_wilson_and_zero_support():
    assert wilson(0,100)[0] == 0
    assert wilson(100,100)[0] == pytest.approx(.9630065)
    assert math.isnan(pair_metrics(10,0,2,0)['P_guard_given_anchor'])
    assert math.isnan(wilson(0,0)[0])
    with pytest.raises(ValueError):
        pair_metrics(100,80,80,1)


def test_empirical_perfection_never_becomes_proof():
    frame = pd.DataFrame({'hits':[1]*27+[0]*73, 'runs':[1]*27+[0]*73})
    pairs = search_pairs(frame,[Prop('hits',1),Prop('runs',1)])
    assert set(pairs.type) == {'WEAK_OR_NONE'}
    assert rank_pairs(pairs).empty
    supported = pd.DataFrame({'hits':[1]*500+[0]*500,'runs':[1]*500+[0]*500})
    pairs = search_pairs(supported,[Prop('hits',1),Prop('runs',1)])
    assert set(pairs.type) == {'EMPIRICAL_NEAR_IMPLICATION'}


def test_proof_violation_and_missing_are_fatal():
    with pytest.raises(ValueError,match='contradicts'):
        search_pairs(pd.DataFrame({'home_runs':[1],'hits':[0]}), [Prop('home_runs',1),Prop('hits',1)])
    with pytest.raises(ValueError,match='Missing'):
        search_pairs(pd.DataFrame({'home_runs':[None],'hits':[0]}), [Prop('home_runs',1),Prop('hits',1)])


def test_matrix_does_not_overflow_boolean_or_small_integer_counts():
    frame = pd.DataFrame({'hits':[1]*1000,'runs':[1]*1000})
    pairs = search_pairs(frame,[Prop('hits',1),Prop('runs',1)])
    assert pairs.n_joint.eq(1000).all()

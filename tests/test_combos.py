import numpy as np
import pandas as pd
import pytest
from sports_dependency_engine.dependency.combo_search import Combo, ComboConfig, combo_metrics, discover_combos, evaluate_combos
from sports_dependency_engine.sports.mlb.props import Prop


def test_direct_conjunction_and_leakage_not_product():
    a = np.array([True]*4+[False]*4)
    g1 = np.array([True,True,True,False]+[False]*4)
    g2 = np.array([False,True,True,True]+[False]*4)
    m = combo_metrics(a, g1 & g2)
    assert m['P_guard_given_anchor'] == .5  # NOT .75 * .75
    assert m['joint_prob'] == .25
    assert m['leakage'] == .25
    assert m['conditional_failure'] == .5
    assert m['leakage_ci_low'] < .25 < m['leakage_ci_high']


def test_exact_and_zero_support():
    combo = Combo(Prop('home_runs',1), (Prop('hits',1),Prop('total_bases',4),Prop('RBI',1)))
    data = pd.DataFrame({'home_runs':[1,0], 'hits':[1,0], 'total_bases':[4,0], 'RBI':[1,0]})
    result = evaluate_combos(data,[combo]).iloc[0]
    assert result['type'] == 'EXACT_IMPLICATION'
    assert result.leakage == 0
    assert result.P_rule_guards_given_anchor == 1
    data['home_runs'] = 0
    assert np.isnan(evaluate_combos(data,[combo]).iloc[0].P_guard_given_anchor)
    data['home_runs'] = 1
    with pytest.raises(ValueError,match='contradicts'):
        evaluate_combos(data,[combo])


def test_guard_order_does_not_change_identity():
    a, b, c = Prop('hits',1),Prop('runs',1),Prop('RBI',1)
    assert Combo(a,(b,c)).candidate_id == Combo(a,(c,b)).candidate_id
    with pytest.raises(ValueError,match='Duplicate'):
        Combo(a,(a,))
    with pytest.raises(ValueError,match='scope'):
        Combo(a,(Prop('runs',1,scope='other'),))


def test_joint_pruning_drops_pairwise_eligible_combination():
    # Both guards pass 90% individually; their conjunction only passes 80%.
    data = pd.DataFrame({'a':[1]*100,'b':[0]*10+[1]*90,'c':[1]*90+[0]*10})
    props = [Prop(x,1) for x in ['a','b','c']]
    config = ComboConfig(min_anchor=10,min_guard=10,min_conditional=.9,min_conditional_lower=0)
    candidates, _, audit = discover_combos(data,props,config)
    assert any(c.anchor.stat=='a' and len(c.guards)==1 for c in candidates)
    assert not any(c.anchor.stat=='a' and len(c.guards)==2 for c in candidates)
    assert audit['joint_screen_rejected'] > 0


def test_guard_cap_budget_support_and_determinism():
    frame = pd.DataFrame({x:[1]*200 for x in ['a','b','c','d']})
    props = [Prop(x,1) for x in frame]
    config = ComboConfig(max_candidates_per_anchor=2)
    candidates, stats, audit = discover_combos(frame,props,config)
    assert audit['evaluated'] == 12
    assert all(len(c.guards)<=2 for c in candidates)
    assert all(len(x)==1 for x in audit['capped_guards'].values())
    reversed_candidates, _, _ = discover_combos(frame,list(reversed(props)),config)
    assert [c.candidate_id for c in candidates] == [c.candidate_id for c in reversed_candidates]
    assert set(stats.type) == {'EMPIRICAL_CANDIDATE'}
    with pytest.raises(ValueError,match='budget'):
        discover_combos(frame,props,ComboConfig(max_evaluations=1))
    none, _, audit = discover_combos(frame.iloc[:5],props)
    assert not none and audit['retained']==0

@pytest.mark.parametrize('kwargs',[{'max_guards':4},{'max_guards':0},{'min_anchor':0},{'min_conditional':1.1},{'max_candidates_per_anchor':100}])
def test_invalid_config(kwargs):
    with pytest.raises(ValueError):
        ComboConfig(**kwargs)

from itertools import product
import pandas as pd
import pytest
from sports_dependency_engine.sports.mlb.props import Prop, default_props, outcomes
from sports_dependency_engine.dependency.implications import prove

@pytest.mark.parametrize('stat,threshold', [('hits',1), ('total_bases',4), ('runs',1), ('RBI',1), ('hits_plus_runs_plus_RBI',3)])
def test_home_run_implications(stat, threshold):
    assert prove(Prop('home_runs',1), Prop(stat,threshold)).proven

@pytest.mark.parametrize('stat', ['hits','total_bases','hits_plus_runs_plus_RBI','runs','RBI','home_runs'])
def test_threshold_monotonicity(stat):
    assert prove(Prop(stat,4), Prop(stat,2)).proven
    assert not prove(Prop(stat,2), Prop(stat,4)).proven


def test_scope_and_nonimplications():
    assert not prove(Prop('home_runs',1), Prop('hits',1,scope='first_five_innings')).proven
    assert not prove(Prop('home_runs',1), Prop('hits',1,sport='nba')).proven
    assert not prove(Prop('total_bases',4), Prop('home_runs',1)).proven
    assert not prove(Prop('hits',1), Prop('runs',1)).proven
    assert prove(Prop('hits',2), Prop('total_bases',2)).proven
    assert prove(Prop('home_runs',2), Prop('hits_plus_runs_plus_RBI',6)).proven


def test_all_proofs_on_independent_feasible_scoring_states():
    # Independent enumeration covers singles through HR and additional runs/RBI.
    rows = []
    for s,d,t,h,r,b in product(range(3), repeat=6):
        rows.append(dict(home_runs=h, hits=s+d+t+h, total_bases=s+2*d+3*t+4*h,
                         runs=h+r, RBI=h+b, hits_plus_runs_plus_RBI=s+d+t+3*h+r+b))
    props = default_props()
    events = outcomes(pd.DataFrame(rows), props)
    for a,b in product(props, repeat=2):
        if prove(a,b).proven:
            assert not (events[a.label] & ~events[b.label]).any(), (a,b)

@pytest.mark.parametrize('threshold', [0,-1,1.5,True])
def test_invalid_threshold(threshold):
    with pytest.raises(ValueError):
        Prop('hits',threshold)

@pytest.mark.parametrize('tb,hits', [(1,1),(4,1),(5,2),(6,2),(8,2),(9,3)])
def test_total_bases_implies_minimum_hits(tb,hits):
    assert prove(Prop('total_bases',tb),Prop('hits',hits)).proven
    assert not prove(Prop('total_bases',tb),Prop('hits',hits+1)).proven

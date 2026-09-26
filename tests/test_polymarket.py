import pytest
from sports_dependency_engine.polymarket.parser import normalize_outcomes

def test_outcome_mapping_by_label_and_reject_misalignment():
    result = normalize_outcomes({'outcomes':'["No","Yes"]','clobTokenIds':['n','y'],'outcomePrices':'["0.6","0.4"]'})
    assert result[1]['token_id'] == 'y'
    with pytest.raises(ValueError):
        normalize_outcomes({'outcomes':['Yes'],'clobTokenIds':[],'outcomePrices':[.5]})

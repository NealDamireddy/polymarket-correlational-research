"""Only supported pairs enter the primary ranking; all pairs remain available."""
import pandas as pd

def rank_pairs(pairs: pd.DataFrame) -> pd.DataFrame:
    priority = {"EXACT_IMPLICATION": 0, "EMPIRICAL_NEAR_IMPLICATION": 1,
                "STRONG_DEPENDENCE": 2, "WEAK_OR_NONE": 3}
    return (pairs.loc[pairs.eligible].assign(_priority=lambda x: x["type"].map(priority))
            .sort_values(["_priority", "P_guard_given_anchor_ci_low", "conditional_lift", "n_anchor", "anchor", "guard"],
                         ascending=[True, False, False, False, True, True])
            .drop(columns="_priority").reset_index(drop=True))

"""All directed same-row prop pairs; support-gated exploratory ranking."""
import numpy as np
import pandas as pd
from sports_dependency_engine.config import ResearchConfig
from sports_dependency_engine.dependency.implications import prove
from sports_dependency_engine.dependency.metrics import pair_metrics
from sports_dependency_engine.sports.mlb.props import Prop, outcomes


def search_pairs(frame: pd.DataFrame, props: list[Prop], config: ResearchConfig = ResearchConfig()) -> pd.DataFrame:
    if frame.empty or len(props) < 2:
        raise ValueError("Need observations and at least two props")
    matrix = outcomes(frame, props).to_numpy(dtype=np.int64)
    support = matrix.sum(axis=0)
    joints = matrix.T @ matrix
    rows = []
    for i, anchor in enumerate(props):
        for j, guard in enumerate(props):
            if i == j:
                continue
            m = pair_metrics(len(frame), int(support[i]), int(support[j]), int(joints[i, j]))
            proof = prove(anchor, guard)
            if proof.proven and m["n_violations"]:
                raise ValueError(f"Data contradicts proof: {anchor.label} => {guard.label}")
            eligible = m["n_anchor"] >= config.min_anchor and m["n_guard"] >= config.min_guard
            category = "WEAK_OR_NONE"
            if proof.proven:
                category = "EXACT_IMPLICATION"
            elif eligible and m["P_guard_given_anchor"] >= config.near_probability and m["P_guard_given_anchor_ci_low"] >= config.near_lower_bound:
                category = "EMPIRICAL_NEAR_IMPLICATION"
            elif eligible and m["conditional_lift"] >= config.strong_lift and m["P_guard_given_anchor_ci_low"] > m["P_guard_ci_high"]:
                category = "STRONG_DEPENDENCE"
            rows.append({"sport": anchor.sport, "anchor": anchor.label, "guard": guard.label,
                         **m, "type": category, "eligible": eligible, "proof": proof.explanation,
                         "rule_version": proof.rule_version})
    return pd.DataFrame(rows)

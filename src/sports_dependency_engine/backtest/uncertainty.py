"""One-way cluster-bootstrap sensitivity intervals, not multiway inference."""
import numpy as np
import pandas as pd
from sports_dependency_engine.dependency.combo_search import Combo
from sports_dependency_engine.sports.mlb.props import outcomes


def clustered_intervals(frame: pd.DataFrame, candidates: list[Combo], cluster: str,
                        replicates: int = 1000, seed: int = 1729) -> pd.DataFrame:
    """Resample whole games or whole players; retain resamples with anchor support.

    Perfect empirical agreement has a degenerate percentile interval. Keep Wilson
    intervals alongside these outputs; a zero-width bootstrap is never proof.
    Game and player resampling are separate sensitivity analyses, not a joint
    adjustment for both dependence structures or multiple candidate selection.
    """
    if type(replicates) is not int or not 100 <= replicates <= 5000:
        raise ValueError('Require 100–5000 bootstrap replicates')
    if frame.empty or frame[cluster].isna().any():
        raise ValueError('Require nonempty observations with complete cluster IDs')
    if not candidates:
        return pd.DataFrame(columns=['candidate_id'])
    codes, groups = pd.factorize(frame[cluster], sort=True)
    count = len(groups)
    if count < 2:
        raise ValueError('At least two clusters required')
    props = sorted({p for c in candidates for p in (c.anchor,) + c.guards}, key=lambda p: p.label)
    events = outcomes(frame, props)
    a_counts = np.zeros((count, len(candidates)), dtype=float)
    j_counts = np.zeros_like(a_counts)
    for j, combo in enumerate(candidates):
        a = events[combo.anchor.label].to_numpy(dtype=bool)
        joint = a & events[[p.label for p in combo.guards]].all(axis=1).to_numpy(dtype=bool)
        np.add.at(a_counts[:, j], codes, a)
        np.add.at(j_counts[:, j], codes, joint)
    rng = np.random.default_rng(seed)
    weights = rng.multinomial(count, np.full(count, 1/count), size=replicates).astype(float)
    anchors, joints = weights @ a_counts, weights @ j_counts
    totals = weights @ np.bincount(codes, minlength=count).astype(float)
    conditional = np.divide(joints, anchors, out=np.full_like(joints, np.nan), where=anchors > 0)
    leakage = (anchors-joints) / totals[:, None]
    rows = []
    for j, combo in enumerate(candidates):
        valid = conditional[:, j][np.isfinite(conditional[:, j])]
        low, high = np.quantile(valid, [.025, .975]) if len(valid) else (float('nan'), float('nan'))
        l_low, l_high = np.quantile(leakage[:, j], [.025, .975])
        rows.append({'candidate_id': combo.candidate_id, f'{cluster}_clusters': count,
                     f'{cluster}_bootstrap_valid': len(valid), f'{cluster}_bootstrap_replicates': replicates,
                     f'{cluster}_conditional_low': low, f'{cluster}_conditional_high': high,
                     f'{cluster}_leakage_low': l_low, f'{cluster}_leakage_high': l_high})
    return pd.DataFrame(rows)

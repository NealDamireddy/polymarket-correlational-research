"""Bounded same-player conjunction search, selected using training outcomes only."""
from dataclasses import asdict, dataclass
from hashlib import sha256
from itertools import combinations
import json
import numpy as np
import pandas as pd
from sports_dependency_engine.config import ResearchConfig
from sports_dependency_engine.dependency.implications import prove
from sports_dependency_engine.dependency.metrics import pair_metrics, wilson
from sports_dependency_engine.dependency.pair_search import search_pairs
from sports_dependency_engine.sports.mlb.props import Prop, outcomes


@dataclass(frozen=True)
class ComboConfig:
    min_anchor: int = 100
    min_guard: int = 100
    min_conditional: float = 0.99
    min_conditional_lower: float = 0.95
    max_guards: int = 3
    max_candidates_per_anchor: int = 10
    max_evaluations: int = 5000

    def __post_init__(self) -> None:
        for name in ('min_anchor', 'min_guard', 'max_guards', 'max_candidates_per_anchor', 'max_evaluations'):
            if type(getattr(self, name)) is not int or getattr(self, name) < 1:
                raise ValueError(f'{name} must be a positive integer')
        if self.max_guards > 3 or self.max_candidates_per_anchor > 20:
            raise ValueError('At most three guards and twenty candidates per anchor')
        if not 0 <= self.min_conditional_lower <= self.min_conditional <= 1:
            raise ValueError('Invalid conditional thresholds')


@dataclass(frozen=True)
class Combo:
    anchor: Prop
    guards: tuple[Prop, ...]

    def __post_init__(self) -> None:
        if not 1 <= len(self.guards) <= 3:
            raise ValueError('Require one to three guards')
        legs = (self.anchor,) + self.guards
        if len(set(legs)) != len(legs):
            raise ValueError('Duplicate legs')
        if len({(p.sport, p.scope) for p in legs}) != 1:
            raise ValueError('Combo legs must share sport and player-game scope')
        object.__setattr__(self, 'guards', tuple(sorted(self.guards, key=lambda p: p.label)))

    def to_dict(self) -> dict:
        return {'anchor': asdict(self.anchor), 'guards': [asdict(g) for g in self.guards]}

    @classmethod
    def from_dict(cls, value: dict) -> 'Combo':
        return cls(Prop(**value['anchor']), tuple(Prop(**g) for g in value['guards']))

    @property
    def candidate_id(self) -> str:
        return sha256(json.dumps(self.to_dict(), sort_keys=True).encode()).hexdigest()

    @property
    def exact(self) -> bool:
        return all(prove(self.anchor, g).proven for g in self.guards)

    def descriptor(self) -> dict:
        return {'candidate_id': self.candidate_id, 'sport': self.anchor.sport,
                'anchor': self.anchor.label, 'guards': ' & '.join(g.label for g in self.guards),
                'n_guards': len(self.guards),
                'type': 'EXACT_IMPLICATION' if self.exact else 'EMPIRICAL_CANDIDATE',
                'n_guards_proven_from_anchor': sum(prove(self.anchor, g).proven for g in self.guards),
                'proofs': json.dumps([asdict(prove(self.anchor, g)) for g in self.guards], sort_keys=True)}


def combo_metrics(anchor: np.ndarray, guards_joint: np.ndarray, exact: bool = False) -> dict:
    """Direct contingency counts; guard probabilities are never multiplied."""
    anchor = np.asarray(anchor)
    guards_joint = np.asarray(guards_joint)
    if anchor.ndim != 1 or anchor.shape != guards_joint.shape or anchor.dtype != bool or guards_joint.dtype != bool:
        raise ValueError('Require aligned one-dimensional boolean arrays')
    n = len(anchor)
    n_a = int(anchor.sum())
    n_joint = int((anchor & guards_joint).sum())
    if exact and n_joint != n_a:
        raise ValueError('Data contradicts exact combo proof')
    m = pair_metrics(n, n_a, int(guards_joint.sum()), n_joint)
    failures = n_a - n_joint
    low, high = wilson(failures, n)
    m.update(leakage=failures/n, leakage_ci_low=low, leakage_ci_high=high,
             conditional_failure=failures/n_a if n_a else float('nan'))
    # Exact model probability is a rule conclusion; empirical estimates remain separate.
    m['P_rule_guards_given_anchor'] = 1.0 if exact else float('nan')
    return m


def evaluate_combos(frame: pd.DataFrame, candidates: list[Combo]) -> pd.DataFrame:
    """Evaluate every frozen candidate, including unsupported/zero-anchor cases."""
    if frame.empty:
        raise ValueError('Cannot evaluate an empty cohort')
    props = sorted({p for c in candidates for p in (c.anchor,) + c.guards}, key=lambda p: p.label)
    matrix = outcomes(frame, props)
    rows = []
    for combo in candidates:
        anchor = matrix[combo.anchor.label].to_numpy(dtype=bool)
        guards = matrix[[p.label for p in combo.guards]].all(axis=1).to_numpy(dtype=bool)
        rows.append({**combo.descriptor(), **combo_metrics(anchor, guards, combo.exact)})
    if not rows:
        return pd.DataFrame(columns=['candidate_id', 'anchor', 'guards', 'type', 'n_guards'])
    return pd.DataFrame(rows)


def discover_combos(frame: pd.DataFrame, props: list[Prop], config: ComboConfig = ComboConfig()) -> tuple[list[Combo], pd.DataFrame, dict]:
    """Prune by support, pair bounds, per-anchor guard cap and a hard work budget.

    Fail on exhausted budget instead of silently returning a search-order prefix.
    Discovery is intentionally incomplete; cap exclusions are reported explicitly.
    """
    if len({(p.sport, p.scope) for p in props}) != 1:
        raise ValueError('Search requires one sport and one player-game scope')
    pair_config = ResearchConfig(min_anchor=config.min_anchor, min_guard=config.min_guard)
    pairs = search_pairs(frame, props, pair_config)
    eligible = pairs.loc[pairs.eligible & pairs.P_guard_given_anchor.ge(config.min_conditional)
                         & pairs.P_guard_given_anchor_ci_low.ge(config.min_conditional_lower)].copy()
    eligible['exact'] = eligible.type.eq('EXACT_IMPLICATION')
    eligible = eligible.sort_values(['anchor', 'exact', 'P_guard_given_anchor_ci_low', 'n_guard', 'guard'],
                                    ascending=[True, False, False, False, True])
    prop_by_label = {p.label: p for p in props}
    proposals: list[Combo] = []
    capped: dict[str, list[str]] = {}
    for anchor, guards in eligible.groupby('anchor', sort=True):
        capped[anchor] = guards.guard.iloc[config.max_candidates_per_anchor:].tolist()
        selected = guards.guard.iloc[:config.max_candidates_per_anchor].tolist()
        for size in range(1, min(config.max_guards, len(selected)) + 1):
            for labels in combinations(selected, size):
                if len(proposals) >= config.max_evaluations:
                    raise ValueError('Combo evaluation budget exceeded; reduce guard cap or raise explicit budget')
                proposals.append(Combo(prop_by_label[anchor], tuple(prop_by_label[x] for x in labels)))
    metrics = evaluate_combos(frame, proposals)
    if metrics.empty:
        return [], metrics, {'pair_candidates': len(eligible), 'evaluated': 0, 'retained': 0, 'capped_guards': capped}
    kept = metrics.loc[metrics.n_guard.ge(config.min_guard)
                       & metrics.P_guard_given_anchor.ge(config.min_conditional)
                       & metrics.P_guard_given_anchor_ci_low.ge(config.min_conditional_lower)].copy()
    kept['exact'] = kept.type.eq('EXACT_IMPLICATION')
    kept = kept.sort_values(['exact', 'P_guard_given_anchor_ci_low', 'leakage', 'n_anchor', 'candidate_id'],
                            ascending=[False, False, True, False, True]).drop(columns='exact').reset_index(drop=True)
    lookup = {c.candidate_id: c for c in proposals}
    ordered = [lookup[cid] for cid in kept.candidate_id]
    return ordered, kept, {'pair_candidates': len(eligible), 'evaluated': len(proposals),
                          'retained': len(ordered), 'capped_guards': capped,
                          'joint_screen_rejected': len(proposals)-len(ordered)}

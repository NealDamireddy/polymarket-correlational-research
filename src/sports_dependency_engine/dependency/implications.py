"""Monotone forward chaining on explicit stat lower bounds, never empirical proof."""
from dataclasses import dataclass
from sports_dependency_engine.sports.mlb.props import Prop
from sports_dependency_engine.sports.mlb.rules import RULES, SUM_DEFINITIONS, RULE_VERSION

@dataclass(frozen=True)
class Proof:
    proven: bool
    explanation: str
    rule_version: str = RULE_VERSION


def prove(anchor: Prop, guard: Prop) -> Proof:
    if anchor.sport != guard.sport or anchor.scope != guard.scope:
        return Proof(False, "Different sporting/settlement scopes")
    if anchor.stat == guard.stat and anchor.threshold >= guard.threshold:
        return Proof(True, "Threshold monotonicity")
    if anchor.sport != "mlb":
        return Proof(False, "No cross-stat rules for this sport")
    bounds = {anchor.stat: anchor.threshold}
    reasons: list[str] = []
    changed = True
    while changed:
        changed = False
        for rule in RULES:
            numerator = bounds.get(rule.source, 0) * rule.multiplier
            bound = (numerator + rule.divisor - 1) // rule.divisor
            if bound > bounds.get(rule.target, 0):
                bounds[rule.target] = bound
                reasons.append(rule.explanation)
                changed = True
        for target, terms in SUM_DEFINITIONS.items():
            bound = sum(bounds.get(term, 0) for term in terms)
            if bound > bounds.get(target, 0):
                bounds[target] = bound
                reasons.append(f"{target} is the sum of {', '.join(terms)}")
                changed = True
    proven = bounds.get(guard.stat, 0) >= guard.threshold
    return Proof(proven, "; ".join(reasons) if proven else "No proof from configured rules")

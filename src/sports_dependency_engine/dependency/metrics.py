"""Descriptive probabilities with marginal Wilson intervals (not simultaneous)."""
from math import sqrt, nan

def wilson(successes: int, trials: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if not 0 <= successes <= trials:
        raise ValueError("Require 0 <= successes <= trials")
    if trials == 0:
        return nan, nan
    p = successes / trials
    denominator = 1 + z*z / trials
    center = (p + z*z / (2*trials)) / denominator
    half = z * sqrt(p*(1-p)/trials + z*z/(4*trials*trials)) / denominator
    return (0.0 if successes == 0 else max(0.0, center-half),
            1.0 if successes == trials else min(1.0, center+half))


def pair_metrics(n: int, n_a: int, n_b: int, n_ab: int) -> dict[str, float | int]:
    if n <= 0 or not (0 <= n_ab <= min(n_a, n_b) <= max(n_a, n_b) <= n) or n_a+n_b-n_ab > n:
        raise ValueError("Invalid contingency counts")
    pa, pb, joint = n_a/n, n_b/n, n_ab/n
    conditional = n_ab/n_a if n_a else nan
    values = {"n": n, "n_anchor": n_a, "n_guard": n_b, "n_joint": n_ab,
              "n_violations": n_a-n_ab, "P_anchor": pa, "P_guard": pb,
              "joint_prob": joint, "P_guard_given_anchor": conditional,
              "P_anchor_given_guard": n_ab/n_b if n_b else nan,
              "dependency_ratio": joint/(pa*pb) if pa*pb else nan,
              "conditional_lift": conditional/pb if pb else nan}
    for name, successes, trials in (("P_anchor", n_a, n), ("P_guard", n_b, n),
                                   ("joint_prob", n_ab, n),
                                   ("P_guard_given_anchor", n_ab, n_a),
                                   ("P_anchor_given_guard", n_ab, n_b)):
        values[name+"_ci_low"], values[name+"_ci_high"] = wilson(successes, trials)
    return values

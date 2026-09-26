"""Conservative lower-bound rules from official credited batting statistics.

Applies to identical player/game/stat settlement, not arbitrary market wording.
Rule 9.06 covers hits/total bases and Rule 9.04 RBI. A credited home run
credits its batter a hit, run and RBI. Walk-off non-HR hits are not home runs.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class LowerBoundRule:
    source: str
    target: str
    multiplier: int
    explanation: str
    divisor: int = 1

RULES = (
    LowerBoundRule("total_bases", "hits", 1, "At most four TB per hit, so hits >= ceil(TB/4)", divisor=4),
    LowerBoundRule("home_runs", "hits", 1, "Each credited HR is a hit"),
    LowerBoundRule("home_runs", "total_bases", 4, "Each credited HR contributes four TB"),
    LowerBoundRule("home_runs", "runs", 1, "The credited HR batter scores"),
    LowerBoundRule("home_runs", "RBI", 1, "The credited HR includes the batter's RBI"),
    LowerBoundRule("hits", "total_bases", 1, "Each hit contributes at least one TB"),
    LowerBoundRule("hits", "hits_plus_runs_plus_RBI", 1, "HRR includes nonnegative hits"),
    LowerBoundRule("runs", "hits_plus_runs_plus_RBI", 1, "HRR includes nonnegative runs"),
    LowerBoundRule("RBI", "hits_plus_runs_plus_RBI", 1, "HRR includes nonnegative RBI"),
)
SUM_DEFINITIONS = {"hits_plus_runs_plus_RBI": ("hits", "runs", "RBI")}
RULE_VERSION = "mlb-official-batting-v1"

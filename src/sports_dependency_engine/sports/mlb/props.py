"""Binary propositions evaluated on one player's official full-game batting line."""
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class Prop:
    stat: str
    threshold: int
    operator: str = ">="
    sport: str = "mlb"
    scope: str = "same_player_full_game"

    def __post_init__(self) -> None:
        if self.operator != ">=" or type(self.threshold) is not int or self.threshold < 1:
            raise ValueError("Only positive integer >= thresholds are supported")

    @property
    def label(self) -> str:
        return f"{self.stat}>={self.threshold}"

    def evaluate(self, frame: pd.DataFrame) -> pd.Series:
        values = frame[self.stat]
        if values.isna().any():
            raise ValueError(f"Missing outcomes in {self.stat}")
        return values.ge(self.threshold)


def default_props() -> list[Prop]:
    families = {"home_runs": 2, "hits": 3, "total_bases": 6,
                "hits_plus_runs_plus_RBI": 6, "runs": 2, "RBI": 3}
    return [Prop(stat, n) for stat, maximum in families.items() for n in range(1, maximum + 1)]


def outcomes(frame: pd.DataFrame, props: list[Prop]) -> pd.DataFrame:
    if len({p.label for p in props}) != len(props):
        raise ValueError("Duplicate proposition labels")
    return pd.DataFrame({p.label: p.evaluate(frame) for p in props}, index=frame.index)

"""Fail-closed validation plus explicit exclusions and missingness reporting."""
import pandas as pd
from sports_dependency_engine.sports.mlb.player_games import NUMERIC

def validate(frame: pd.DataFrame) -> dict:
    if frame.empty:
        raise ValueError("Empty player-game dataset")
    if frame.duplicated(["game_id", "player_id"]).any():
        raise ValueError("Duplicate player-game keys")
    required = NUMERIC + ["game_id", "date", "player_id", "player_name", "team", "opponent"]
    if frame[required].isna().any().any():
        raise ValueError("Missing required data")
    values = frame[NUMERIC]
    if (values < 0).any().any() or (values % 1 != 0).any().any():
        raise ValueError("Batting counts must be nonnegative integers")
    checks = {
        "hits_decomposition": frame.hits == frame.singles+frame.doubles+frame.triples+frame.home_runs,
        "total_bases": frame.total_bases == frame.singles+2*frame.doubles+3*frame.triples+4*frame.home_runs,
        "hrr": frame.hits_plus_runs_plus_RBI == frame.hits+frame.runs+frame.RBI,
        "hits_le_ab": frame.hits <= frame.at_bats,
        "ab_le_pa": frame.at_bats <= frame.plate_appearances,
        "hr_le_runs": frame.home_runs <= frame.runs,
        "hr_le_rbi": frame.home_runs <= frame.RBI,
    }
    failures = {name: int((~ok).sum()) for name, ok in checks.items()}
    if any(failures.values()):
        raise ValueError(f"Invalid scoring identities: {failures}")
    return {"rows": len(frame), "games": int(frame.game_id.nunique()),
            "players": int(frame.player_id.nunique()), "start": str(frame.date.min()), "end": str(frame.date.max()),
            "missing_by_column": frame.isna().sum().astype(int).to_dict(), "identity_violations": failures,
            "zero_pa_rows": int(frame.plate_appearances.eq(0).sum())}

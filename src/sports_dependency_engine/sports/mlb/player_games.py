"""Normalize official per-player box scores; never reconstruct RBI from pitches."""
from typing import Any

STAT_FIELDS = {"plate_appearances": "plateAppearances", "at_bats": "atBats", "hits": "hits",
               "doubles": "doubles", "triples": "triples", "home_runs": "homeRuns",
               "runs": "runs", "RBI": "rbi", "walks": "baseOnBalls",
               "strikeouts": "strikeOuts", "stolen_bases": "stolenBases"}
NUMERIC = list(STAT_FIELDS) + ["singles", "total_bases", "hits_plus_runs_plus_RBI"]


def player_rows(game: dict, box: dict) -> tuple[list[dict[str, Any]], list[dict]]:
    rows, excluded = [], []
    for side, other in (("home", "away"), ("away", "home")):
        team = box["teams"][side]
        side_rows = []
        for player_id in team["batters"]:
            player = team["players"][f"ID{player_id}"]
            stats = player.get("stats", {}).get("batting", {})
            if not stats:
                excluded.append({"game_id": game["gamePk"], "player_id": player_id, "reason": "no_batting_line"})
                continue
            missing = [source for source in STAT_FIELDS.values() if source not in stats]
            if missing:
                raise ValueError(f"Game {game['gamePk']} player {player_id}: missing {missing}")
            row = {target: stats[source] for target, source in STAT_FIELDS.items()}
            row["singles"] = row["hits"]-row["doubles"]-row["triples"]-row["home_runs"]
            row["total_bases"] = row["singles"]+2*row["doubles"]+3*row["triples"]+4*row["home_runs"]
            row["hits_plus_runs_plus_RBI"] = row["hits"]+row["runs"]+row["RBI"]
            row.update(game_id=game["gamePk"], date=game["officialDate"], season=int(game["season"]),
                       player_id=player_id, player_name=player["person"]["fullName"],
                       team=team["team"]["name"], opponent=box["teams"][other]["team"]["name"],
                       home_away=side, batting_order=player.get("battingOrder"), park=game.get("venue", {}).get("name"))
            side_rows.append(row)
        # Include pinch runners with 0 PA when reconciling team totals.
        for target, source in STAT_FIELDS.items():
            actual = sum(r[target] for r in side_rows)
            expected = team["teamStats"]["batting"][source]
            if actual != expected:
                raise ValueError(f"Game {game['gamePk']} {side}: {target} player sum {actual} != team {expected}")
        if not side_rows:
            raise ValueError(f"No batting rows for {game['gamePk']} {side}")
        rows.extend(side_rows)
    return rows, excluded

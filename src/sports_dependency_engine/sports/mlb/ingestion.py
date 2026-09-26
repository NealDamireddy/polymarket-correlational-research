"""MLB official schedule and box scores, chunked by calendar month from 2015."""
from datetime import date, timedelta
from sports_dependency_engine.io import CachedClient

BASE = "https://statsapi.mlb.com/api/v1"

def schedule(client: CachedClient, start: str, end: str) -> tuple[list[dict], list[dict]]:
    cursor, last = date.fromisoformat(start), date.fromisoformat(end)
    if cursor > last or cursor.year < 2015:
        raise ValueError("Require 2015-01-01 <= start <= end")
    entries: dict[int, list[dict]] = {}
    while cursor <= last:
        next_month = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)
        stop = min(last, next_month-timedelta(days=1))
        payload = client.get(f"{BASE}/schedule", {"sportId": 1, "startDate": cursor.isoformat(), "endDate": stop.isoformat(), "gameType": "R"})
        for day in payload["dates"]:
            for game in day["games"]:
                entries.setdefault(game["gamePk"], []).append({**game, "officialDate": game.get("officialDate", day["date"])})
        cursor = stop + timedelta(days=1)

    def exclusion_reason(game: dict) -> str | None:
        if not start <= game["officialDate"] <= end:
            return "official_date_outside_window"
        if game.get("gameType") != "R":
            return "not_regular_season"
        if game["status"].get("abstractGameState") != "Final":
            return game["status"].get("detailedState", "not_final")
        if game["status"].get("codedGameState") not in ("F", "O"):
            return "nonstandard_final_status"
        return None

    eligible, excluded = [], []
    for gid, versions in entries.items():
        # A postponed entry may precede the completed makeup game with the same ID.
        # Select an eligible final version before deduplicating schedule entries.
        selected = next((i for i, g in enumerate(versions) if exclusion_reason(g) is None), 0)
        for i, game in enumerate(versions):
            reason = "duplicate_schedule_entry" if i != selected else exclusion_reason(game)
            if reason:
                excluded.append({"game_id": gid, "reason": reason,
                                 "official_date": game["officialDate"], "status": game["status"]})
            else:
                eligible.append(game)
    return sorted(eligible, key=lambda g: (g["officialDate"], g["gamePk"])), excluded


def boxscore(client: CachedClient, game_id: int) -> dict:
    return client.get(f"{BASE}/game/{game_id}/boxscore")

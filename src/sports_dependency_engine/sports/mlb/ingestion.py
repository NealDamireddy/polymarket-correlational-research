"""MLB official schedule and box scores, chunked by calendar month from 2015."""
from datetime import date, timedelta
from sports_dependency_engine.io import CachedClient

BASE = "https://statsapi.mlb.com/api/v1"

def schedule(client: CachedClient, start: str, end: str) -> tuple[list[dict], list[dict]]:
    cursor, last = date.fromisoformat(start), date.fromisoformat(end)
    if cursor > last or cursor.year < 2015:
        raise ValueError("Require 2015-01-01 <= start <= end")
    eligible, excluded, seen = [], [], set()
    while cursor <= last:
        next_month = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)
        stop = min(last, next_month-timedelta(days=1))
        payload = client.get(f"{BASE}/schedule", {"sportId": 1, "startDate": cursor.isoformat(), "endDate": stop.isoformat(), "gameType": "R"})
        for day in payload["dates"]:
            for game in day["games"]:
                gid = game["gamePk"]
                if gid in seen:
                    excluded.append({"game_id": gid, "reason": "duplicate_schedule_entry"})
                    continue
                seen.add(gid)
                official = game.get("officialDate", day["date"])
                reason = None
                if not start <= official <= end:
                    reason = "official_date_outside_window"
                elif game.get("gameType") != "R":
                    reason = "not_regular_season"
                elif game["status"].get("abstractGameState") != "Final":
                    reason = game["status"].get("detailedState", "not_final")
                elif game["status"].get("codedGameState") not in ("F", "O"):
                    reason = "nonstandard_final_status"
                if reason:
                    excluded.append({"game_id": gid, "reason": reason})
                else:
                    eligible.append({**game, "officialDate": official})
        cursor = stop + timedelta(days=1)
    return sorted(eligible, key=lambda g: (g["officialDate"], g["gamePk"])), excluded


def boxscore(client: CachedClient, game_id: int) -> dict:
    return client.get(f"{BASE}/game/{game_id}/boxscore")

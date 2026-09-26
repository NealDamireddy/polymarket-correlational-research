"""Reproducible Milestone 1 CLI. No prices or trading enter the outcome pipeline."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import importlib.metadata
import json
import hashlib
from pathlib import Path
import sys
import pandas as pd
from sports_dependency_engine.config import ResearchConfig
from sports_dependency_engine.io import CachedClient
from sports_dependency_engine.sports.mlb.ingestion import schedule, boxscore
from sports_dependency_engine.sports.mlb.player_games import player_rows
from sports_dependency_engine.sports.mlb.props import default_props, outcomes
from sports_dependency_engine.dependency.pair_search import search_pairs
from sports_dependency_engine.reports.diagnostics import validate
from sports_dependency_engine.reports.rankings import rank_pairs
from sports_dependency_engine.reports.research import research_report


def run(start: str, end: str, root: Path, offline: bool = False, config: ResearchConfig = ResearchConfig()) -> Path:
    client = CachedClient(root / "data/raw/mlb", offline=offline)
    run_id = f"{start}_{end}"
    processed = root / "data/processed" / run_id
    output = root / "outputs" / run_id
    output.mkdir(parents=True, exist_ok=True)
    rows, excluded_players = [], []
    try:
        games, excluded_games = schedule(client, start, end)
        for i, game in enumerate(games):
            new, excluded = player_rows(game, boxscore(client, game["gamePk"]))
            rows.extend(new)
            excluded_players.extend(excluded)
            if (i+1) % 25 == 0:
                print(f"Validated {i+1}/{len(games)} games", flush=True)
        frame = pd.DataFrame(rows).sort_values(["date", "game_id", "player_id"]).reset_index(drop=True) if rows else pd.DataFrame()
        validation = validate(frame)
        if validation["games"] != len(games):
            raise ValueError("Processed game count differs from eligible schedule")
        cohort = frame.loc[frame.plate_appearances.gt(0)].reset_index(drop=True)
        props = default_props()
        pairs = search_pairs(cohort, props, config)
        ranked = rank_pairs(pairs)
        manifest = {"schema_version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
                    "requested_start": start, "requested_end": end, "analysis_rows": len(cohort),
                    "cohort": "regular season, final, plate_appearances > 0; pooled same-player full-game",
                    "config": asdict(config), "props": [asdict(p) for p in props],
                    "excluded_games": excluded_games, "excluded_players": excluded_players,
                    "raw_files": list(client.used.values()),
                    "source_sha256": {str(p.relative_to(Path(__file__).parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in sorted(Path(__file__).parent.rglob("*.py"))},
                    "python": sys.version,
                    "dependencies": {x: importlib.metadata.version(x) for x in ["numpy", "pandas", "pyarrow", "requests"]}}
        processed.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(processed / "player_games.parquet", index=False)
        pd.concat([cohort[["game_id", "player_id", "date"]], outcomes(cohort, props)], axis=1).to_parquet(processed / "prop_outcomes.parquet", index=False)
        pairs.to_csv(output / "all_pairs.csv", index=False)
        ranked.to_csv(output / "ranked_pairs.csv", index=False)
        (output / "validation.json").write_text(json.dumps(validation, indent=2))
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2))
        (output / "research_report.md").write_text(research_report(validation, pairs, ranked, manifest))
        (output / "failure.json").unlink(missing_ok=True)
        print(f"Completed: {validation['games']} games, {len(cohort)} cohort rows, {len(ranked)} ranked pairs. {output}")
        return output
    except Exception as exc:
        (output / "failure.json").write_text(json.dumps({"error": str(exc), "rows_accumulated": len(rows), "raw_files": list(client.used.values())}, indent=2))
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True, help="YYYY-MM-DD, 2015 onward")
    parser.add_argument("--end", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--offline", action="store_true", help="Require cached inputs; no network calls")
    parser.add_argument("--min-anchor", type=int, default=100)
    parser.add_argument("--min-guard", type=int, default=100)
    args = parser.parse_args()
    run(args.start, args.end, args.root, args.offline, ResearchConfig(min_anchor=args.min_anchor, min_guard=args.min_guard))

if __name__ == "__main__":
    main()

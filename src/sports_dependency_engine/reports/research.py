"""Small Markdown research report generated exclusively from pipeline outputs."""
import pandas as pd

def table(frame: pd.DataFrame, columns: list[str], limit: int = 10) -> str:
    if frame.empty:
        return "No supported relationships in this category.\n"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in frame[columns].head(limit).itertuples(index=False, name=None):
        lines.append("| " + " | ".join(f"{x:.4f}" if isinstance(x, float) else str(x) for x in row) + " |")
    return "\n".join(lines) + "\n"


def research_report(validation: dict, pairs: pd.DataFrame, ranked: pd.DataFrame, manifest: dict) -> str:
    columns = ["anchor", "guard", "n_anchor", "P_guard_given_anchor", "P_guard_given_anchor_ci_low", "dependency_ratio"]
    exact = ranked[ranked.type.eq("EXACT_IMPLICATION")]
    near = ranked[ranked.type.eq("EMPIRICAL_NEAR_IMPLICATION")].sort_values("n_anchor", ascending=False)
    high = ranked.sort_values(["dependency_ratio", "n_anchor"], ascending=False)
    nonexact = high[~high.type.eq("EXACT_IMPLICATION")]
    missing = {k: v for k, v in validation["missing_by_column"].items() if v}
    return f'''# MLB dependency research — Milestone 1

## Dataset and cohort

Official MLB regular-season box scores, {validation['start']} through {validation['end']}.
{validation['games']:,} games; {validation['rows']:,} player-game rows; {validation['players']:,} distinct players.
The analysis includes {manifest['analysis_rows']:,} player-games with at least one plate appearance.
{validation['zero_pa_rows']} zero-PA rows are preserved in Parquet but excluded from this explicitly defined cohort.
{len(manifest['excluded_games'])} schedule entries excluded; {len(manifest['excluded_players'])} entries without batting lines.
See manifest.json for each exclusion and raw file hashes. Team totals reconciled for every processed game.
Missing values by column: {missing or 'none in collected columns'}.
Pitcher handedness, temperature and wind are not collected in this milestone; batting_order is the raw MLB order/substitution code.
This run is a bounded validation window, not a full 2015–present download.

## Statistical policy

Policy: {manifest['config']}. All {len(pairs)} directed pairs are retained;
{len(ranked)} meet both support thresholds and enter the ranking.
Intervals are nominal marginal 95% Wilson intervals. They assume independent Bernoulli observations;
repeated players and shared games violate that approximation. They are descriptive, not clustered,
simultaneous or adjusted for selection. Lift and dependency ratio are algebraically identical here,
not two independent pieces of evidence. Ratios have no uncertainty interval in this milestone.
Pooled player-game results do not estimate any specific player's future probability.

## Mechanically proven implications

{len(pairs[pairs.type.eq('EXACT_IMPLICATION')])} directed proofs across the configured prop grid;
{len(exact)} meet the support thresholds. No observed proof violations.
Proof explanations and rule versions appear in all_pairs.csv. Exactness assumes identical player,
game scope and official-stat settlement, including consistent void and participation rules.

{table(exact, columns)}
## Highest-support empirical near-implications

{table(near, columns)}
## Highest dependency ratios (including exact relationships)

{table(high, columns)}
## Highest non-exact dependency ratios

{table(nonexact, columns)}
## Interpretation and next validation

This is exploratory outcome research, not evidence of an executable betting edge.
No Polymarket prices were joined and no out-of-sample predictive claims are made.
The configured rules and support policy were fixed before this run. Freeze candidates before
chronological holdout evaluation; use player/game-aware uncertainty, season stability checks,
and market-specific participation/settlement alignment before pricing comparisons.
Historical box scores may contain later official corrections; retrieval timestamps do not make
these records point-in-time data. Suspended-game completion and correction timestamps must be
resolved before historical price backtests. The backtest modules are intentionally not implemented.
'''

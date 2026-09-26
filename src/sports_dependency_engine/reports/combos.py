"""Outcome-only combo validation report; retain frozen training order."""
import pandas as pd
from sports_dependency_engine.reports.research import table


def combo_report(results: pd.DataFrame, manifest: dict) -> str:
    if results.empty:
        findings = 'No candidates passed the training screen. The holdout was not searched for replacements.'
    else:
        exact = results.loc[results.type.eq('EXACT_IMPLICATION')]
        empirical = results.loc[~results.type.eq('EXACT_IMPLICATION')]
        columns = ['anchor', 'guards', 'train_n_anchor', 'test_n_anchor',
                   'train_P_guard_given_anchor', 'test_P_guard_given_anchor', 'test_leakage']
        counts = results.groupby('n_guards').size().to_dict()
        findings = f'''Frozen list: **{len(results)}** structures; guard-count breakdown: {counts}.
**{len(exact)}** have every guard mechanically implied by the anchor;
**{len(empirical)}** rely at least partly on empirical agreement.
{int(results.test_support_sufficient.sum())} meet holdout support thresholds;
{int(results.test_screen_pass.sum())} meet the original joint-conditional screen in holdout.
These flags describe validation outcomes, not a newly selected list.

## Exact structures (first ten in frozen training order)

{table(exact, columns)}
## Empirical structures (first ten in frozen training order)

{table(empirical, columns)}
## Empirical validation summary

{int(empirical.test_screen_pass.sum())} of {len(empirical)} empirical structures pass the original screen in holdout.
{int(empirical.test_n_violations.gt(0).sum())} have at least one holdout guard failure when the anchor occurred.
Every candidate, including failures and insufficient-support cases, is retained in holdout_combos.csv.
Different leg lists often describe the same sporting event. These counts are not independent discoveries.
'''
    return f'''# MLB combo search and chronological validation — Milestone 2

## Data and frozen selection

Training: {manifest['train_start']}–{manifest['train_end']}, {manifest['train_games']} games,
{manifest['train_rows']:,} positive-PA player-games.
Holdout: {manifest['test_start']}–{manifest['test_end']}, {manifest['test_games']} games,
{manifest['test_rows']:,} positive-PA player-games.
All combinations refer to a single player's full game, pooled across players.
Candidate checksum: `{manifest['frozen_sha256']}`.

Policy: {manifest['config']}.
Pair candidates: {manifest['search_audit']['pair_candidates']}; evaluated combinations:
{manifest['search_audit']['evaluated']}; retained: {manifest['search_audit']['retained']}.
Per-anchor cap exclusions are listed in the frozen bundle. The search is bounded and incomplete.
No holdout outcome influences candidate inclusion or displayed ordering.

{findings}
## Leakage and uncertainty

Guards are evaluated as a conjunction on each row. No pair probabilities are multiplied.
Leakage = (anchor occurrences minus anchor-and-all-guards occurrences) / total player-games.
The conditional failure rate uses anchor occurrences as its denominator; these are different quantities.
P_guard in the CSV means the probability of the entire guard conjunction.
Exact rule probabilities are separate from empirical estimates and require matching market settlement.

The CSV includes marginal 95% Wilson intervals plus {manifest['bootstrap_replicates']} bootstrap
resamples of whole games and, separately, whole players (seed {manifest['bootstrap_seed']}).
These are one-way sensitivity intervals, not a simultaneous two-way cluster adjustment.
Each bootstrap reports valid conditional replicates; zero-anchor replicates are omitted from conditional
quantiles. A perfect observed rate produces a degenerate percentile bootstrap interval; retain the Wilson
interval and do not interpret bootstrap perfection as certainty. Zero-anchor candidates have undefined
empirical conditionals and remain in the output. No multiplicity correction is claimed.

## Limits and next step

This is retrospective chronological validation by official game date. Source box scores are final,
possibly corrected records. Historical availability times and suspended-game completion have not been
reconstructed, so this is **not a point-in-time backtest**. Repeated players can appear in both periods,
which matches later-game validation but does not test unseen-player generalization. Two months do not
establish multi-season stability; extend with predeclared rolling or untouched season holdouts next.

No actual Polymarket combo quotes, fees, depth or settlement terms were compared. Logical redundancy
and low sporting leakage alone do not establish an executable edge. Same-player eligibility remains
unverified. No trading or authenticated quote requests are implemented.
'''

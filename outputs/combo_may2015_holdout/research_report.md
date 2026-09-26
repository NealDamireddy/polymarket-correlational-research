# MLB combo search and chronological validation — Milestone 2

## Data and frozen selection

Training: 2015-04-05–2015-04-30, 327 games,
6,863 positive-PA player-games.
Holdout: 2015-05-01–2015-05-31, 428 games,
8,936 positive-PA player-games.
All combinations refer to a single player's full game, pooled across players.
Candidate checksum: `cc32e52b2a8aeb1959655622c5dd2a2bd8a0d387c3ffa2be201c057019c07485`.

Policy: {'min_anchor': 100, 'min_guard': 100, 'min_conditional': 0.99, 'min_conditional_lower': 0.95, 'max_guards': 3, 'max_candidates_per_anchor': 10, 'max_evaluations': 5000}.
Pair candidates: 106; evaluated combinations:
1034; retained: 1034.
Per-anchor cap exclusions are listed in the frozen bundle. The search is bounded and incomplete.
No holdout outcome influences candidate inclusion or displayed ordering.

Frozen list: **1034** structures; guard-count breakdown: {1: 105, 2: 311, 3: 618}.
**656** have every guard mechanically implied by the anchor;
**378** rely at least partly on empirical agreement.
1034 meet holdout support thresholds;
1012 meet the original joint-conditional screen in holdout.
These flags describe validation outcomes, not a newly selected list.

## Exact structures (first ten in frozen training order)

| anchor | guards | train_n_anchor | test_n_anchor | train_P_guard_given_anchor | test_P_guard_given_anchor | test_leakage |
| --- | --- | --- | --- | --- | --- | --- |
| hits>=1 | total_bases>=1 | 3819 | 5098 | 1.0000 | 1.0000 | 0.0000 |
| hits>=1 | hits_plus_runs_plus_RBI>=1 | 3819 | 5098 | 1.0000 | 1.0000 | 0.0000 |
| hits>=1 | hits_plus_runs_plus_RBI>=1 & total_bases>=1 | 3819 | 5098 | 1.0000 | 1.0000 | 0.0000 |
| total_bases>=1 | hits>=1 & hits_plus_runs_plus_RBI>=1 | 3819 | 5098 | 1.0000 | 1.0000 | 0.0000 |
| total_bases>=1 | hits>=1 | 3819 | 5098 | 1.0000 | 1.0000 | 0.0000 |
| total_bases>=1 | hits_plus_runs_plus_RBI>=1 | 3819 | 5098 | 1.0000 | 1.0000 | 0.0000 |
| hits_plus_runs_plus_RBI>=2 | hits_plus_runs_plus_RBI>=1 | 2787 | 3651 | 1.0000 | 1.0000 | 0.0000 |
| runs>=1 | hits_plus_runs_plus_RBI>=1 | 2252 | 2839 | 1.0000 | 1.0000 | 0.0000 |
| total_bases>=2 | hits>=1 | 2181 | 2869 | 1.0000 | 1.0000 | 0.0000 |
| total_bases>=2 | hits_plus_runs_plus_RBI>=1 | 2181 | 2869 | 1.0000 | 1.0000 | 0.0000 |

## Empirical structures (first ten in frozen training order)

| anchor | guards | train_n_anchor | test_n_anchor | train_P_guard_given_anchor | test_P_guard_given_anchor | test_leakage |
| --- | --- | --- | --- | --- | --- | --- |
| hits_plus_runs_plus_RBI>=4 | hits_plus_runs_plus_RBI>=1 & hits_plus_runs_plus_RBI>=3 & total_bases>=1 | 1017 | 1265 | 1.0000 | 1.0000 | 0.0000 |
| hits_plus_runs_plus_RBI>=4 | hits_plus_runs_plus_RBI>=1 & total_bases>=1 | 1017 | 1265 | 1.0000 | 1.0000 | 0.0000 |
| hits_plus_runs_plus_RBI>=4 | hits>=1 & hits_plus_runs_plus_RBI>=1 & total_bases>=1 | 1017 | 1265 | 1.0000 | 1.0000 | 0.0000 |
| hits_plus_runs_plus_RBI>=4 | hits>=1 & hits_plus_runs_plus_RBI>=2 & total_bases>=1 | 1017 | 1265 | 1.0000 | 1.0000 | 0.0000 |
| hits_plus_runs_plus_RBI>=4 | hits>=1 & hits_plus_runs_plus_RBI>=2 | 1017 | 1265 | 1.0000 | 1.0000 | 0.0000 |
| hits_plus_runs_plus_RBI>=4 | hits>=1 & hits_plus_runs_plus_RBI>=1 & hits_plus_runs_plus_RBI>=3 | 1017 | 1265 | 1.0000 | 1.0000 | 0.0000 |
| hits_plus_runs_plus_RBI>=4 | hits>=1 & hits_plus_runs_plus_RBI>=1 & hits_plus_runs_plus_RBI>=2 | 1017 | 1265 | 1.0000 | 1.0000 | 0.0000 |
| hits_plus_runs_plus_RBI>=4 | hits>=1 & hits_plus_runs_plus_RBI>=3 & total_bases>=1 | 1017 | 1265 | 1.0000 | 1.0000 | 0.0000 |
| hits_plus_runs_plus_RBI>=4 | total_bases>=1 | 1017 | 1265 | 1.0000 | 1.0000 | 0.0000 |
| hits_plus_runs_plus_RBI>=4 | hits>=1 & hits_plus_runs_plus_RBI>=2 & hits_plus_runs_plus_RBI>=3 | 1017 | 1265 | 1.0000 | 1.0000 | 0.0000 |

## Empirical validation summary

356 of 378 empirical structures pass the original screen in holdout.
212 have at least one holdout guard failure when the anchor occurred.
Every candidate, including failures and insufficient-support cases, is retained in holdout_combos.csv.
Different leg lists often describe the same sporting event. These counts are not independent discoveries.

## Leakage and uncertainty

Guards are evaluated as a conjunction on each row. No pair probabilities are multiplied.
Leakage = (anchor occurrences minus anchor-and-all-guards occurrences) / total player-games.
The conditional failure rate uses anchor occurrences as its denominator; these are different quantities.
P_guard in the CSV means the probability of the entire guard conjunction.
Exact rule probabilities are separate from empirical estimates and require matching market settlement.

The CSV includes marginal 95% Wilson intervals plus 1000 bootstrap
resamples of whole games and, separately, whole players (seed 1729).
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

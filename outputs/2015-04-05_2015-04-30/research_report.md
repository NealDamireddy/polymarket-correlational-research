# MLB dependency research — Milestone 1

## Dataset and cohort

Official MLB regular-season box scores, 2015-04-05 through 2015-04-30.
327 games; 8,079 player-game rows; 712 distinct players.
The analysis includes 6,863 player-games with at least one plate appearance.
1216 zero-PA rows are preserved in Parquet but excluded from this explicitly defined cohort.
7 schedule entries excluded; 1280 entries without batting lines.
See manifest.json for each exclusion and raw file hashes. Team totals reconciled for every processed game.
Missing values by column: none in collected columns.
Pitcher handedness, temperature and wind are not collected in this milestone; batting_order is the raw MLB order/substitution code.
This run is a bounded validation window, not a full 2015–present download.

## Statistical policy

Policy: {'min_anchor': 100, 'min_guard': 100, 'near_probability': 0.99, 'near_lower_bound': 0.95, 'strong_lift': 1.5}. All 462 directed pairs are retained;
420 meet both support thresholds and enter the ranking.
Intervals are nominal marginal 95% Wilson intervals. They assume independent Bernoulli observations;
repeated players and shared games violate that approximation. They are descriptive, not clustered,
simultaneous or adjusted for selection. Lift and dependency ratio are algebraically identical here,
not two independent pieces of evidence. Ratios have no uncertainty interval in this milestone.
Pooled player-game results do not estimate any specific player's future probability.

## Mechanically proven implications

103 directed proofs across the configured prop grid;
84 meet the support thresholds. No observed proof violations.
Proof explanations and rule versions appear in all_pairs.csv. Exactness assumes identical player,
game scope and official-stat settlement, including consistent void and participation rules.

| anchor | guard | n_anchor | P_guard_given_anchor | P_guard_given_anchor_ci_low | dependency_ratio |
| --- | --- | --- | --- | --- | --- |
| hits>=1 | total_bases>=1 | 3819 | 1.0000 | 0.9990 | 1.7971 |
| total_bases>=1 | hits>=1 | 3819 | 1.0000 | 0.9990 | 1.7971 |
| hits>=1 | hits_plus_runs_plus_RBI>=1 | 3819 | 1.0000 | 0.9990 | 1.6133 |
| total_bases>=1 | hits_plus_runs_plus_RBI>=1 | 3819 | 1.0000 | 0.9990 | 1.6133 |
| hits_plus_runs_plus_RBI>=2 | hits_plus_runs_plus_RBI>=1 | 2787 | 1.0000 | 0.9986 | 1.6133 |
| runs>=1 | hits_plus_runs_plus_RBI>=1 | 2252 | 1.0000 | 0.9983 | 1.6133 |
| total_bases>=2 | hits>=1 | 2181 | 1.0000 | 0.9982 | 1.7971 |
| total_bases>=2 | total_bases>=1 | 2181 | 1.0000 | 0.9982 | 1.7971 |
| total_bases>=2 | hits_plus_runs_plus_RBI>=1 | 2181 | 1.0000 | 0.9982 | 1.6133 |
| RBI>=1 | hits_plus_runs_plus_RBI>=1 | 1778 | 1.0000 | 0.9978 | 1.6133 |

## Highest-support empirical near-implications

| anchor | guard | n_anchor | P_guard_given_anchor | P_guard_given_anchor_ci_low | dependency_ratio |
| --- | --- | --- | --- | --- | --- |
| hits_plus_runs_plus_RBI>=3 | hits>=1 | 1770 | 0.9972 | 0.9934 | 1.7920 |
| hits_plus_runs_plus_RBI>=3 | total_bases>=1 | 1770 | 0.9972 | 0.9934 | 1.7920 |
| total_bases>=3 | hits_plus_runs_plus_RBI>=2 | 1215 | 0.9918 | 0.9849 | 2.4422 |
| hits_plus_runs_plus_RBI>=4 | hits>=1 | 1017 | 1.0000 | 0.9962 | 1.7971 |
| hits_plus_runs_plus_RBI>=4 | total_bases>=1 | 1017 | 1.0000 | 0.9962 | 1.7971 |
| total_bases>=4 | hits_plus_runs_plus_RBI>=2 | 791 | 1.0000 | 0.9952 | 2.4625 |
| total_bases>=4 | hits_plus_runs_plus_RBI>=3 | 791 | 0.9962 | 0.9889 | 3.8627 |
| RBI>=2 | hits>=1 | 593 | 0.9916 | 0.9804 | 1.7819 |
| RBI>=2 | total_bases>=1 | 593 | 0.9916 | 0.9804 | 1.7819 |
| RBI>=2 | hits_plus_runs_plus_RBI>=3 | 593 | 0.9949 | 0.9852 | 3.8578 |

## Highest dependency ratios (including exact relationships)

| anchor | guard | n_anchor | P_guard_given_anchor | P_guard_given_anchor_ci_low | dependency_ratio |
| --- | --- | --- | --- | --- | --- |
| total_bases>=5 | total_bases>=6 | 359 | 0.4513 | 0.4006 | 19.1170 |
| total_bases>=6 | total_bases>=5 | 162 | 1.0000 | 0.9768 | 19.1170 |
| hits_plus_runs_plus_RBI>=6 | total_bases>=6 | 293 | 0.4130 | 0.3581 | 17.4951 |
| total_bases>=6 | hits_plus_runs_plus_RBI>=6 | 162 | 0.7469 | 0.6748 | 17.4951 |
| hits_plus_runs_plus_RBI>=6 | RBI>=3 | 293 | 0.4983 | 0.4414 | 17.2717 |
| RBI>=3 | hits_plus_runs_plus_RBI>=6 | 198 | 0.7374 | 0.6720 | 17.2717 |
| RBI>=3 | total_bases>=6 | 198 | 0.3586 | 0.2951 | 15.1912 |
| total_bases>=6 | RBI>=3 | 162 | 0.4383 | 0.3642 | 15.1912 |
| hits>=3 | total_bases>=6 | 303 | 0.3102 | 0.2608 | 13.1427 |
| total_bases>=6 | hits>=3 | 162 | 0.5802 | 0.5033 | 13.1427 |

## Highest non-exact dependency ratios

| anchor | guard | n_anchor | P_guard_given_anchor | P_guard_given_anchor_ci_low | dependency_ratio |
| --- | --- | --- | --- | --- | --- |
| total_bases>=5 | total_bases>=6 | 359 | 0.4513 | 0.4006 | 19.1170 |
| hits_plus_runs_plus_RBI>=6 | total_bases>=6 | 293 | 0.4130 | 0.3581 | 17.4951 |
| total_bases>=6 | hits_plus_runs_plus_RBI>=6 | 162 | 0.7469 | 0.6748 | 17.4951 |
| hits_plus_runs_plus_RBI>=6 | RBI>=3 | 293 | 0.4983 | 0.4414 | 17.2717 |
| RBI>=3 | hits_plus_runs_plus_RBI>=6 | 198 | 0.7374 | 0.6720 | 17.2717 |
| RBI>=3 | total_bases>=6 | 198 | 0.3586 | 0.2951 | 15.1912 |
| total_bases>=6 | RBI>=3 | 162 | 0.4383 | 0.3642 | 15.1912 |
| hits>=3 | total_bases>=6 | 303 | 0.3102 | 0.2608 | 13.1427 |
| total_bases>=6 | hits>=3 | 162 | 0.5802 | 0.5033 | 13.1427 |
| total_bases>=5 | hits_plus_runs_plus_RBI>=6 | 359 | 0.5515 | 0.4998 | 12.9186 |

## Interpretation and next validation

This is exploratory outcome research, not evidence of an executable betting edge.
No Polymarket prices were joined and no out-of-sample predictive claims are made.
The configured rules and support policy were fixed before this run. Freeze candidates before
chronological holdout evaluation; use player/game-aware uncertainty, season stability checks,
and market-specific participation/settlement alignment before pricing comparisons.
Historical box scores may contain later official corrections; retrieval timestamps do not make
these records point-in-time data. Suspended-game completion and correction timestamps must be
resolved before historical price backtests. The backtest modules are intentionally not implemented.

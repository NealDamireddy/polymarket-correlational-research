# MLB dependency research — Milestone 1

## Dataset and cohort

Official MLB regular-season box scores, 2015-05-01 through 2015-05-31.
428 games; 10,456 player-game rows; 763 distinct players.
The analysis includes 8,936 player-games with at least one plate appearance.
1520 zero-PA rows are preserved in Parquet but excluded from this explicitly defined cohort.
5 schedule entries excluded; 1655 entries without batting lines.
See manifest.json for each exclusion and raw file hashes. Team totals reconciled for every processed game.
Missing values by column: {'batting_order': 1}.
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
| hits>=1 | total_bases>=1 | 5098 | 1.0000 | 0.9992 | 1.7528 |
| total_bases>=1 | hits>=1 | 5098 | 1.0000 | 0.9992 | 1.7528 |
| hits>=1 | hits_plus_runs_plus_RBI>=1 | 5098 | 1.0000 | 0.9992 | 1.6000 |
| total_bases>=1 | hits_plus_runs_plus_RBI>=1 | 5098 | 1.0000 | 0.9992 | 1.6000 |
| hits_plus_runs_plus_RBI>=2 | hits_plus_runs_plus_RBI>=1 | 3651 | 1.0000 | 0.9989 | 1.6000 |
| total_bases>=2 | hits>=1 | 2869 | 1.0000 | 0.9987 | 1.7528 |
| total_bases>=2 | total_bases>=1 | 2869 | 1.0000 | 0.9987 | 1.7528 |
| total_bases>=2 | hits_plus_runs_plus_RBI>=1 | 2869 | 1.0000 | 0.9987 | 1.6000 |
| runs>=1 | hits_plus_runs_plus_RBI>=1 | 2839 | 1.0000 | 0.9986 | 1.6000 |
| RBI>=1 | hits_plus_runs_plus_RBI>=1 | 2277 | 1.0000 | 0.9983 | 1.6000 |

## Highest-support empirical near-implications

| anchor | guard | n_anchor | P_guard_given_anchor | P_guard_given_anchor_ci_low | dependency_ratio |
| --- | --- | --- | --- | --- | --- |
| hits_plus_runs_plus_RBI>=3 | hits>=1 | 2229 | 0.9978 | 0.9948 | 1.7489 |
| hits_plus_runs_plus_RBI>=3 | total_bases>=1 | 2229 | 0.9978 | 0.9948 | 1.7489 |
| total_bases>=3 | hits_plus_runs_plus_RBI>=2 | 1572 | 0.9949 | 0.9900 | 2.4351 |
| hits_plus_runs_plus_RBI>=4 | hits>=1 | 1265 | 1.0000 | 0.9970 | 1.7528 |
| hits_plus_runs_plus_RBI>=4 | total_bases>=1 | 1265 | 1.0000 | 0.9970 | 1.7528 |
| total_bases>=4 | hits_plus_runs_plus_RBI>=2 | 1047 | 1.0000 | 0.9963 | 2.4475 |
| RBI>=2 | hits_plus_runs_plus_RBI>=3 | 732 | 0.9959 | 0.9880 | 3.9925 |
| RBI>=2 | total_bases>=1 | 732 | 0.9945 | 0.9860 | 1.7433 |
| RBI>=2 | hits>=1 | 732 | 0.9945 | 0.9860 | 1.7433 |
| hits_plus_runs_plus_RBI>=5 | total_bases>=1 | 707 | 1.0000 | 0.9946 | 1.7528 |

## Highest dependency ratios (including exact relationships)

| anchor | guard | n_anchor | P_guard_given_anchor | P_guard_given_anchor_ci_low | dependency_ratio |
| --- | --- | --- | --- | --- | --- |
| hits_plus_runs_plus_RBI>=6 | total_bases>=6 | 367 | 0.5341 | 0.4829 | 18.8631 |
| total_bases>=6 | hits_plus_runs_plus_RBI>=6 | 253 | 0.7747 | 0.7193 | 18.8631 |
| hits_plus_runs_plus_RBI>=6 | RBI>=3 | 367 | 0.4632 | 0.4128 | 18.0755 |
| RBI>=3 | hits_plus_runs_plus_RBI>=6 | 229 | 0.7424 | 0.6820 | 18.0755 |
| total_bases>=5 | total_bases>=6 | 515 | 0.4913 | 0.4483 | 17.3515 |
| total_bases>=6 | total_bases>=5 | 253 | 1.0000 | 0.9850 | 17.3515 |
| hits>=3 | total_bases>=6 | 403 | 0.3921 | 0.3456 | 13.8476 |
| total_bases>=6 | hits>=3 | 253 | 0.6245 | 0.5634 | 13.8476 |
| total_bases>=6 | RBI>=3 | 253 | 0.3399 | 0.2843 | 13.2643 |
| RBI>=3 | total_bases>=6 | 229 | 0.3755 | 0.3154 | 13.2643 |

## Highest non-exact dependency ratios

| anchor | guard | n_anchor | P_guard_given_anchor | P_guard_given_anchor_ci_low | dependency_ratio |
| --- | --- | --- | --- | --- | --- |
| hits_plus_runs_plus_RBI>=6 | total_bases>=6 | 367 | 0.5341 | 0.4829 | 18.8631 |
| total_bases>=6 | hits_plus_runs_plus_RBI>=6 | 253 | 0.7747 | 0.7193 | 18.8631 |
| hits_plus_runs_plus_RBI>=6 | RBI>=3 | 367 | 0.4632 | 0.4128 | 18.0755 |
| RBI>=3 | hits_plus_runs_plus_RBI>=6 | 229 | 0.7424 | 0.6820 | 18.0755 |
| total_bases>=5 | total_bases>=6 | 515 | 0.4913 | 0.4483 | 17.3515 |
| hits>=3 | total_bases>=6 | 403 | 0.3921 | 0.3456 | 13.8476 |
| total_bases>=6 | hits>=3 | 253 | 0.6245 | 0.5634 | 13.8476 |
| total_bases>=6 | RBI>=3 | 253 | 0.3399 | 0.2843 | 13.2643 |
| RBI>=3 | total_bases>=6 | 229 | 0.3755 | 0.3154 | 13.2643 |
| total_bases>=5 | hits_plus_runs_plus_RBI>=6 | 515 | 0.5437 | 0.5005 | 13.2382 |

## Interpretation and next validation

This is exploratory outcome research, not evidence of an executable betting edge.
No Polymarket prices were joined and no out-of-sample predictive claims are made.
The configured rules and support policy were fixed before this run. Freeze candidates before
chronological holdout evaluation; use player/game-aware uncertainty, season stability checks,
and market-specific participation/settlement alignment before pricing comparisons.
Historical box scores may contain later official corrections; retrieval timestamps do not make
these records point-in-time data. Suspended-game completion and correction timestamps must be
resolved before historical price backtests. The backtest modules are intentionally not implemented.

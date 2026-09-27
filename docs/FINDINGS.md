# Research findings and reproducibility record

Last updated: 2026-09-26. Covers Milestones 1 and 2 in this repository only.

This is the canonical narrative record of completed experiments. It consolidates the generated reports, records negative results and data corrections, and explains what a new researcher can and cannot conclude. Numeric claims below come from the linked local artifacts. API findings are a dated documentation review, not a fresh production eligibility test. Background claims about other projects in the README are outside this evidence base.

## 1. Current conclusion

The system can discover and mechanically validate exact same-player MLB prop implications and screen empirical guard combinations. April-selected combinations were evaluated on later May outcomes without replacing or reranking candidates using the holdout.

- April discovery: **327 games, 6,863 eligible player-games, 22 props, 462 directed pairs**.
- Pair proofs: **103 exact implications**, of which **84** pass the support requirements; zero observed proof violations.
- Combo discovery: **1,034 frozen structures**, each with one anchor and one to three guards.
- May evaluation: **428 games and 8,936 eligible player-games**.
- **656 exact structures** had zero observed violations. **356 of 378 empirical structures** passed the same conditional/support screen in May.
- The **22 screen failures are overlapping versions of one empirical relationship**, detailed in Section 6. They are not 22 independent discoveries or failure mechanisms.
- **No executable Polymarket price comparison, demonstrated betting edge, automated trading, or point-in-time backtest has been completed.**

The evidence supports correctness of the research pipeline and short-horizon descriptive stability. It does not establish multi-season generalization, a specific player's future probability, or profitability.

## 2. Research question and measurement units

For anchor event A and guards G1…Gk, compare the measured or proven probability of the entire guard conjunction conditional on A with an eventual market-implied conditional price. Each row is a single player's official full-game batting line; every leg in a structure refers to that same row. Counts pool different players and games.

Let N be cohort rows, nA anchor occurrences, nG rows satisfying every guard, and nAG rows satisfying the anchor and every guard:

| Measure | Definition | Interpretation |
| --- | --- | --- |
| Anchor probability | nA / N | P(A) |
| Guard probability | nG / N | P(all guards), not an individual leg in combo outputs |
| Joint probability | nAG / N | P(A and all guards) |
| Conditional probability | nAG / nA | P(all guards given A); undefined when nA = 0 |
| Reverse conditional | nAG / nG | P(A given all guards); undefined when nG = 0 |
| Dependency ratio | (nAG/N) / [(nA/N)(nG/N)] | Joint probability relative to marginal independence |
| Conditional lift | (nAG/nA) / (nG/N) | Algebraically identical to the dependency ratio |
| Leakage | (nA − nAG) / N | Additional failure mass across all player-games |
| Conditional failure | (nA − nAG) / nA | Failure frequency within anchor occurrences |

Undefined ratios remain missing; zero-support conditionals are not coerced to zero or one. Empirical probabilities remain separate from `P_rule_guards_given_anchor`, which is 1 only when a mechanical proof covers every guard.

## 3. Data sources, cohort, and quality

### Source choice

Primary ingestion uses MLB's public schedule and game box-score endpoints. Box scores already contain official batter-game totals, so the pipeline normalizes these records rather than reconstructing runs, RBI and steals from pitch-level Statcast data. Required counts include PA, AB, hit types, HR, runs, RBI, walks, strikeouts and steals. Singles, total bases and H+R+RBI are derived and checked.

An optional pybaseball/Statcast download module exists for pitch-level enrichment, but it was **not exercised** in these runs. Neither sample represents the complete 2015–present history.

### Collected data

| Measure | April 5–30, 2015 | May 1–31, 2015 |
| --- | ---: | ---: |
| Completed regular-season games | 327 | 428 |
| Normalized player-game rows | 8,079 | 10,456 |
| Distinct players in normalized data | 712 | 763 |
| Analysis rows, PA > 0 | 6,863 | 8,936 |
| Zero-PA rows preserved outside analysis | 1,216 | 1,520 |
| Excluded schedule entries | 7 | 5 |
| Entries without batting lines, logged separately | 1,280 | 1,655 |
| Missing required batting counts | 0 | 0 |
| Missing raw batting-order codes | 0 | 1 |
| Scoring-identity violations | 0 | 0 |

Excluded schedule entries are not necessarily distinct omitted games: duplicate schedule versions are included in those counts. Zero-PA rows can include roster entries and pinch runners and are not automatically evidence of missing observations. They remain in processed data. The PA > 0 cohort is a research choice, not a market participation/void policy.

Context includes player identity, official game date, season, team/opponent, home/away, park and raw batting-order/substitution code. Weather, wind and opposing-pitcher details are not collected. The one missing May order code does not affect the batting-count analysis.

For every processed game, player totals reconcile to team totals. Missing required fields, duplicate player-game keys, invalid counts, broken scoring identities, and empirical contradictions of an exact proof abort analysis. Download failures produce a failure record; inputs are cached separately from processed Parquet.

Evidence: [April validation](../outputs/2015-04-05_2015-04-30/validation.json), [April ingestion manifest](../outputs/2015-04-05_2015-04-30/manifest.json), [May validation](../outputs/2015-05-01_2015-05-31/validation.json), [May ingestion manifest](../outputs/2015-05-01_2015-05-31/manifest.json).

## 4. Milestone 1: propositions, rules, and pair findings

### Proposition grid and screening policy

The 22 binary props are HR >= 1–2; hits >= 1–3; TB >= 1–6; H+R+RBI >= 1–6; runs >= 1–2; RBI >= 1–3. All directed non-self pairs are computed, giving 22 × 21 = 462 comparisons.

Both anchor and guard require at least 100 occurrences to enter the supported ranking. A configured rule proves `EXACT_IMPLICATION` independently of empirical counts, but small-support proofs are excluded from that ranking. `EMPIRICAL_NEAR_IMPLICATION` requires a conditional rate >= 0.99 and nominal Wilson lower bound >= 0.95. `STRONG_DEPENDENCE` requires lift >= 1.5 and a conditional lower bound above the guard marginal upper bound, plus support. Everything else is `WEAK_OR_NONE`; this last label does not prove independence, particularly for unsupported pairs.

| Classification | All pairs | Supported pairs |
| --- | ---: | ---: |
| Exact implication | 103 | 84 |
| Empirical near-implication | 22 | 22 |
| Strong dependence | 314 | 314 |
| Weak or none under this screen | 23 | 0 |
| Total | 462 | 420 |

Ranking uses category, conditional lower bound, lift and anchor support with deterministic ties. Wilson bounds discourage ranking tiny empirical samples as certain. These screens are not significance tests.

### Mechanical rules and representative exact results

The engine propagates lower bounds from explicit scoring definitions, same-stat threshold monotonicity and the H+R+RBI sum. It also uses hits >= ceil(TB / 4), because a hit contributes no more than four total bases. No LLM decides implications at runtime. It is a sound, deliberately incomplete collection of rules: absence of a proof does not prove nonlogical dependence.

| Anchor | Guard | Anchor occurrences | Joint successes | Conditional rate | Wilson 95% lower bound | Lift |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `home_runs>=1` | `hits>=1` | 564 | 564 | 100.0000% | 99.3235% | 1.7971 |
| `home_runs>=1` | `total_bases>=4` | 564 | 564 | 100.0000% | 99.3235% | 8.6764 |
| `home_runs>=1` | `runs>=1` | 564 | 564 | 100.0000% | 99.3235% | 3.0475 |
| `home_runs>=1` | `RBI>=1` | 564 | 564 | 100.0000% | 99.3235% | 3.8600 |
| `home_runs>=1` | `hits_plus_runs_plus_RBI>=3` | 564 | 564 | 100.0000% | 99.3235% | 3.8774 |
| `hits>=2` | `total_bases>=2` | 1,371 | 1,371 | 100.0000% | 99.7206% | 3.1467 |
| `total_bases>=5` | `hits>=2` | 359 | 359 | 100.0000% | 98.9413% | 5.0058 |

These empirical lower bounds quantify observed support, not uncertainty in the mathematical implication itself. Application to contracts still requires matching player, game scope, credited statistics and settlement/void rules.

### Representative empirical findings

H+R+RBI is written as `hits_plus_runs_plus_RBI` in the data. The following relationships have no proof under the configured rules:

| Anchor | Guard | Anchor occurrences | Joint successes | Conditional rate | Wilson 95% lower bound | Lift |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `hits_plus_runs_plus_RBI>=3` | `hits>=1` | 1,770 | 1,765 | 99.7175% | 99.3404% | 1.7920 |
| `hits_plus_runs_plus_RBI>=4` | `hits>=1` | 1,017 | 1,017 | 100.0000% | 99.6237% | 1.7971 |
| `total_bases>=3` | `hits_plus_runs_plus_RBI>=2` | 1,215 | 1,205 | 99.1770% | 98.4916% | 2.4422 |
| `total_bases>=4` | `hits_plus_runs_plus_RBI>=3` | 791 | 788 | 99.6207% | 98.8909% | 3.8627 |
| `RBI>=2` | `hits_plus_runs_plus_RBI>=3` | 593 | 590 | 99.4941% | 98.5233% | 3.8578 |

For example, H+R+RBI >= 4 implied at least one hit in all 1,017 April anchor observations and all 1,265 May anchor observations. It remains empirical: runs and RBI can be accumulated without a hit. A 100% observed rate does not upgrade the classification to exact.

### Why lift alone is misleading

`total_bases>=5 → total_bases>=6` has approximately 19.12× lift in April but only about 45.13% conditional success (162 of 359 anchor occurrences). The reverse direction is a threshold proof. Large lift is compatible with substantial guard risk and is not a substitute for a high conditional probability.

Evidence: [all pair metrics and proofs](../outputs/2015-04-05_2015-04-30/all_pairs.csv), [supported ranking](../outputs/2015-04-05_2015-04-30/ranked_pairs.csv), [generated April report](../outputs/2015-04-05_2015-04-30/research_report.md).

## 5. Milestone 2: bounded discovery and frozen validation

April is the discovery sample. The candidate bundle was written before May outcomes were downloaded for this experiment. This is a reproducible freeze, not a public or tamper-proof preregistration. April itself had already been explored in Milestone 1; discovery estimates are not out-of-sample results.

Discovery first screens supported pairs at conditional >= 0.99 and Wilson lower bound >= 0.95. Per anchor, it retains at most ten guards, prioritizing exact proofs, conditional lower bounds and support. It enumerates one to three guards, counts their conjunction directly, and requires the same conditional screen and at least 100 joint-guard occurrences. The 5,000-evaluation budget is a hard error boundary, not silent truncation.

- 106 pair candidates passed the initial screen.
- One guard was removed by the cap: `hits_plus_runs_plus_RBI>=4` for anchor `total_bases>=6`.
- 1,034 proposed structures were evaluated, and all 1,034 passed the joint screen in this run.
- No structures were rejected by the joint screen here; tests separately verify that individually eligible guards can fail it in combination.
- 934 structures had zero observed April leakage; the maximum retained training leakage was approximately 0.1457% of all April cohort rows.

| Guard count | Total legs | Mechanically exact | Partly empirical | Total |
| --- | ---: | ---: | ---: | ---: |
| 1 | 2 | 84 | 21 | 105 |
| 2 | 3 | 204 | 107 | 311 |
| 3 | 4 | 368 | 250 | 618 |
| Total | — | 656 | 378 | 1,034 |

The frozen bundle records structured legs, training metrics, game IDs, date range, input/code hashes, configuration and pruning audit. Evaluation verifies the checksum and proof-semantics hashes, rejects shared game IDs and non-later test dates, and retains every candidate in training order. It never substitutes new candidates based on test outcomes.

Frozen payload SHA-256:

```text
cc32e52b2a8aeb1959655622c5dd2a2bd8a0d387c3ffa2be201c057019c07485
```

Evidence: [frozen candidate bundle](../outputs/combo_april2015_frozen/frozen_candidates.json), [training combo metrics](../outputs/combo_april2015_frozen/train_combos.csv), [protocol](milestone2.md).

## 6. May holdout results, including failures

| Measure | Result |
| --- | ---: |
| Frozen structures evaluated | 1,034 |
| Meeting May support thresholds | 1,034 |
| Passing original conditional screen in May | 1,012 |
| Mechanically exact structures, zero observed violations | 656 |
| Empirical structures passing screen | 356 of 378 |
| Empirical structures failing screen | 22 of 378 |
| Empirical structures with at least one guard failure | 212 of 378 |
| Structures with zero observed May leakage | 822 |
| Largest observed May leakage | 0.1343% of cohort rows |

A structure can have failures and still pass a 99% conditional screen. Therefore “passed” does not mean “risk-free.” Conversely, small unconditional leakage can coexist with a conditional failure rate above the screen.

### All 22 screen failures share one underlying condition

Each failed structure uses anchor `total_bases>=4` and includes guard `hits_plus_runs_plus_RBI>=3`. Other guards in those structures are already implied by the anchor or the HRR guard. Thus they reduce to the same sporting condition for this analysis, even though their leg lists differ.

| Measure for TB >= 4 → H+R+RBI >= 3 | April discovery | May holdout |
| --- | ---: | ---: |
| Anchor occurrences | 791 | 1,047 |
| Anchor-and-guard successes | 788 | 1,035 |
| Guard failures within anchor | 3 | 12 |
| Conditional success | 99.6207% | 98.8539% |
| Conditional failure | 0.3793% | 1.1461% |
| Leakage across all player-games | 0.0437% | 0.1343% |

The May conditional rate is below 99%, so these 22 structures fail the original screen. The 12 May failing player-games are shared across the structures; summing their failure counts would repeatedly count the same sporting outcomes. This illustrates both empirical instability and the need to collapse logical equivalences before interpreting discovery counts.

This relationship is not a scoring guarantee: two doubles with no runs or RBI give four total bases but only two H+R+RBI. This is a logical counterexample, not a claim that all 12 observed failures had that precise batting line.

Evidence: [complete holdout CSV](../outputs/combo_may2015_holdout/holdout_combos.csv), [generated holdout report](../outputs/combo_may2015_holdout/research_report.md), [holdout manifest](../outputs/combo_may2015_holdout/manifest.json).

## 7. Uncertainty and interpretation limits

1. **Marginal intervals:** probabilities and leakage have nominal 95% Wilson intervals using their own denominators. Pairwise probabilities assume IID Bernoulli observations for this approximation. Lift/ratio uncertainty is not estimated by a dedicated interval.
2. **Cluster sensitivity:** May outputs add 1,000 bootstrap resamples of whole games and, separately, whole players, using seed 1729. All candidates share each set of resampled clusters. These are separate one-way checks, not a simultaneous two-way dependence adjustment.
3. **Perfect empirical samples:** percentile bootstrap intervals can collapse to [1, 1] because the sample contains no failures to resample. Keep the Wilson interval and never treat bootstrap perfection as a proof.
4. **Zero-support resamples:** anchor-free bootstrap replicates are omitted from conditional quantiles and counted in the output. All-zero anchor support produces an undefined empirical conditional. All real May candidates had positive support, but the implementation tests zero-support cases.
5. **Selection and multiplicity:** neither Wilson nor bootstrap outputs provide a simultaneous post-selection guarantee across the many related candidates. Nominal intervals and passing thresholds do not establish statistical significance or profitability.
6. **Pooled populations:** players repeat and may appear in both periods. Population mix and opportunities to bat affect the estimates. This is later-game validation, not unseen-player validation or a named-player forecast.
7. **Time availability:** split dates are official game dates; records are final and may have later corrections. A separate cached-schedule audit found no April training game with a recorded resumption date beyond April 30. That check does not reconstruct all historical outcome-availability or correction timestamps.
8. **Coverage:** only two adjacent months from 2015 were analyzed. No complete-season, multi-season or contemporary-market conclusion is established.

## 8. Implementation findings and corrections

| Finding | Correction / impact | Evidence |
| --- | --- | --- |
| Early rules omitted TB-to-minimum-hits inference | Added ceil(TB/4) bound before final Milestone 1 outputs; mechanically provable relationships no longer appear as merely empirical for that reason. | [rules](../src/sports_dependency_engine/sports/mlb/rules.py), [proof tests](../tests/test_implications.py) |
| Floating-point Wilson endpoint was slightly above zero for zero successes | Explicitly return boundary 0 or 1 where appropriate. | [metrics](../src/sports_dependency_engine/dependency/metrics.py), [metric tests](../tests/test_metrics.py) |
| A postponed schedule version could hide the completed makeup game with the same ID | Collect versions and choose an eligible completed game before deduplication; keep other versions in exclusion records. May increased from 426 to 428 games and 8,897 to 8,936 eligible rows before combo evaluation. | [ingestion](../src/sports_dependency_engine/sports/mlb/ingestion.py), [regression tests](../tests/test_ingestion.py) |
| Redundant guard combinations inflate structure counts | Document overlap explicitly. Automatic canonical grouping of equivalent sporting events is still future work. | Section 6 and full holdout CSV |

The schedule correction recovered games 414038 and 414083. The corrected schedule preserves the 327 April training game IDs. May's corrected dataset, rather than the preliminary incomplete build, is the holdout input recorded in its manifest.

Completed verification at Milestone 2: **52 tests passed**. Tests include independent feasible-scoring-state checks of configured proofs, known contingency/joint counts, data validation, guard caps and work budget, frozen list integrity, proof-semantic drift, chronology/game overlap, zero support, candidate retention after failures, and seeded reproducibility. Full April CSV replay and full May combo/bootstrap replay were byte-identical in the tested environment. Changed notebook code cells were executed against the actual outputs. No new test claim is implied for future code changes.

## 9. Polymarket findings and remaining gap

The [API investigation](polymarket_api.md) records the documentation reviewed on **2026-09-21**. It describes public sports/market metadata, order books, and the combo-eligible leg catalog, and an authenticated workflow for executable combo RFQs. This document does not assert that those endpoints or policies were retested on its update date.

No specific same-player combination's acceptance, available price, depth, fee or expiry has been verified. The public eligible-leg catalog is not a price feed for all possible combos. The implemented adapters are GET-only and use a reproducible cache; cached order books must not be treated as fresh executable quotes. Player/threshold matching and settlement interpretation remain unresolved for actual contracts.

The existing investigation concerns the documented `polymarket.com` Gamma/CLOB/RFQ interfaces. It does **not** establish feature parity or eligibility on Polymarket US or any other venue variant. Venue-specific checks are required before transferring findings.

An eventual `q_combo / q_anchor` comparison needs synchronized executable cost per payout share, trade size, fees, spreads, expiry and identical settlement. Values outside [0, 1] should be investigated, not clipped. No price discrepancy or positive expected return has been measured here.

## 10. Reproduce and inspect the work

Run from the repository root with Python 3.11+:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q

# Build April first. Omit --offline on a fresh checkout to populate the cache.
python main.py --start 2015-04-05 --end 2015-04-30

# Use new output directories: freeze/evaluate deliberately refuse overwrites.
python -m sports_dependency_engine.backtest.historical freeze \
  --train data/processed/2015-04-05_2015-04-30/player_games.parquet \
  --output outputs/reproduction_april_frozen

python main.py --start 2015-05-01 --end 2015-05-31

python -m sports_dependency_engine.backtest.historical evaluate \
  --frozen outputs/reproduction_april_frozen/frozen_candidates.json \
  --test data/processed/2015-05-01_2015-05-31/player_games.parquet \
  --output outputs/reproduction_may_holdout \
  --bootstrap-replicates 1000 --seed 1729
```

Add `--offline` to the ingestion commands for cached replay. Raw JSON and processed Parquet are local and git-ignored, so a fresh checkout needs downloads. New upstream revisions can change a fresh build; matching cached input hashes are necessary to reproduce the original sample exactly. A regenerated frozen bundle includes a new timestamp and may have a different checksum even when its candidates agree. Changes to recorded proof/prop semantics cause evaluation of the old bundle to fail intentionally; preserve its source version instead of bypassing the check.

Input and source hashes, policy and retrieval/build timestamps are in the manifests. The tested dependency versions are in the [lockfile](../requirements-lock.txt). The portable install requirements are in [pyproject.toml](../pyproject.toml). Source changes made after a freeze can legitimately appear in the evaluation manifest; they do not rewrite the original training provenance. Cached-data reproducibility does not imply historical point-in-time correctness.

### Reading the output columns

| Columns | Meaning |
| --- | --- |
| `candidate_id`, `anchor`, `guards`, `n_guards` | Stable structured-leg identity and readable definition |
| `type`, `proofs`, `n_guards_proven_from_anchor` | Exact versus partly empirical status and rule evidence |
| `train_*`, `test_*` | Metrics for discovery and holdout separately |
| `*_n`, `*_n_anchor`, `*_n_guard`, `*_n_joint` | Total, anchor, conjunction and intersection counts |
| `*_n_violations` | Anchor occurrences where one or more guards failed |
| `*_P_guard_given_anchor`, `*_ci_low`, `*_ci_high` | Conditional estimate and marginal Wilson bounds |
| `*_leakage`, `*_conditional_failure` | Unconditional versus anchor-conditional risk added by guards |
| `test_support_sufficient`, `test_screen_pass` | Descriptive validation flags, never holdout reselection |
| `test_game_id_*`, `test_player_id_*` | Separate bootstrap sensitivity intervals and valid replicate counts |
| `conditional_change`, `leakage_change` | Holdout minus training values |

[Notebook 04](../notebooks/04_combo_search.ipynb) reads the frozen search; [Notebook 06](../notebooks/06_chronological_validation.ipynb) reads the holdout. They consume library outputs and contain no alternative research implementation.

## 11. Open questions and next experiments

- Collapse or label logically equivalent sporting events before summarizing independent research hypotheses; retain contract leg lists separately for eventual pricing.
- Extend a prespecified frozen protocol to full seasons and untouched later periods; report failures without retuning on the same holdout.
- Measure player, season and exposure sensitivity and improve joint clustering/selection-aware uncertainty where needed.
- Attach outcome completion/availability and correction timestamps before historical price comparisons.
- Verify actual venue, player identity, game scope, thresholds, participation, voids and combo acceptance.
- Capture and compare genuinely executable prices and all costs before claiming an edge.

## 12. Documentation maintenance protocol

For each future experiment, append a dated entry to this file and update the result tables. Record the hypothesis, fixed configuration, input/source hashes, selection versus evaluation periods, all material successes and failures, exclusions, uncertainty limitations, corrections, test/replay status, artifact links, and unresolved questions. Preserve prior frozen artifacts; distinguish corrected results from superseded preliminary counts. Do not promote a correlation finding to a pricing or profitability claim without the missing evidence.

| Record | Completed scope | Durable evidence |
| --- | --- | --- |
| Milestone 1, 2026-09-21 session | Official data normalization, pair search, proofs, April validation | April outputs and original manifest timestamps |
| Milestone 2, 2026-09-26 | Frozen combo discovery, corrected May ingestion, chronological evaluation, cluster sensitivity | Frozen bundle and May holdout manifest |
| Findings consolidation, 2026-09-26 | Unified documentation, failure-family interpretation, reproducibility instructions | This document; underlying frozen results unchanged |

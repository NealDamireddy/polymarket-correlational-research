# Polymarket Correlational Research

**Start with [Research findings and reproducibility record](docs/FINDINGS.md)** for the consolidated methods, verified results, failures, data corrections, limitations, and reproduction commands. It is the ongoing findings record for this repository.

An auditable research project investigating whether structural dependence between sports props can create a pricing edge in Polymarket combo markets.

> **Bottom line:** the statistical and logical dependency search is feasible, reproducible, and produced meaningful candidates. This milestone did **not** establish an executable betting edge. No historical combo quotes were joined, no out-of-sample pricing backtest was run, and no orders were submitted.

## Why I investigated this

This project grew out of a practical question about boosted sports combos and hedging.

The original idea was to combine several apparently very safe legs with one uncertain leg, use the combo boost to improve the payout, and hedge the uncertain leg by buying its opposite outcome separately. The appeal was intuitive: the heavy favorites appeared close to guaranteed, while the hedge seemed to cover the remaining uncertainty.

The first mathematical review exposed two important problems:

1. **Several “safe” legs are not collectively safe.** Three legs with individual win probabilities of 99%, 98%, and 98% survive together only about 95.08% of the time if treated as independent. A hedge on the uncertain game does not protect against one of those legs failing.
2. **A hedge does not create expected value.** It only redistributes outcomes. The combo must already be mispriced enough to overcome the added failure probability, fees, spread, and execution risk. Buying an overpriced opposite side can hedge away an otherwise positive edge.

That led to two complementary research directions:

- The separate **Polymarket Model** project studies late-game winner markets: safe-lead rules, market flow, game state, execution, and whether displayed 98–99¢ contracts are actually underpriced.
- This repository studies **dependency between prop outcomes**: whether one leg logically or empirically makes another leg much more likely, and whether a combo venue might price that dependence incorrectly.

The central hypothesis here is not simply “correlated props win more often.” It is:

> If two accepted combo legs are more dependent than the quoted combo price reflects—and that difference survives fees, spread, size, settlement rules, and adverse execution—then the discrepancy may be exploitable.

## What this project tests

The first milestone focuses on same-player, full-game MLB batting props. Each observation is one player-game, and each prop is a structured threshold such as:

- `home_runs >= 1`
- `hits >= 2`
- `total_bases >= 4`
- `runs >= 1`
- `RBI >= 2`
- `hits + runs + RBI >= 3`

The project evaluates 22 prop definitions and all 462 directed anchor/guard pairs. For a pair \(A \rightarrow B\), it records the marginal probabilities, joint probability, both conditional probabilities, support, violations, lift, and Wilson confidence intervals.

The primary question is:

\[
P(B \mid A) \quad \text{versus} \quad P(B)
\]

If the guard becomes substantially more likely when the anchor occurs, the pair is dependent. But dependence alone is not an edge: a market may already price it correctly, reject redundant legs, or offer too little executable size.

## Research approach

### 1. Build a trustworthy player-game dataset

The pipeline uses official MLB Stats API schedules and box scores rather than attempting to reconstruct credited batting totals from pitch data. This matters because runs, RBI, stolen bases, substitutions, and official scoring are not always safely inferred from pitch-level records alone.

The ingestion layer:

- caches raw responses for reproducibility;
- restricts the cohort to completed regular-season games;
- distinguishes doubleheaders by game ID;
- preserves zero-plate-appearance rows but excludes them from the analysis cohort;
- treats missing required counts as errors rather than zeros;
- rejects duplicate keys, negative or fractional counts, broken scoring identities, and failed team-total reconciliation;
- records every excluded game/player and hashes raw inputs in a manifest.

The completed validation window covers April 5–30, 2015:

| Measure | Result |
| --- | ---: |
| Completed regular-season games | 327 |
| Normalized player-game rows | 8,079 |
| Distinct players | 712 |
| Analysis rows with PA > 0 | 6,863 |
| Zero-PA rows preserved but excluded | 1,216 |
| Missing collected values | 0 |
| Scoring-identity violations | 0 |

This is a deliberately bounded validation sample, not the full 2015–present history.

### 2. Separate logical implications from empirical correlations

This distinction is essential.

Some relationships are true by baseball scoring rules, independent of a historical sample. For example:

- a home run implies at least one hit;
- a home run implies at least four total bases;
- two hits imply at least two total bases;
- any positive hit, run, or RBI contributes to `hits + runs + RBI`;
- a higher threshold implies every lower threshold for the same statistic.

The project includes a deterministic rule engine that proves conservative lower-bound implications using threshold monotonicity, official stat relationships, and sum rules. It does not use an LLM at runtime. A proof that conflicts with observed data causes the analysis to fail.

Other relationships are only empirical. They may look nearly deterministic in one sample but fail later. These are labeled separately and require support and uncertainty thresholds.

### 3. Screen every directed pair conservatively

For each pair, the engine reports:

- \(P(A)\) and \(P(B)\);
- \(P(A \cap B)\);
- \(P(B \mid A)\) and \(P(A \mid B)\);
- support and violation counts;
- dependency ratio / conditional lift;
- nominal 95% Wilson intervals for each probability;
- whether the implication is mechanically proven;
- whether the pair passes the prespecified support policy.

The milestone policy requires at least 100 anchor occurrences and 100 guard occurrences. An empirical near-implication requires:

- \(P(B \mid A) \ge 0.99\); and
- a Wilson lower bound of at least 0.95.

These are exploratory screening criteria, not significance tests. The pooled rows are not independent: players repeat, games contain multiple players, and the search examines many pairs.

### 4. Investigate the market bridge without trading

The Polymarket adapters are intentionally read-only. They support market discovery, public order-book retrieval, combo-catalog inspection, pagination, and explicit outcome-label mapping.

The API review found that:

- public market metadata is not the same thing as an executable quote;
- combo catalogs show eligible component markets, not every possible combination or its price;
- executable combo RFQs require an authenticated workflow;
- same-player or logically redundant legs are not guaranteed to be accepted;
- position IDs, outcome token IDs, player identity, thresholds, and settlement wording must be aligned explicitly.

For a future comparison, \(q_{combo}/q_{anchor}\) can be used as a diagnostic implied conditional price. It is not automatically a coherent probability because fees, spreads, size, quote expiry, and settlement differences matter.

### 5. Freeze multi-guard candidates without multiplying pairwise rates

The current code also extends the pair search to combinations of one anchor and as many as three guards. Each guard conjunction is evaluated directly on the same player-game rows. The implementation never multiplies pairwise conditional probabilities as if the guards were independent.

Candidate discovery is bounded by explicit support, conditional-probability, guard-count, per-anchor, and total-evaluation limits. The selected list is then serialized with a checksum, the training date range, game IDs, input hashes, source hashes, configuration, and training statistics. A separate holdout command refuses overlapping or non-later dates and evaluates every frozen candidate without choosing replacements from the test period.

## Findings

### Proven structure exists

Across the 22-prop grid, the engine found:

- **103 mechanically proven directed implications**;
- **84 proven implications** meeting both support thresholds;
- **zero observed violations** of those proofs;
- **462 total directed pairs**, of which 420 met both support thresholds.

Representative exact relationships include:

| Anchor | Guard | Anchor support | Observed conditional | 95% lower bound | Lift |
| --- | --- | ---: | ---: | ---: | ---: |
| `hits >= 1` | `total_bases >= 1` | 3,819 | 100.00% | 99.90% | 1.80× |
| `hits >= 1` | `H+R+RBI >= 1` | 3,819 | 100.00% | 99.90% | 1.61× |
| `total_bases >= 2` | `hits >= 1` | 2,181 | 100.00% | 99.82% | 1.80× |
| `RBI >= 1` | `H+R+RBI >= 1` | 1,778 | 100.00% | 99.78% | 1.61× |
| `home_runs >= 1` | `total_bases >= 4` | 564 | 100.00% | 99.32% | 8.68× |

These are useful sanity checks and potential pricing probes, but a logically redundant pair may be rejected by the platform or deliberately repriced.

### Strong empirical dependence also exists

Several relationships were not proven by the configured rules but were extremely reliable in the sample:

| Anchor | Guard | Anchor support | Observed conditional | 95% lower bound | Lift |
| --- | --- | ---: | ---: | ---: | ---: |
| `H+R+RBI >= 3` | `hits >= 1` | 1,770 | 99.72% | 99.34% | 1.79× |
| `total_bases >= 3` | `H+R+RBI >= 2` | 1,215 | 99.18% | 98.49% | 2.44× |
| `H+R+RBI >= 4` | `hits >= 1` | 1,017 | 100.00% | 99.62% | 1.80× |
| `total_bases >= 4` | `H+R+RBI >= 2` | 791 | 100.00% | 99.52% | 2.46× |
| `RBI >= 2` | `H+R+RBI >= 3` | 593 | 99.49% | 98.52% | 3.86× |

These candidates are more interesting for future validation because they are not merely identical thresholds in disguise. They are also more dangerous to overinterpret: pooled historical association is not a guarantee, and the candidate list was selected from the same data used to estimate it.

### The frozen multi-guard set was tested on the next month

The bounded April 2015 search evaluated and retained 1,034 one-to-three-guard structures under the prespecified screen:

| Candidate class | Count |
| --- | ---: |
| Every guard mechanically implied by the anchor | 656 |
| At least partly empirical | 378 |
| One guard | 105 |
| Two guards | 311 |
| Three guards | 618 |
| Zero observed sporting leakage in training | 934 |

The maximum training leakage among retained structures was about 0.146% of all player-game rows. The frozen list was then evaluated without reselection on May 1–31, 2015: 428 games and 8,936 positive-PA player-games.

- All 1,034 structures met the holdout support thresholds.
- 1,012 of 1,034 met the original joint-conditional screen in holdout.
- 356 of 378 partly empirical structures passed the holdout screen.
- 212 empirical structures had at least one holdout guard failure when the anchor occurred.
- All 656 mechanically exact structures remained exact under the matching data/scoring scope.

All 22 screen failures are overlapping leg-list variants of one underlying empirical condition: `total_bases >= 4 → H+R+RBI >= 3`. It recorded 788/791 successes in April (99.62%) and 1,035/1,047 in May (98.85%), falling below the original 99% screen. The 12 May failures are shared across those structures and must not be counted 22 times.

This is encouraging short-horizon stability alongside a concrete example of empirical deterioration—not evidence of a priced edge. April and May are adjacent retrospective months, repeated players can appear in both, official statistics may have been revised later, and the counts contain many logically equivalent leg lists. Two months do not establish multi-season or point-in-time performance.

### Large lift is not the same as a safe leg

The highest dependency ratios often involve rare, high thresholds. For example, `total_bases >= 5` and `total_bases >= 6` have a lift above 19×, but only about 45% of five-total-base games reach six total bases. High lift says the guard becomes much more likely relative to its low baseline; it does not say the conditional probability is high enough for a near-certain combo leg.

This is why the ranking emphasizes conditional lower bounds and support, not lift alone.

## Is the strategy feasible?

### Feasible as a research program: yes

The project demonstrates that it is possible to:

- build a validated player-game dataset from official records;
- express props as machine-checkable objects rather than text guesses;
- prove exact relationships mechanically;
- search empirical dependencies with explicit support and uncertainty;
- preserve a reproducible audit trail;
- connect candidate relationships to public market and combo metadata.

### Established as an executable edge: no

This milestone does not answer the decisive trading question because it has not yet observed the price actually offered for an accepted correlated combo at a tradable size.

An executable edge would require all of the following:

1. Both contracts refer to the same player, game, scope, participation policy, and official-stat settlement.
2. The venue accepts the exact pair or multi-leg combination.
3. A synchronized executable combo quote and component quote are captured with size and expiry.
4. The conditional outcome rate holds in a frozen chronological test set.
5. The advantage remains after fees, spread, slippage, partial fills, voids, latency, and adverse selection.
6. Multi-leg analysis uses direct joint counts; pairwise conditionals are not multiplied as though guards were independent.

Until those conditions are met, the correct conclusion is **promising dependency structure, unproven market edge**.

## How this fits with the broader Polymarket research

The companion Polymarket Model project reached the same broad lesson from a different direction:

- perfect-looking historical late-game cohorts were still too small to prove profitability above a 99¢ all-in cost;
- MLB did not validate cleanly in the later sample, and one NHL loss nearly erased modeled gains;
- a one-cent adverse price move could eliminate the apparent advantage;
- actual signed market flow did not improve predictive log loss over market price alone in the completed comparison;
- added foul/timeout and lineup proxy models did not outperform the score/time baseline in the structural feasibility test;
- combo-plus-hedge constructions still fail when a supposedly safe leg loses.

Together, the projects suggest that the main challenge is not finding correlation. Correlation is abundant. The hard part is identifying a relationship the market both permits and misprices by more than the complete cost of execution, then showing that result survives a truly forward test.

## Reproduce the completed run

Python 3.11 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python main.py --start 2015-04-05 --end 2015-04-30 --offline
pytest -q
```

The online form downloads and caches official MLB responses:

```bash
python main.py --start 2015-04-05 --end 2015-04-30
```

The installed CLI is equivalent:

```bash
sports-dependency --start 2015-04-05 --end 2015-04-30
```

Use `--root PATH` to change the data/output root. `--min-anchor` and `--min-guard` override the default support thresholds. Large multi-season runs make thousands of cached requests and accumulate player-game rows in memory.

## Repository map

```text
src/sports_dependency_engine/
├── sports/mlb/       # ingestion, normalization, prop definitions, scoring rules
├── dependency/       # proofs, pair/combo search, metrics
├── polymarket/       # read-only catalogs, books, prices, response parsing
├── reports/          # validation, ranking, and research reports
└── backtest/         # frozen chronological validation and cluster sensitivity

notebooks/            # output-consuming walkthroughs; no unique research logic
outputs/              # committed validation report, rankings, and manifests
docs/                 # Polymarket API investigation
tests/                # ingestion, proof, metric, and market-parser tests
data/                 # ignored raw/processed datasets; only .gitkeep is committed
```

Key artifacts:

- [`research_report.md`](outputs/2015-04-05_2015-04-30/research_report.md) — generated results and limitations.
- [`ranked_pairs.csv`](outputs/2015-04-05_2015-04-30/ranked_pairs.csv) — support-gated candidate ranking.
- [`all_pairs.csv`](outputs/2015-04-05_2015-04-30/all_pairs.csv) — every directed pair and proof result.
- [`validation.json`](outputs/2015-04-05_2015-04-30/validation.json) — counts, missingness, and identity checks.
- [`manifest.json`](outputs/2015-04-05_2015-04-30/manifest.json) — policy, exclusions, source hashes, retrieval times, and runtime versions.
- [`frozen_candidates.json`](outputs/combo_april2015_frozen/frozen_candidates.json) — checksummed one-to-three-guard discovery set and training provenance.
- [`train_combos.csv`](outputs/combo_april2015_frozen/train_combos.csv) — direct conjunction metrics for all 1,034 frozen structures.
- [`Milestone 2 report`](outputs/combo_may2015_holdout/research_report.md) — April-frozen candidates evaluated on the May chronological holdout.
- [`holdout_combos.csv`](outputs/combo_may2015_holdout/holdout_combos.csv) — every frozen candidate, including failures, in original training order.
- [`milestone2.md`](docs/milestone2.md) — selection, integrity, uncertainty, and timing protocol.
- [`polymarket_api.md`](docs/polymarket_api.md) — combo and pricing API boundaries.

Raw and processed datasets remain local and are excluded from Git because they are large and reproducible from the cached-source workflow. The committed lockfile records the tested environment; `pyproject.toml` remains the portable dependency specification.

## Next experiments

The next phase should be prespecified before expanding the sample:

1. Extend the frozen protocol across complete seasons and untouched later-season holdouts.
2. Measure season, player, and threshold stability with player/game-aware uncertainty.
3. Collapse or label logically equivalent leg structures before interpreting candidate counts.
4. Verify actual Polymarket US contract wording and same-player combo eligibility.
5. Capture synchronized executable RFQs/books, quote expiry, size, and fees.
6. Attach outcome-availability timestamps before any historical price backtest.
7. Replay every outcome branch, including anchor failure, guard failure, voids, and partial fills.
8. Stress every candidate by at least one tick before considering paper execution.

## Scope and disclaimer

This repository is research software, not a trading system or a recommendation to bet. It contains no credentials, order-submission logic, or claimed profitable strategy. Historical box scores can contain later official corrections, and the marginal Wilson intervals do not adjust for clustering, repeated searches, or selection. Separate one-way game/player bootstrap sensitivity intervals are included for the May holdout; they do not provide a simultaneous multiway or post-selection guarantee. “No configured proof” also does not mean a relationship is nonlogical; the rule engine is intentionally conservative and incomplete.


## Milestone 2: freeze first, evaluate later

Use separate commands so candidate selection is complete before fetching or examining holdout outcomes:

```bash
python -m sports_dependency_engine.backtest.historical freeze \
  --train data/processed/2015-04-05_2015-04-30/player_games.parquet \
  --output outputs/my_april_frozen

python main.py --start 2015-05-01 --end 2015-05-31

python -m sports_dependency_engine.backtest.historical evaluate \
  --frozen outputs/my_april_frozen/frozen_candidates.json \
  --test data/processed/2015-05-01_2015-05-31/player_games.parquet \
  --output outputs/my_may_holdout
```

Output directories must be new; existing frozen selections/results cannot be overwritten by these commands. The completed run is in `outputs/combo_april2015_frozen/` and `outputs/combo_may2015_holdout/`. The JSON bundle records training input hashes, code hashes, configuration, candidates, training metrics and pruning audit. Evaluation verifies bundle integrity, proof-semantics hashes, disjoint game IDs and strictly later dates. This is reproducibility metadata, not a tamper-proof public preregistration.

Default discovery requires at least 100 anchor and 100 guard occurrences, pair conditional >= .99 and Wilson lower bound >= .95. Each anchor retains at most ten eligible guards, prioritizing proofs, lower bounds and support. Enumerate one to three guards and apply the same thresholds to the **joint** guard outcome, including joint guard support. A hard 5,000-evaluation budget raises an error rather than returning a truncated search. Caps are configurable and exclusions are logged. No tiny-support exact rules enter this candidate ranking.

All frozen candidates appear in `holdout_combos.csv`, in training order: failures, insufficient support and zero-anchor cases are retained. `test_screen_pass` is a descriptive holdout flag, not a newly selected set. `P_guard` now refers to the whole guard conjunction. Leakage uses **all player-games** as denominator; conditional failure uses only anchor occurrences. Different leg lists can represent equivalent sporting events, so candidate counts do not measure independent discoveries.

The CSV reports marginal Wilson intervals and reproducible percentile bootstrap intervals for whole-game and whole-player resampling separately. These are sensitivity checks, not a two-way cluster correction or multiplicity-adjusted inference. All-success empirical samples produce bootstrap [1, 1]; keep Wilson uncertainty and never treat that as proof. Zero-anchor bootstrap replicates are counted and omitted from conditional quantiles; all-zero support yields an undefined conditional.

This evaluates later official game dates using final, potentially revised statistics. It does not reconstruct when outcomes became available, so it is not a point-in-time backtest. Suspended-game completion, scoring revisions, market participation and executable-price timing still need explicit handling. The initial April/May exercise is a pipeline and stability check; multi-season generalization remains untested.

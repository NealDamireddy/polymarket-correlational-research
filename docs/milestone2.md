# Milestone 2 design and validation protocol

The April 2015 player-game build is the training set. Candidate definitions and thresholds are frozen in a separate command before May 2015 outcomes are downloaded or evaluated for this combo exercise. No pricing or prediction model is fitted.

## Search

Generate same-row anchor + 1–3 guard structures. Start from supported pairs with at least .99 empirical conditional probability and a .95 Wilson lower bound. Cap guard candidates per anchor at ten and all evaluations at 5,000; log caps and fail if the explicit work budget is exhausted. Count each guard conjunction directly. Retain only joint outcomes meeting the same conditional and support screen. Export training order and a checksummed structured candidate bundle.

The search intentionally retains different leg lists that are logically redundant. They can be distinct market contracts, but are often the same sporting event. Counts and rankings must not be interpreted as independent tests or independent opportunities. Exact proofs mean all guards are individually implied by the anchor, under the configured scoring rules.

## Evaluation

Every frozen candidate is evaluated, without filtering or reordering on holdout statistics. Date overlap and reused game IDs are errors. Missing/invalid batting counts or empirical contradictions of an exact rule are errors. Unsupported candidates and zero-anchor conditionals are preserved. The output retains training/holdout counts, probabilities, intervals and leakage changes, with separate holdout support and screen-pass flags.

Game and player resampling are separate one-way cluster-bootstrap sensitivity analyses. They use the same resampled clusters for all candidates in a run. They do not correct simultaneously for both dependence structures or for testing many related combinations. A percentile bootstrap cannot infer unobserved failures from a perfect sample, so its zero-width interval is not evidence of exactness. Report Wilson intervals alongside it. No nominal confidence guarantee is claimed after candidate selection.

## Timing limitation

Final MLB data can be revised and an official game date can precede its resumption/completion. Strictly later official dates prevent straightforward row/date reuse but do not certify historical availability. Results are labelled retrospective chronological holdout validation, never a point-in-time backtest. Before a historical price backtest, attach outcome availability timestamps and exclude or correctly place unfinished games. Player overlap across periods is intentional; an unseen-player experiment would require another split.

## Data fix discovered during expansion

The source schedule can contain a postponed entry followed by a final makeup entry with the same game ID. The ingestion code now collects all versions and prefers an eligible completed game before deduplication. Other entries remain in the exclusion manifest with their status. Regression tests cover either source order. April's frozen outcomes are unchanged; May's completed games are not lost merely because a postponed version appeared first.

## Tests

Known direct-joint counts distinguish conjunction estimates from multiplied pairwise conditionals. Additional tests cover leakage denominators, exact-proof violations, tiny-support exclusion, guard caps, work-budget failures, deterministic guard-order identities, candidate freezing, chronological/game overlap rejection, bundle tampering, proof-semantic drift, zero-support holdouts, all-candidate retention after failures, and seeded reproducibility.

"""Frozen-candidate retrospective chronological validation; no price backtest."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import pandas as pd
from sports_dependency_engine.backtest.uncertainty import clustered_intervals
from sports_dependency_engine.dependency.combo_search import Combo, ComboConfig, discover_combos, evaluate_combos
from sports_dependency_engine.reports.diagnostics import validate
from sports_dependency_engine.sports.mlb.props import Prop, default_props


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes() -> dict[str, str]:
    root = Path(__file__).resolve().parents[1]
    return {str(p.relative_to(root)): file_hash(p) for p in sorted(root.rglob('*.py'))}


def canonical_hash(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def load_cohort(path: Path) -> tuple[pd.DataFrame, dict]:
    frame = pd.read_parquet(path)
    diagnostics = validate(frame)
    frame['date'] = pd.to_datetime(frame.date, format='%Y-%m-%d', errors='raise').dt.strftime('%Y-%m-%d')
    if frame.groupby('game_id').date.nunique().gt(1).any():
        raise ValueError('A game ID spans multiple official dates')
    cohort = frame.loc[frame.plate_appearances.gt(0)].sort_values(['date', 'game_id', 'player_id']).reset_index(drop=True)
    if cohort.empty:
        raise ValueError('No positive-PA observations')
    return cohort, diagnostics


def freeze_candidates(train: Path, output: Path, config: ComboConfig = ComboConfig(),
                      props: list[Prop] | None = None) -> Path:
    """Create a new immutable-by-convention candidate bundle; refuse overwrites."""
    if output.exists():
        raise FileExistsError(f'Output already exists: {output}; choose a new run directory')
    frame, validation = load_cohort(train)
    selected_props = default_props() if props is None else props
    candidates, statistics, audit = discover_combos(frame, selected_props, config)
    payload = {'schema_version': 1, 'created_at': datetime.now(timezone.utc).isoformat(),
               'train_file': str(train.resolve()), 'train_sha256': file_hash(train),
               'train_start': frame.date.min(), 'train_end': frame.date.max(),
               'train_game_ids': sorted(int(x) for x in frame.game_id.unique()),
               'train_rows': len(frame), 'validation': validation, 'config': asdict(config),
               'props': [asdict(p) for p in selected_props], 'search_audit': audit,
               'source_hashes': source_hashes(),
               'candidates': [c.to_dict() for c in candidates],
               'train_statistics': json.loads(statistics.to_json(orient='records', double_precision=15))}
    bundle = {'sha256': canonical_hash(payload), 'payload': payload}
    output.mkdir(parents=True, exist_ok=False)
    statistics.to_csv(output / 'train_combos.csv', index=False)
    target = output / 'frozen_candidates.json'
    target.write_text(json.dumps(bundle, indent=2, allow_nan=False))
    return target


def read_frozen(path: Path) -> tuple[dict, list[Combo], str]:
    bundle = json.loads(path.read_text())
    payload = bundle['payload']
    if payload['schema_version'] != 1 or canonical_hash(payload) != bundle['sha256']:
        raise ValueError('Candidate bundle checksum/schema mismatch')
    current = source_hashes()
    for name in ('sports/mlb/rules.py', 'dependency/implications.py', 'sports/mlb/props.py'):
        if payload['source_hashes'][name] != current[name]:
            raise ValueError(f'Proof semantics changed since freezing: {name}')
    candidates = [Combo.from_dict(value) for value in payload['candidates']]
    ids = [c.candidate_id for c in candidates]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate frozen candidates')
    if ids != [row['candidate_id'] for row in payload['train_statistics']]:
        raise ValueError('Candidate order and training statistics differ')
    return payload, candidates, bundle['sha256']


def evaluate_holdout(frozen: Path, test: Path, output: Path, replicates: int = 1000, seed: int = 1729) -> Path:
    """Evaluate all frozen candidates in training order, without holdout selection."""
    if output.exists():
        raise FileExistsError(f'Output already exists: {output}; choose a new run directory')
    payload, candidates, bundle_hash = read_frozen(frozen)
    frame, validation = load_cohort(test)
    if frame.date.min() <= payload['train_end']:
        raise ValueError('Holdout must be strictly later than all training dates')
    if set(frame.game_id) & set(payload['train_game_ids']):
        raise ValueError('Training and holdout game IDs overlap')
    config = ComboConfig(**payload['config'])
    measured = evaluate_combos(frame, candidates)
    train_stats = pd.DataFrame(payload['train_statistics'])
    if candidates:
        measured['support_sufficient'] = measured.n_anchor.ge(config.min_anchor) & measured.n_guard.ge(config.min_guard)
        measured['screen_pass'] = (measured.support_sufficient
                                   & measured.P_guard_given_anchor.ge(config.min_conditional)
                                   & measured.P_guard_given_anchor_ci_low.ge(config.min_conditional_lower))
        for cluster in ('game_id', 'player_id'):
            intervals = clustered_intervals(frame, candidates, cluster, replicates=replicates, seed=seed)
            measured = measured.merge(intervals, on='candidate_id', validate='one_to_one', sort=False)
        descriptors = ['candidate_id', 'sport', 'anchor', 'guards', 'n_guards', 'type',
                       'n_guards_proven_from_anchor', 'proofs']
        combined = train_stats.rename(columns={c: 'train_'+c for c in train_stats if c not in descriptors})
        holdout = measured.drop(columns=[c for c in descriptors if c != 'candidate_id'])
        holdout = holdout.rename(columns={c: 'test_'+c for c in holdout if c != 'candidate_id'})
        combined = combined.merge(holdout, on='candidate_id', how='left', validate='one_to_one', sort=False)
        combined['conditional_change'] = combined.test_P_guard_given_anchor-combined.train_P_guard_given_anchor
        combined['leakage_change'] = combined.test_leakage-combined.train_leakage
    else:
        combined = pd.DataFrame(columns=['candidate_id', 'anchor', 'guards', 'type'])
    manifest = {'created_at': datetime.now(timezone.utc).isoformat(), 'frozen_file': str(frozen.resolve()),
                'frozen_sha256': bundle_hash, 'frozen_file_sha256': file_hash(frozen),
                'train_start': payload['train_start'], 'train_end': payload['train_end'],
                'train_rows': payload['train_rows'], 'train_games': len(payload['train_game_ids']),
                'test_file': str(test.resolve()), 'test_sha256': file_hash(test),
                'test_start': frame.date.min(), 'test_end': frame.date.max(),
                'test_rows': len(frame), 'test_games': int(frame.game_id.nunique()),
                'test_validation': validation, 'config': payload['config'],
                'search_audit': payload['search_audit'], 'candidates_evaluated': len(candidates),
                'bootstrap_replicates': replicates, 'bootstrap_seed': seed, 'source_hashes': source_hashes(),
                'interpretation': 'Retrospective official-date holdout; not point-in-time or executable-price backtest'}
    from sports_dependency_engine.reports.combos import combo_report
    report = combo_report(combined, manifest)
    output.mkdir(parents=True, exist_ok=False)
    combined.to_csv(output / 'holdout_combos.csv', index=False)
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False))
    (output / 'research_report.md').write_text(report)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    freeze = sub.add_parser('freeze', help='Search training outcomes and freeze candidates')
    freeze.add_argument('--train', type=Path, required=True)
    freeze.add_argument('--output', type=Path, required=True)
    freeze.add_argument('--min-anchor', type=int, default=100)
    freeze.add_argument('--min-guard', type=int, default=100)
    freeze.add_argument('--max-guards', type=int, default=3)
    freeze.add_argument('--guard-cap', type=int, default=10)
    freeze.add_argument('--max-evaluations', type=int, default=5000)
    evaluate = sub.add_parser('evaluate', help='Evaluate every frozen candidate on later data')
    evaluate.add_argument('--frozen', type=Path, required=True)
    evaluate.add_argument('--test', type=Path, required=True)
    evaluate.add_argument('--output', type=Path, required=True)
    evaluate.add_argument('--bootstrap-replicates', type=int, default=1000)
    evaluate.add_argument('--seed', type=int, default=1729)
    args = parser.parse_args()
    if args.command == 'freeze':
        result = freeze_candidates(args.train, args.output,
                                   ComboConfig(min_anchor=args.min_anchor, min_guard=args.min_guard,
                                               max_guards=args.max_guards, max_candidates_per_anchor=args.guard_cap,
                                               max_evaluations=args.max_evaluations))
    else:
        result = evaluate_holdout(args.frozen, args.test, args.output, args.bootstrap_replicates, args.seed)
    print(result)

if __name__ == '__main__':
    main()

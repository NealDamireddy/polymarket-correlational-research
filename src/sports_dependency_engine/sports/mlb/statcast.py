"""Optional cached pitch-level enrichment; not authoritative batter run/RBI totals."""
from datetime import date, timedelta
from pathlib import Path
import pandas as pd

def download_statcast(start: str, end: str, cache: Path) -> list[Path]:
    """Cache each day separately; install the statcast extra before calling."""
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if first.year < 2015 or first > last:
        raise ValueError("Require 2015 onward and ordered dates")
    from pybaseball import statcast
    cache.mkdir(parents=True, exist_ok=True)
    paths = []
    while first <= last:
        path = cache / f"statcast_{first.isoformat()}.parquet"
        if not path.exists():
            frame: pd.DataFrame = statcast(first.isoformat(), first.isoformat())
            temporary = path.with_suffix(".tmp")
            frame.to_parquet(temporary, index=False)
            temporary.replace(path)
        paths.append(path)
        first += timedelta(days=1)
    return paths

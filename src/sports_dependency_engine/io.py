"""GET-only cached public data with provenance and atomic cache writes."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class CachedClient:
    def __init__(self, cache: Path, offline: bool = False):
        self.cache = cache
        self.offline = offline
        self.used: dict[str, dict] = {}
        self.session = requests.Session()
        retries = Retry(total=4, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"])
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def get(self, url: str, params: dict | None = None) -> Any:
        prepared = requests.Request("GET", url, params=sorted((params or {}).items())).prepare().url
        key = hashlib.sha256(prepared.encode()).hexdigest()
        path = self.cache / f"{key}.json"
        if path.exists():
            envelope = json.loads(path.read_text())
        else:
            if self.offline:
                raise FileNotFoundError(f"Offline cache miss: {prepared}")
            response = self.session.get(prepared, timeout=(10, 60))
            response.raise_for_status()
            envelope = {"url": prepared, "retrieved_at": datetime.now(timezone.utc).isoformat(), "payload": response.json()}
            self.cache.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(".tmp")
            temporary.write_text(json.dumps(envelope, sort_keys=True))
            temporary.replace(path)
        self.used[key] = {"file": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                          "url": envelope["url"], "retrieved_at": envelope["retrieved_at"]}
        return envelope["payload"]

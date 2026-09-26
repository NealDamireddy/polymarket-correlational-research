"""Public GET-only market catalog access. Use a separate timestamped price cache."""
from sports_dependency_engine.io import CachedClient

GAMMA = "https://gamma-api.polymarket.com"

def sports(client: CachedClient) -> list[dict]:
    return client.get(f"{GAMMA}/sports")

def events_page(client: CachedClient, tag_id: int, offset: int = 0, limit: int = 100) -> list[dict]:
    """Fetch one explicit page; callers must paginate and retain raw metadata."""
    if offset < 0 or not 1 <= limit <= 100:
        raise ValueError("Invalid pagination")
    return client.get(f"{GAMMA}/events", {"tag_id": tag_id, "active": "true", "closed": "false", "limit": limit, "offset": offset})

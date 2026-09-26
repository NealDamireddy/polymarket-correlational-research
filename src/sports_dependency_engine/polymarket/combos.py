"""Public eligible-leg catalog only. Authenticated RFQ creation is out of scope."""
from sports_dependency_engine.io import CachedClient

def combo_markets_page(client: CachedClient, cursor: str | None = None) -> dict:
    params = {"limit": 50}
    if cursor:
        params["cursor"] = cursor
    return client.get("https://combos-rfq-api.polymarket.com/v1/rfq/combo-markets", params)

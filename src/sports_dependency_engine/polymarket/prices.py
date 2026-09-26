"""Raw CLOB order books; no midpoint is presented as executable probability."""
from sports_dependency_engine.io import CachedClient

def order_book(client: CachedClient, token_id: str) -> dict:
    return client.get("https://clob.polymarket.com/book", {"token_id": token_id})

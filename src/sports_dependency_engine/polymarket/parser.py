"""Conservative array normalization; player/threshold matching remains manual."""
import json

def normalize_outcomes(market: dict) -> list[dict]:
    def array(name: str) -> list:
        value = market[name]
        value = json.loads(value) if isinstance(value, str) else value
        if not isinstance(value, list):
            raise ValueError(f"{name} is not an array")
        return value
    names, tokens, prices = array("outcomes"), array("clobTokenIds"), array("outcomePrices")
    if not len(names) == len(tokens) == len(prices):
        raise ValueError("Misaligned outcome arrays")
    return [{"outcome": n, "token_id": t, "indicative_price": float(p)} for n, t, p in zip(names, tokens, prices)]

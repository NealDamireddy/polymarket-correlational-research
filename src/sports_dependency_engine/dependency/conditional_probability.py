"""Public conditional estimate helper."""
from sports_dependency_engine.dependency.metrics import wilson

def estimate(successes: int, anchors: int) -> dict[str, float | int]:
    low, high = wilson(successes, anchors)
    return {"successes": successes, "anchors": anchors,
            "probability": successes / anchors if anchors else float("nan"),
            "ci_low": low, "ci_high": high}

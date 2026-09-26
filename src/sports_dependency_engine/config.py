"""Versioned research policy; thresholds are not optimized on observed data."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ResearchConfig:
    min_anchor: int = 100
    min_guard: int = 100
    near_probability: float = 0.99
    near_lower_bound: float = 0.95
    strong_lift: float = 1.5

    def __post_init__(self) -> None:
        if self.min_anchor < 1 or self.min_guard < 1:
            raise ValueError("Support thresholds must be positive")
        if not 0 <= self.near_lower_bound <= self.near_probability <= 1:
            raise ValueError("Invalid probability thresholds")
        if self.strong_lift <= 1:
            raise ValueError("Strong lift must exceed one")

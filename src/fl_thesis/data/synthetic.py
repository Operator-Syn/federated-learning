"""Synthetic inputs used by the workspace smoke test.

Placeholder data only — the study proper takes its series from the simulation and the
calibration data. Kept in a module so the smoke test exercises a real import path
instead of an inline expression that nothing else can call.
"""

from __future__ import annotations

import numpy as np


def availability_series(
    rounds: int = 20,
    *,
    seed: int = 20261118,
    minimum: int = 3,
    span: int = 3,
) -> np.ndarray:
    """Return a reproducible count of reachable stations per round.

    Args:
        rounds: number of training rounds to generate.
        seed: RNG seed; the same seed always yields the same series.
        minimum: smallest count of reachable stations.
        span: width of the inclusive range above ``minimum``.

    Returns:
        An ``int`` array of length ``rounds`` with values in
        ``[minimum, minimum + span - 1]``.
    """
    if rounds < 0:
        raise ValueError("rounds must be non-negative")
    if minimum < 0 or span < 1:
        raise ValueError("minimum must be >= 0 and span >= 1")

    rng = np.random.default_rng(seed)
    return minimum + rng.integers(0, span, size=rounds)

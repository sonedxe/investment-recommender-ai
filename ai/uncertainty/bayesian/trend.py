"""Market trend signal ``s_tend`` in [-1, 1] used by the context rule RC6.

    s_tend = clip((r_12m - mu) / sigma, -1, 1)

``r_12m`` is the compounded return of the last ``window`` monthly returns and
``mu``/``sigma`` are annual, so the signal reads as "how many annual standard
deviations the last year deviated from the expected return". With fewer than
``window`` months (or ``sigma = 0``) the trend is neutral (0).
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def trend_signal(monthly_returns: ArrayLike, mu: float, sigma: float, window: int = 12) -> float:
    returns = np.asarray(monthly_returns, dtype=float)
    if window < 1:
        raise ValueError("window must be positive")
    if len(returns) < window or sigma <= 0:
        return 0.0
    r_window = float(np.prod(1.0 + returns[-window:]) - 1.0)
    return float(np.clip((r_window - mu) / sigma, -1.0, 1.0))

"""Human-like delay utilities."""

import random
import time


def human_delay(min_sec: float = 0.5, max_sec: float = 1.0) -> float:
    """
    Wait for a random duration (normally distributed) to simulate human behavior.

    Args:
        min_sec: Minimum delay in seconds
        max_sec: Maximum delay in seconds

    Returns:
        The actual delay used
    """
    # Use normal distribution centered between min and max
    mean = (min_sec + max_sec) / 2
    std = (max_sec - min_sec) / 4  # ~95% of values within range

    delay = random.gauss(mean, std)
    # Clamp to min/max
    delay = max(min_sec, min(max_sec, delay))

    print(f"  (waiting {delay:.1f}s)")
    time.sleep(delay)
    return delay

import numpy as np
from math import sin, pi
import random


def generate_step(
    t: float, period: float, amplitude: float, error: float = 1, mean: float = 0
) -> float:
    return mean + sin(2 * pi * t / period) * amplitude + random.random() * error

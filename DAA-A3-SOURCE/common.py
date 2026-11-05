"""Reconstructed shared helpers; seed and conventions follow PDF page 1."""
from dataclasses import dataclass, field
import random
import statistics
import time
SEED = 2401
@dataclass
class Counter:
    comps: int = 0
    mult: int = 0
    add: int = 0
    calls: int = 0
    depth: int = 0
    distances: int = 0
    steps: int = 0
    largest_side: float = 0.0
    parts: list = field(default_factory=list)
    def reset(self):
        self.__dict__.update(Counter().__dict__)
def seeded_rng():
    return random.Random(SEED)
def median_ms(fn, reps=3):
    samples=[]
    for _ in range(reps):
        start=time.perf_counter(); fn(); samples.append((time.perf_counter()-start)*1000)
    return statistics.median(samples)

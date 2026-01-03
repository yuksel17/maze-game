"""Utilities needed for Guitar Riff Pathfinding (A*, search, distances, PQ)"""

import bisect
import collections
import collections.abc
import functools
import heapq
import random
from itertools import chain, combinations
from statistics import mean
import numpy as np

# =============================================================================
# 1. Priority Queue — A* için en gerekli yapı
# =============================================================================

class PriorityQueue:
    """A Queue where the min (or max) element is returned first (for A* search)."""

    def __init__(self, order='min', f=lambda x: x):
        self.heap = []
        self.f = f if order == 'min' else (lambda x: -f(x))

    def append(self, item):
        heapq.heappush(self.heap, (self.f(item), item))

    def extend(self, items):
        for item in items:
            self.append(item)

    def pop(self):
        if self.heap:
            return heapq.heappop(self.heap)[1]
        raise Exception('Trying to pop from empty PriorityQueue.')

    def __len__(self):
        return len(self.heap)

    def __contains__(self, key):
        return any(item == key for _, item in self.heap)


# =============================================================================
# 2. Useful sequence utilities
# =============================================================================

def first(iterable, default=None):
    """Return first element."""
    return next(iter(iterable), default)

def shuffled(iterable):
    items = list(iterable)
    random.shuffle(items)
    return items

identity = lambda x: x

def argmin_random_tie(seq, key=identity):
    """Return a min element; break ties randomly."""
    return min(shuffled(seq), key=key)

def argmax_random_tie(seq, key=identity):
    return max(shuffled(seq), key=key)


# =============================================================================
# 3. Basic math / vector tools — parmak hareketi cost hesaplarında kullanılır
# =============================================================================

def vector_add(a, b):
    """Component-wise addition."""
    if hasattr(a, '__iter__') and hasattr(b, '__iter__'):
        assert len(a) == len(b)
        return list(map(vector_add, a, b))
    return a + b


def scalar_vector_product(x, y):
    """Multiply vector by scalar."""
    return [scalar_vector_product(x, _y) for _y in y] if hasattr(y, '__iter__') else x * y


# =============================================================================
# 4. Distance metrics — fretboard hareketi için kritik
# =============================================================================

def euclidean_distance(x, y):
    return np.sqrt(sum((_x - _y) ** 2 for _x, _y in zip(x, y)))

def manhattan_distance(x, y):
    return sum(abs(_x - _y) for _x, _y in zip(x, y))

def hamming_distance(x, y):
    return sum(_x != _y for _x, _y in zip(x, y))


# =============================================================================
# 5. Utility: memoization — heuristic caching
# =============================================================================

def memoize(fn, slot=None, maxsize=32):
    if slot:
        def memoized_fn(obj, *args):
            if hasattr(obj, slot):
                return getattr(obj, slot)
            else:
                val = fn(obj, *args)
                setattr(obj, slot, val)
                return val
    else:
        @functools.lru_cache(maxsize=maxsize)
        def memoized_fn(*args):
            return fn(*args)
    return memoized_fn

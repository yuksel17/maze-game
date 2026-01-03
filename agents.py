import math
from collections import namedtuple

# ------------------------------------------------------------
# 1. Basic helpers
# ------------------------------------------------------------

def is_in(thing, seq):
    """Check if thing is equal to some item in seq."""
    return any(thing == x for x in seq)

# ------------------------------------------------------------
# 2. 2D geometric utilities
# ------------------------------------------------------------

Point = namedtuple("Point", "x y")

def turn_heading(heading, inc):
    """Turn a heading by an increment (heading in degrees)."""
    return (heading + inc) % 360

def distance_squared(a, b):
    """Return squared Euclidean distance between two points/vectors."""
    return sum((x - y) ** 2 for x, y in zip(a, b))

def dot_product(a, b):
    """Dot product of two vectors."""
    return sum(x * y for x, y in zip(a, b))

# ------------------------------------------------------------
# 3. 2D movement helpers (might be useful for modeling fret shifts)
# ------------------------------------------------------------

orientations = [0, 90, 180, 270]  # cardinal directions

def vector_add(a, b):
    """Component-wise vector addition."""
    return tuple(x + y for x, y in zip(a, b))

# ------------------------------------------------------------
# Done — everything else removed.
# ------------------------------------------------------------

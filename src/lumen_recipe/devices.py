"""Immutable, bounded device geometry. No device discovery or hardware I/O."""
from dataclasses import dataclass
import json
import math
from pathlib import Path

@dataclass(frozen=True)
class DeviceProfile:
    name: str
    top_width: int
    top_height: int
    key_coordinates: tuple

    def __post_init__(self):
        if type(self.name) is not str or not 1 <= len(self.name) <= 80 or not self.name.isascii() or not all(c.isalnum() or c in "-_" for c in self.name):
            raise ValueError("Device name must contain 1–80 ASCII letters, digits, hyphens or underscores")
        if any(type(n) is not int or not 1 <= n <= 64 for n in (self.top_width, self.top_height)) or self.top_width * self.top_height > 2048:
            raise ValueError("Matrix dimensions must be 1–64, at most 2048 pixels")
        if type(self.key_coordinates) not in (tuple, list) or not 1 <= len(self.key_coordinates) <= 1024:
            raise ValueError("Provide 1–1024 key coordinates, using null for reserved positions")
        result = []
        for point in self.key_coordinates:
            if point is None:
                result.append(None)
            elif type(point) in (tuple, list) and len(point) == 2 and all(type(v) in (float, int) and 0 <= v <= 1 and math.isfinite(v) for v in point):
                result.append(tuple(point))
            else:
                raise ValueError("Key coordinates must be finite normalized [x,y] pairs or null")
        if not any(point is not None for point in result):
            raise ValueError("At least one active key coordinate is required")
        object.__setattr__(self, "key_coordinates", tuple(result))

    @property
    def top_coordinates(self):
        return tuple((x / (self.top_width - 1) if self.top_width > 1 else .5,
                      y / (self.top_height - 1) if self.top_height > 1 else .5)
                     for y in range(self.top_height) for x in range(self.top_width))

    @property
    def reserved_keys(self):
        return frozenset(i for i, point in enumerate(self.key_coordinates) if point is None)

    @property
    def active_keys(self):
        return tuple(i for i, point in enumerate(self.key_coordinates) if point is not None)

    def to_dict(self):
        return {"name": self.name, "top_width": self.top_width, "top_height": self.top_height,
                "key_coordinates": [list(point) if point is not None else None for point in self.key_coordinates]}

    @classmethod
    def resolve(cls, value):
        if isinstance(value, cls):
            return value
        if value == "cyberboard":
            return CYBERBOARD
        if value == "matrix16":
            return MATRIX16
        if type(value) is dict and set(value) == {"name", "top_width", "top_height", "key_coordinates"}:
            return cls(**value)
        raise ValueError("Expected a DeviceProfile, exact profile object, cyberboard or matrix16")

CYBERBOARD = DeviceProfile(**json.loads(Path(__file__).with_name("cyberboard.json").read_text(encoding="utf-8")))
MATRIX16 = DeviceProfile("matrix16", 16, 16, tuple((i / 15, .5) for i in range(16)))

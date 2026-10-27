"""Предметні класи з повним порядком через functools.total_ordering."""

from dataclasses import dataclass
from functools import total_ordering


@total_ordering
@dataclass(frozen=True, eq=False)
class Booking:
    """Бронювання: порядок за вартістю, потім за кількістю ночей, потім за гостем."""

    guest: str
    nights: int
    room_type: str
    price: float
    status: str
    total_price: float

    def _key(self) -> tuple[float, int, str]:
        """Ключ порівняння."""
        return (self.total_price, self.nights, self.guest)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Booking):
            return NotImplemented
        return self._key() == other._key()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Booking):
            return NotImplemented
        return self._key() < other._key()

    def __hash__(self) -> int:
        return hash(self._key())


@total_ordering
@dataclass(frozen=True, eq=False)
class Box:
    """Коробка: порядок за об'ємом, потім за площею фронтальної грані, потім за w."""

    w: float
    h: float
    d: float

    def _key(self) -> tuple[float, float, float]:
        """Ключ порівняння: (об'єм, площа w*h, w)."""
        return (self.w * self.h * self.d, self.w * self.h, self.w)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Box):
            return NotImplemented
        return self._key() == other._key()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Box):
            return NotImplemented
        return self._key() < other._key()

    def __hash__(self) -> int:
        return hash(self._key())

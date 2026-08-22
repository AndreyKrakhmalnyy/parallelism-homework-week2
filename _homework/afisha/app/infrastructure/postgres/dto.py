from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class SalesSummary:
    paid_orders: int
    revenue: int


@dataclass(slots=True, frozen=True)
class OccupancySummary:
    total: int
    available: int
    reserved: int
    sold: int

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class SalesSummaryDTO:
    paid_orders: int
    revenue: int


@dataclass(slots=True, frozen=True)
class OccupancySummaryDTO:
    total: int
    available: int
    reserved: int
    sold: int

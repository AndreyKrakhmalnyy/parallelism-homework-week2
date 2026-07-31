from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class SalesDashboard(BaseModel):
    paid_orders: int    
    sold_tickets: int
    revenue: int
    average_order: int


class OccupancyDashboard(BaseModel):
    total: int
    available: int
    reserved: int
    sold: int
    occupancy_percent: float


class EventDashboard(BaseModel):
    event_title: str
    starts_at: datetime
    sales: SalesDashboard
    occupancy: OccupancyDashboard


class EventCreate(BaseModel):
    location_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    category: str = Field(min_length=1, max_length=100)
    starts_at: datetime
    base_price: int = Field(gt=0)


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organizer_id: int
    location_id: int
    title: str
    description: str | None
    category: str
    starts_at: datetime
    base_price: int
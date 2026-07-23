from app.api.schemas.seat import SeatRead
from pydantic import BaseModel, ConfigDict


class LocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    city: str
    address: str


class LocationDetail(BaseModel):
    location: LocationRead
    seats: list[SeatRead]
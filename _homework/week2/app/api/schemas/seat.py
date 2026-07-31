from pydantic import BaseModel


class SeatRead(BaseModel):
    id: int
    location_id: int
    sector: str
    row: int
    number: int
    x: int
    y: int
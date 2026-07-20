class DomainError(Exception):
    pass

class EventNotFoundError(Exception):
    def __init__(self, event_id: int) -> None:
        self.detail = f"Event with ID={event_id} not found"
        super().__init__(self.detail)
    
class SeatNotFoundError(Exception):
    def __init__(self, seat_id: int) -> None:
        self.detail = f"Seat with ID={seat_id} not found"
        super().__init__(self.detail)
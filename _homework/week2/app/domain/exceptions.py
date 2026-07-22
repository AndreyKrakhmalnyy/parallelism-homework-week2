class DomainError(Exception):
    pass

class EventSeatNotFoundError(Exception):
    def __init__(self, event_id: int, seat_ids: list[int]) -> None:
        self.detail = f"Selected seats (with IDs {", ".join(str(seat) for seat in seat_ids)}) for event with ID={event_id} not found"
        super().__init__(self.detail)

class EventNotFoundError(Exception):
    def __init__(self, event_id: int) -> None:
        self.detail = f"Event with event_id={event_id} not found"
        super().__init__(self.detail)

class SeatNotAvailableError(Exception):
    def __init__(self, event_id: int, seat_id: int) -> None:
        self.detail = f"Seat {seat_id} for event {event_id} is not available"
        super().__init__(self.detail)
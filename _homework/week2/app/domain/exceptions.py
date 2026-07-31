class DomainError(Exception):
    status_code = 400

class EventSeatNotFoundError(DomainError):
    status_code = 404
    def __init__(self, event_id: int, seat_ids: list[int]) -> None:
        self.detail = f"Selected seats (with IDs {", ".join(str(seat) for seat in seat_ids)}) for event with ID={event_id} not found"
        super().__init__(self.detail)

class EventNotFoundError(DomainError):
    status_code = 404
    def __init__(self, event_id: int) -> None:
        self.detail = f"Event with event_id={event_id} not found"
        super().__init__(self.detail)

class SeatReservationError(DomainError):
    status_code = 409
    def __init__(self, event_id: int, seat_id: int) -> None:
        self.detail = f"Seat {seat_id} for event {event_id} is not available. Please, try later."
        super().__init__(self.detail)

class PaymentNotAvailableError(DomainError):
    status_code = 503
    def __init__(self, event_id: int) -> None:
        self.detail = f"Payment for event with ID={event_id} is not available. Please, try later."
        super().__init__(self.detail)
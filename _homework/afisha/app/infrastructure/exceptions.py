class InfrastructureError(Exception):
    pass

class EventViewConsumeringError(InfrastructureError):
    def __init__(self, error_msg: str) -> None:
        self.detail = f"Unexpected error while processing 'EventView' queue: {error_msg}"
        super().__init__(self.detail)
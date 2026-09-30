from typing import Literal, Optional, TypedDict
from faststream import AckPolicy


class SubscriberParams(TypedDict, total=False):
    batch: bool
    max_records: Optional[int]
    ack_policy: AckPolicy
    batch_timeout_ms: int
    auto_offset_reset: Literal["latest", "earliest", "none"]
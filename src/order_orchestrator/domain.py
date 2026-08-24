from dataclasses import dataclass
from enum import Enum


class OrderState(str, Enum):
    PENDING = "pending"
    INVENTORY_RESERVED = "inventory_reserved"
    PAYMENT_AUTHORIZED = "payment_authorized"
    FULFILLMENT_REQUESTED = "fulfillment_requested"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    FAILED = "failed"


@dataclass(frozen=True)
class OrderSaga:
    order_id: str
    state: OrderState = OrderState.PENDING
    inventory_reserved: bool = False
    payment_authorized: bool = False
    fulfillment_requested: bool = False

from dataclasses import dataclass, replace
from enum import Enum
from typing import Optional


class FulfillmentState(str, Enum):
    READY = "ready"
    LABEL_CREATED = "label_created"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    EXCEPTION = "exception"


@dataclass(frozen=True)
class Fulfillment:
    order_id: str
    state: FulfillmentState = FulfillmentState.READY
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    exception_reason: Optional[str] = None


def attach_label(fulfillment: Fulfillment, carrier: str, tracking_number: str) -> Fulfillment:
    if fulfillment.state != FulfillmentState.READY:
        raise ValueError("label can only be attached from ready state")
    return replace(
        fulfillment,
        state=FulfillmentState.LABEL_CREATED,
        carrier=carrier,
        tracking_number=tracking_number,
    )


def mark_in_transit(fulfillment: Fulfillment) -> Fulfillment:
    if fulfillment.state != FulfillmentState.LABEL_CREATED:
        raise ValueError("shipment must have a label before transit")
    return replace(fulfillment, state=FulfillmentState.IN_TRANSIT)


def mark_delivered(fulfillment: Fulfillment) -> Fulfillment:
    if fulfillment.state != FulfillmentState.IN_TRANSIT:
        raise ValueError("only in-transit shipments can be delivered")
    return replace(fulfillment, state=FulfillmentState.DELIVERED)


def mark_exception(fulfillment: Fulfillment, reason: str) -> Fulfillment:
    if fulfillment.state == FulfillmentState.DELIVERED:
        raise ValueError("delivered shipment cannot enter exception")
    return replace(
        fulfillment,
        state=FulfillmentState.EXCEPTION,
        exception_reason=reason,
    )

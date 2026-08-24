from dataclasses import replace

from .domain import OrderSaga, OrderState


class InvalidTransition(ValueError):
    pass


def reserve_inventory(saga: OrderSaga) -> OrderSaga:
    if saga.state != OrderState.PENDING:
        raise InvalidTransition(f"cannot reserve inventory from {saga.state}")
    return replace(saga, state=OrderState.INVENTORY_RESERVED, inventory_reserved=True)


def authorize_payment(saga: OrderSaga) -> OrderSaga:
    if saga.state != OrderState.INVENTORY_RESERVED:
        raise InvalidTransition(f"cannot authorize payment from {saga.state}")
    return replace(saga, state=OrderState.PAYMENT_AUTHORIZED, payment_authorized=True)


def request_fulfillment(saga: OrderSaga) -> OrderSaga:
    if saga.state != OrderState.PAYMENT_AUTHORIZED:
        raise InvalidTransition(f"cannot request fulfillment from {saga.state}")
    return replace(saga, state=OrderState.FULFILLMENT_REQUESTED, fulfillment_requested=True)


def complete(saga: OrderSaga) -> OrderSaga:
    if saga.state != OrderState.FULFILLMENT_REQUESTED:
        raise InvalidTransition(f"cannot complete from {saga.state}")
    return replace(saga, state=OrderState.COMPLETED)


def compensate(saga: OrderSaga) -> OrderSaga:
    if saga.state in {OrderState.COMPLETED, OrderState.FAILED}:
        raise InvalidTransition(f"cannot compensate from {saga.state}")
    return replace(
        saga,
        state=OrderState.FAILED,
        inventory_reserved=False,
        payment_authorized=False,
        fulfillment_requested=False,
    )

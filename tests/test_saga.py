from order_orchestrator.domain import OrderSaga, OrderState
from order_orchestrator.saga import (
    authorize_payment,
    complete,
    compensate,
    request_fulfillment,
    reserve_inventory,
)


def test_happy_path_reaches_completed():
    saga = OrderSaga(order_id="o-1")
    saga = reserve_inventory(saga)
    saga = authorize_payment(saga)
    saga = request_fulfillment(saga)
    saga = complete(saga)
    assert saga.state == OrderState.COMPLETED


def test_compensation_clears_side_effect_flags():
    saga = authorize_payment(reserve_inventory(OrderSaga(order_id="o-2")))
    failed = compensate(saga)
    assert failed.state == OrderState.FAILED
    assert not failed.inventory_reserved
    assert not failed.payment_authorized

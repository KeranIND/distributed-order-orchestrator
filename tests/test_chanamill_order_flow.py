from order_orchestrator.chanamill import (
    MTMOrder,
    MTMState,
    authorize_payment,
    capture_fit_feedback,
    complete,
    lock_profile,
    mark_delivered,
    pass_qc,
    request_fulfillment,
    request_production,
)


def test_mtm_order_reaches_completed_with_fit_feedback():
    order = MTMOrder(
        order_id="cm-order-1",
        fitid_snapshot_id="fitid-v12",
        garment_spec_version="shirt-spec-v7",
    )
    order = lock_profile(order)
    order = authorize_payment(order)
    order = request_production(order, "prod-1001")
    order = pass_qc(order)
    order = request_fulfillment(order, "ship-501")
    order = mark_delivered(order)
    order = capture_fit_feedback(order, "feedback-77")
    order = complete(order)

    assert order.state == MTMState.COMPLETED
    assert order.production_job_id == "prod-1001"
    assert order.shipment_id == "ship-501"
    assert order.fit_feedback_id == "feedback-77"
    assert order.history[0] == "fitid.snapshot.locked"
    assert order.history[-1] == "order.completed"

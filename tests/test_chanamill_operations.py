from decimal import Decimal

from order_orchestrator.creator_commerce import CommissionPolicy, CreatorAttribution
from order_orchestrator.fulfillment import Fulfillment, FulfillmentState, attach_label, mark_delivered, mark_in_transit
from order_orchestrator.manufacturing import ProductionJob, ProductionState, advance, record_qc


def test_production_job_reaches_ready_to_ship_after_qc_pass():
    job = ProductionJob(
        job_id="job-1",
        order_id="order-1",
        fitid_version=4,
        garment_spec_version="shirt-v7",
        factory_partner_id="india-partner-1",
    )
    job = advance(job, ProductionState.CUTTING)
    job = advance(job, ProductionState.STITCHING)
    job = advance(job, ProductionState.QC_PENDING)
    job = record_qc(job, passed=True, notes="measurements verified")
    job = advance(job, ProductionState.READY_TO_SHIP)
    assert job.state == ProductionState.READY_TO_SHIP


def test_creator_commission_uses_order_attribution():
    attribution = CreatorAttribution(
        order_id="order-2",
        creator_id="creator-7",
        storefront_id="store-3",
        source="creator_storefront",
    )
    policy = CommissionPolicy(rate=Decimal("0.12"))
    assert attribution.attributed
    assert policy.commission(Decimal("100.00")) == Decimal("12.00")


def test_fulfillment_reaches_delivered_state():
    shipment = Fulfillment(order_id="order-3")
    shipment = attach_label(shipment, "carrier", "TRACK-1")
    shipment = mark_in_transit(shipment)
    shipment = mark_delivered(shipment)
    assert shipment.state == FulfillmentState.DELIVERED

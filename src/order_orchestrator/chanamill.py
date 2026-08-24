from dataclasses import dataclass, field, replace
from enum import Enum
from typing import List, Optional


class MTMState(str, Enum):
    PENDING = "pending"
    PROFILE_LOCKED = "profile_locked"
    PAYMENT_AUTHORIZED = "payment_authorized"
    PRODUCTION_REQUESTED = "production_requested"
    QC_PASSED = "qc_passed"
    FULFILLMENT_REQUESTED = "fulfillment_requested"
    DELIVERED = "delivered"
    FEEDBACK_CAPTURED = "feedback_captured"
    COMPLETED = "completed"
    REVIEW_REQUIRED = "review_required"
    FAILED = "failed"


@dataclass(frozen=True)
class MTMOrder:
    order_id: str
    fitid_snapshot_id: str
    garment_spec_version: str
    state: MTMState = MTMState.PENDING
    production_job_id: Optional[str] = None
    shipment_id: Optional[str] = None
    fit_feedback_id: Optional[str] = None
    history: List[str] = field(default_factory=list)


class InvalidMTMTransition(ValueError):
    pass


def _move(order: MTMOrder, expected: MTMState, target: MTMState, event: str, **changes) -> MTMOrder:
    if order.state != expected:
        raise InvalidMTMTransition(f"cannot apply {event} from {order.state}")
    return replace(order, state=target, history=[*order.history, event], **changes)


def lock_profile(order: MTMOrder) -> MTMOrder:
    return _move(order, MTMState.PENDING, MTMState.PROFILE_LOCKED, "fitid.snapshot.locked")


def authorize_payment(order: MTMOrder) -> MTMOrder:
    return _move(order, MTMState.PROFILE_LOCKED, MTMState.PAYMENT_AUTHORIZED, "payment.authorized")


def request_production(order: MTMOrder, production_job_id: str) -> MTMOrder:
    return _move(
        order,
        MTMState.PAYMENT_AUTHORIZED,
        MTMState.PRODUCTION_REQUESTED,
        "production.requested",
        production_job_id=production_job_id,
    )


def pass_qc(order: MTMOrder) -> MTMOrder:
    return _move(order, MTMState.PRODUCTION_REQUESTED, MTMState.QC_PASSED, "qc.passed")


def request_fulfillment(order: MTMOrder, shipment_id: str) -> MTMOrder:
    return _move(
        order,
        MTMState.QC_PASSED,
        MTMState.FULFILLMENT_REQUESTED,
        "fulfillment.requested",
        shipment_id=shipment_id,
    )


def mark_delivered(order: MTMOrder) -> MTMOrder:
    return _move(order, MTMState.FULFILLMENT_REQUESTED, MTMState.DELIVERED, "order.delivered")


def capture_fit_feedback(order: MTMOrder, fit_feedback_id: str) -> MTMOrder:
    return _move(
        order,
        MTMState.DELIVERED,
        MTMState.FEEDBACK_CAPTURED,
        "fit.feedback.captured",
        fit_feedback_id=fit_feedback_id,
    )


def complete(order: MTMOrder) -> MTMOrder:
    return _move(order, MTMState.FEEDBACK_CAPTURED, MTMState.COMPLETED, "order.completed")


def require_review(order: MTMOrder, reason: str) -> MTMOrder:
    if order.state in {MTMState.COMPLETED, MTMState.FAILED}:
        raise InvalidMTMTransition(f"cannot require review from {order.state}")
    return replace(order, state=MTMState.REVIEW_REQUIRED, history=[*order.history, f"review.required:{reason}"])

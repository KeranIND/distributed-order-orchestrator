from dataclasses import dataclass, replace
from enum import Enum
from typing import Optional


class ProductionState(str, Enum):
    QUEUED = "queued"
    CUTTING = "cutting"
    STITCHING = "stitching"
    QC_PENDING = "qc_pending"
    QC_PASSED = "qc_passed"
    QC_FAILED = "qc_failed"
    READY_TO_SHIP = "ready_to_ship"


@dataclass(frozen=True)
class ProductionJob:
    job_id: str
    order_id: str
    fitid_version: int
    garment_spec_version: str
    factory_partner_id: str
    state: ProductionState = ProductionState.QUEUED
    qc_notes: Optional[str] = None


def advance(job: ProductionJob, next_state: ProductionState) -> ProductionJob:
    allowed = {
        ProductionState.QUEUED: {ProductionState.CUTTING},
        ProductionState.CUTTING: {ProductionState.STITCHING},
        ProductionState.STITCHING: {ProductionState.QC_PENDING},
        ProductionState.QC_PENDING: {ProductionState.QC_PASSED, ProductionState.QC_FAILED},
        ProductionState.QC_FAILED: {ProductionState.STITCHING},
        ProductionState.QC_PASSED: {ProductionState.READY_TO_SHIP},
    }
    if next_state not in allowed.get(job.state, set()):
        raise ValueError(f"invalid production transition {job.state} -> {next_state}")
    return replace(job, state=next_state)


def record_qc(job: ProductionJob, passed: bool, notes: str) -> ProductionJob:
    if job.state != ProductionState.QC_PENDING:
        raise ValueError("QC can only be recorded while qc_pending")
    return replace(
        job,
        state=ProductionState.QC_PASSED if passed else ProductionState.QC_FAILED,
        qc_notes=notes,
    )

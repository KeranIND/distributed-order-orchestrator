# Chanamill Made-to-Measure Order Orchestrator

A public reference implementation of the workflow I am building toward for **Chanamill personalized apparel**: take an order that depends on a FitID snapshot and garment configuration, lock the required state, route it through production and fulfillment, and capture the delivered-fit outcome back into the system.

This repository does **not** contain Chanamill production code or proprietary fit logic. It models the same operational problem class with synthetic data and public-safe contracts.

## Why this is a distributed-systems problem

A made-to-measure order is not a normal SKU checkout. It crosses multiple independently failing boundaries:

```text
FitID snapshot
    ↓
Garment configuration lock
    ↓
Payment authorization
    ↓
Production job creation
    ↓
Tailor / manufacturing assignment
    ↓
Quality control
    ↓
Freight / fulfillment
    ↓
Delivery
    ↓
Fit feedback captured
```

If one step fails, the system must know what has already happened, what can be retried safely, and what must be compensated or manually reviewed.

## State machine

```text
PENDING
   ↓
PROFILE_LOCKED
   ↓
PAYMENT_AUTHORIZED
   ↓
PRODUCTION_REQUESTED
   ↓
QC_PASSED
   ↓
FULFILLMENT_REQUESTED
   ↓
DELIVERED
   ↓
FEEDBACK_CAPTURED
   ↓
COMPLETED

Failure → COMPENSATING / REVIEW_REQUIRED / FAILED
```

## Domain concepts

- immutable FitID snapshot per order
- garment specification version
- production job
- manufacturing partner assignment
- QC result
- shipment handoff
- fit-feedback event
- idempotency key per external action
- audit history for every state transition

## Reliability concerns

- duplicate webhook/event delivery
- timeout after downstream success
- payment authorized but production rejected
- production completed but fulfillment delayed
- QC failure after manufacturing cost has already been incurred
- stale FitID changes after order placement
- retry-safe manufacturing and fulfillment commands
- manual intervention without losing workflow history

## Architecture

```text
Checkout / Order API
        ↓
Persist order + frozen FitID + garment spec
        ↓
Saga coordinator
  ├── authorize payment
  ├── create production job
  ├── record QC
  ├── request fulfillment
  └── capture delivered-fit feedback
        ↓
Outbox / event publication
        ↓
Operational systems
```

## Why orchestration

The order has ordered dependencies and irreversible physical-world steps. Explicit orchestration makes state, retries, and failure recovery visible instead of scattering control flow across loosely related consumers.

## Repository structure

```text
src/order_orchestrator/
  domain.py
  saga.py
  idempotency.py
  chanamill.py
  audit.py

tests/
  test_saga.py
  test_chanamill_order_flow.py

docs/
  architecture.md
  mtm-order-lifecycle.md
```

## Relationship to Chanamill

Chanamill's product spans measurements, fit preferences, garment specifications, manufacturing, fulfillment, and post-delivery fit feedback. This repository isolates the **workflow and reliability layer** of that system into a reviewable public implementation.

The FitID algorithms, measurement methods, production integrations, supplier details, and current private application code are intentionally excluded.
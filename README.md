# Chanamill Made-to-Measure Order Orchestrator

A public reference implementation of the workflow I am building toward for **Chanamill personalized apparel**: take an order that depends on a FitID snapshot and garment configuration, lock the required state, preserve creator attribution when present, route the order through production and QC, hand it to fulfillment, and capture the delivered-fit outcome back into the system.

This repository does **not** contain Chanamill production code or proprietary fit logic. It models the same operational problem class with synthetic data and public-safe contracts.

## Why this is a distributed-systems problem

A made-to-measure order is not a normal SKU checkout. It crosses multiple independently failing software and physical-world boundaries:

```text
FitID snapshot
    ↓
Garment configuration lock
    ↓
Creator/storefront attribution (optional)
    ↓
Payment authorization
    ↓
Production job creation
    ↓
Cutting / stitching
    ↓
Quality control
    ↓
Freight / fulfillment
    ↓
Delivery
    ↓
Fit feedback captured
```

If one step fails, the system must know what has already happened, what can be retried safely, what requires reconciliation, and what must be compensated or manually reviewed.

## Order orchestration state

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

## Physical production state

The production job has its own lifecycle because manufacturing side effects are not interchangeable with API retries:

```text
QUEUED
  ↓
CUTTING
  ↓
STITCHING
  ↓
QC_PENDING
  ├── QC_FAILED → STITCHING / rework
  └── QC_PASSED
          ↓
   READY_TO_SHIP
```

`manufacturing.py` models this state machine separately from checkout/order state.

## Creator commerce

Chanamill's creator-commerce direction should not create a separate order stack. Creator storefronts are modeled as an attribution layer over the same FitID, product, production and fulfillment systems.

`creator_commerce.py` captures:

- creator ID
- storefront ID
- attribution source
- commission policy
- eligible-order commission calculation

The attribution travels with the order snapshot so creator economics remain auditable after fulfillment.

## Fulfillment

`fulfillment.py` models the shipping boundary independently:

```text
READY
  ↓
LABEL_CREATED
  ↓
IN_TRANSIT
  ↓
DELIVERED
```

with an explicit `EXCEPTION` state for carrier/operational problems.

Delivery matters to the personalization system because it marks the point at which a physical garment can generate fit feedback.

## Domain concepts

- immutable FitID snapshot per order
- garment specification version
- creator/storefront attribution
- commission policy
- production job
- manufacturing partner assignment
- cutting/stitching lifecycle
- QC result and rework path
- shipment/tracking state
- delivered-fit feedback
- idempotency key per external action
- audit history for state transitions

## Reliability concerns

- duplicate webhook/event delivery
- timeout after downstream success
- payment authorized but production rejected
- manufacturing command acknowledged late
- accidental duplicate physical production
- QC failure after manufacturing cost is incurred
- production complete while fulfillment is delayed
- stale FitID changes after order placement
- creator attribution missing after downstream retries
- carrier exceptions
- manual intervention without losing workflow history

The most important rule is that **software retry semantics cannot be applied blindly to physical-world commands**. Before repeating a production or fulfillment instruction after a timeout, the system should reconcile whether the first instruction actually succeeded.

## Architecture

```text
Checkout / Order API
        ↓
Persist order
  + frozen FitID
  + garment spec
  + creator attribution
        ↓
Saga coordinator
  ├── authorize payment
  ├── create production job
  ├── advance manufacturing state
  ├── enforce QC gate
  ├── request fulfillment
  ├── observe delivery
  └── request fit feedback
        ↓
Outbox / integration boundary
        ↓
Manufacturing + fulfillment systems
```

## Repository structure

```text
src/order_orchestrator/
  domain.py
  saga.py
  idempotency.py
  chanamill.py
  manufacturing.py
  creator_commerce.py
  fulfillment.py

tests/
  test_saga.py
  test_chanamill_order_flow.py
  test_chanamill_operations.py

docs/
  architecture.md
  mtm-order-lifecycle.md
```

## Relationship to Chanamill

Chanamill's product spans measurements, fit preferences, garment specifications, creator-led discovery, made-to-measure manufacturing, fulfillment, and post-delivery fit feedback. This repository isolates the **workflow, physical-operations, and reliability layer** of that system into a reviewable public implementation.

The FitID algorithms, measurement methods, live supplier integrations, supplier identities, operational credentials, and current private application code are intentionally excluded.
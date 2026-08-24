# Chanamill MTM Order Architecture

## Context

Chanamill's made-to-measure order flow crosses software, payment, manufacturing, quality control, freight, fulfillment, and customer feedback. These boundaries fail independently, and some steps create physical work that cannot simply be rolled back.

## Decision

Use explicit orchestration with durable workflow state, idempotent commands, immutable order inputs, and a manual-review path.

```text
Checkout
   ↓
Persist order
   ├── FitID snapshot
   ├── garment spec version
   └── selected configuration
   ↓
Authorize payment
   ↓
Create production job
   ↓
Manufacturing
   ↓
Record QC result
   ↓
Request fulfillment
   ↓
Delivery
   ↓
Capture fit feedback
   ↓
Complete
```

## Why orchestration

This workflow has ordered dependencies and business-critical state. Production and QC are not interchangeable event consumers; they are explicit stages with different failure and compensation semantics.

## Failure classes

### Retryable technical failure
Examples: timeout, temporary API failure, duplicate delivery.

Action: retry idempotently.

### Business rejection
Examples: production cannot accept configuration, QC fails.

Action: transition to review or compensation.

### Irreversible physical progress
Examples: garment already cut or stitched.

Action: do not pretend the operation can be transactionally rolled back; preserve state and escalate according to business policy.

## Consistency model

The service should persist state and an outbox event in one transaction:

```text
DB transaction
  ├── update order/saga state
  └── append outbox record
        ↓
Publisher
        ↓
Operational integration
```

This avoids losing an external command after committing local state.

## Order-time immutability

The order references the exact FitID and garment specification versions used at checkout. Later profile or pattern changes must not rewrite the historical decision.

## Observability

Useful metrics include:
- time from order to production
- time in production
- QC failure rate
- manual-review count
- retries by integration boundary
- duplicate-command rate
- shipment latency
- delivered-fit feedback completion
- age of oldest incomplete workflow

## Public/private boundary

This repository models the architecture and reliability layer. Production integrations, partner identifiers, FitID algorithms, measurement methods, and manufacturing details remain private.
# Architecture

## Context

A commerce order crosses multiple independently failing boundaries. Inventory can be unavailable, payment can time out, fulfillment can reject a request, and any message can be delivered more than once.

A single database transaction cannot safely cover these systems.

## Decision

Use an explicit saga coordinator with durable workflow state and idempotent handlers.

```text
Order API
   ↓
Persist order + saga state
   ↓
Reserve inventory
   ↓
Authorize payment
   ↓
Request fulfillment
   ↓
Complete

Failure at an intermediate step
   ↓
Compensation in reverse dependency order
```

## Why orchestration

The core order path has a defined start, ordered steps, business-critical state, and compensation. Making the control flow explicit is easier to operate than distributing the workflow across unrelated event consumers.

## Failure model

The implementation is designed around at-least-once execution assumptions:

- duplicate commands are expected
- timeouts do not imply downstream failure
- handlers must be idempotent
- state transitions must reject impossible sequences
- compensation must itself be retry-safe

## Production persistence

The reference implementation keeps state in process. A production system would persist saga state and outbox records transactionally, then deliver commands/events asynchronously.

A common shape:

```text
DB transaction
  ├── update order/saga state
  └── append outbox event
        ↓
Outbox publisher
        ↓
Message broker
```

This avoids the dual-write problem between database state and message publication.

## Observability

Important metrics:

- saga completion latency
- retries by step
- compensation rate
- duplicate-command rate
- stuck workflow count
- downstream timeout/error rate
- age of oldest incomplete saga

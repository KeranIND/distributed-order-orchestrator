# Distributed Order Orchestrator

A reference implementation of an idempotent, event-driven order workflow using explicit saga orchestration.

The goal is to make failure modes visible. Creating an order is easy; coordinating inventory, payment, fulfillment, retries, duplicate delivery, and compensating actions is the systems problem.

## Flow

```text
POST /orders
    ↓
Order Service
    ↓ order.created
Saga Orchestrator
    ├── reserve inventory
    ├── authorize payment
    ├── request fulfillment
    └── compensate on failure
```

## Guarantees modeled

- idempotent command handling
- explicit order state transitions
- retry-safe event processing
- compensation for partially completed workflows
- duplicate-message tolerance
- deterministic saga decisions

## State machine

```text
PENDING
  ↓
INVENTORY_RESERVED
  ↓
PAYMENT_AUTHORIZED
  ↓
FULFILLMENT_REQUESTED
  ↓
COMPLETED

Any failed downstream step → COMPENSATING → FAILED
```

## Repository structure

```text
src/order_orchestrator/
  domain.py
  idempotency.py
  saga.py
tests/
  test_saga.py
docs/
  architecture.md
```

This is an original public systems-design project and contains no employer or client code.
# Business scenarios

Business scenarios validate an observable operation across several domain behaviours.
They complement unit tests; they do not replace them.

Each scenario should:

1. Start from business-readable fixture data.
2. Exercise only public APIs.
3. Assert final state, monetary balances and emitted domain events.
4. Avoid databases and web frameworks unless the scenario explicitly targets integration.
5. Remain deterministic and executable with `pytest tests/business`.

## Current scenario

`test_purchase_flow.py` represents an Amazon supplier invoice for EUR 1,210.00.
It creates the purchase, approves it, registers a partial payment, settles the balance
and verifies the complete event sequence.

Run it from `backend/`:

```bash
pytest tests/business
```

# Numera Accounting Domain v0.7 Patch

Adds the first Accounting Engine domain core.

## Copy into your current backend

```text
backend/src/numera/domain/accounting/
backend/src/numera/engines/accounting/
backend/tests/test_accounting_domain.py
backend/tests/test_accounting_engine.py
```

No database deletion required.

## Test

From `backend`:

```cmd
.venv\Scripts\activate
pytest
```

Expected result: accounting tests pass.

## Example generated journal entry

```text
Debit  600000 Purchases       309.60
Debit  472000 Input VAT        30.96
Credit 400000 Suppliers       340.56
```

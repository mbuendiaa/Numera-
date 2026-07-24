# Numera demos

Demos are short executable examples intended for product reviews and development smoke checks.
They use the public domain API and must fail loudly if the represented workflow cannot complete.

Run the first demo from `backend/`:

```bash
python demo/purchase_demo.py
```

The purchase demo creates an Amazon supplier purchase, approves it, registers two payments
and confirms that the purchase finishes paid with no outstanding balance.

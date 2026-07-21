"""Purchase domain exceptions."""


class PurchaseError(Exception):
    """Base exception for purchase business-rule violations."""


class InvalidPurchaseTransition(PurchaseError):
    """Raised when a lifecycle transition is not allowed."""


class InvalidPayment(PurchaseError):
    """Raised when a payment is non-positive or exceeds the balance."""

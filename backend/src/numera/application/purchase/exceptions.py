"""Application errors for purchase use cases."""


class PurchaseNotFoundError(LookupError):
    """Raised when a requested purchase does not exist."""

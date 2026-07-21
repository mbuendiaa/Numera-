"""Exceptions shared by Numera domain value objects."""


class DomainError(Exception):
    """Base class for errors raised by the domain layer."""


class InvalidMoneyAmountError(DomainError, ValueError):
    """Raised when a monetary amount cannot be represented safely."""


class CurrencyMismatchError(DomainError, ValueError):
    """Raised when an operation combines money in different currencies."""

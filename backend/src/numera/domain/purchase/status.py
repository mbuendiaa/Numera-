"""Purchase lifecycle states."""

from enum import Enum


class PurchaseStatus(str, Enum):
    RECEIVED = "RECEIVED"
    APPROVED = "APPROVED"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

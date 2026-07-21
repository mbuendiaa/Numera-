"""Supported ISO 4217 currencies for Numera domain models."""

from enum import Enum


class Currency(str, Enum):
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"

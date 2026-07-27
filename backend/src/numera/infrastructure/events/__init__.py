"""Synchronous domain-event infrastructure."""

from .console_logger import ConsoleEventLogger
from .event_bus import SimpleEventBus

__all__ = ["ConsoleEventLogger", "SimpleEventBus"]

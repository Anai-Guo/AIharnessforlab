"""Standard instrument driver interface.

Inspired by PyGMI (Argonne National Lab) Connect_Instrument pattern.
Every instrument driver follows this interface for consistency.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator that retries a method on failure with exponential backoff.

    Inspired by PyGMI's retry_with pattern for handling flaky GPIB connections.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            last_error = None
            wait = delay
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    logger.warning(
                        "%s failed (attempt %d/%d): %s",
                        func.__name__,
                        attempt + 1,
                        max_attempts,
                        e,
                    )
                    if attempt < max_attempts - 1:
                        time.sleep(wait)
                        wait *= backoff
            raise last_error

        return wrapper

    return decorator


@dataclass
class InstrumentDriver(ABC):
    """Base class for all instrument drivers.

    Subclass this for each instrument type. Provides:
    - Standard connect/disconnect lifecycle
    - Identity query
    - Retry-enabled VISA communication
    - Safe shutdown guarantee
    """

    resource: str  # VISA address or connection string
    timeout_ms: int = 5000
    _connected: bool = field(default=False, init=False, repr=False)
    _instrument: Any = field(default=None, init=False, repr=False)

    @abstractmethod
    def connect(self) -> None:
        """Open connection to the instrument."""
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection safely."""
        ...

    @abstractmethod
    def identity(self) -> str:
        """Query instrument identity (*IDN?)."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset instrument to defaults (*RST)."""
        ...

    @property
    def connected(self) -> bool:
        return self._connected

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()


class VisaDriver(InstrumentDriver):
    """Base driver for VISA-compatible instruments (GPIB, USB, serial).

    Provides connect/disconnect/query/write with automatic retry.
    Supports auto-reconnect on communication failure.
    """

    auto_reconnect: bool = True

    def connect(self) -> None:
        import pyvisa

        rm = pyvisa.ResourceManager()
        self._instrument = rm.open_resource(self.resource, timeout=self.timeout_ms)
        self._connected = True
        logger.info("Connected to %s", self.resource)

    def disconnect(self) -> None:
        if self._instrument:
            try:
                self._instrument.close()
            except Exception:
                pass
            self._instrument = None
        self._connected = False
        logger.info("Disconnected from %s", self.resource)

    def identity(self) -> str:
        return self.query("*IDN?")

    def reset(self) -> None:
        self.write("*RST")

    @retry(max_attempts=3, delay=0.5)
    def _query_inner(self, command: str) -> str:
        """Inner query with retry. Called by query()."""
        return self._instrument.query(command).strip()

    def query(self, command: str) -> str:
        """Send a query and return the response.

        Auto-retries on failure. If retries are exhausted and
        auto_reconnect is enabled, attempts to reconnect and retry once.
        """
        try:
            return self._query_inner(command)
        except Exception:
            if not self.auto_reconnect:
                raise
            logger.info("Retries exhausted for query, attempting reconnect to %s", self.resource)
            self.disconnect()
            self.connect()
            return self._instrument.query(command).strip()

    @retry(max_attempts=3, delay=0.5)
    def _write_inner(self, command: str) -> None:
        """Inner write with retry. Called by write()."""
        self._instrument.write(command)

    def write(self, command: str) -> None:
        """Send a command.

        Auto-retries on failure. If retries are exhausted and
        auto_reconnect is enabled, attempts to reconnect and retry once.
        """
        try:
            self._write_inner(command)
        except Exception:
            if not self.auto_reconnect:
                raise
            logger.info("Retries exhausted for write, attempting reconnect to %s", self.resource)
            self.disconnect()
            self.connect()
            self._instrument.write(command)

    def is_connected(self) -> bool:
        """Test if instrument is still responding."""
        if not self._connected or not self._instrument:
            return False
        try:
            self._instrument.query("*IDN?")
            return True
        except Exception:
            self._connected = False
            return False

    def read_float(self, command: str) -> float:
        """Query and parse as float."""
        return float(self.query(command))

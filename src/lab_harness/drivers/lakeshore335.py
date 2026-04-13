"""Lakeshore 335 Temperature Controller driver."""
from __future__ import annotations

from dataclasses import dataclass

from lab_harness.drivers.base import VisaDriver


@dataclass
class Lakeshore335(VisaDriver):
    """Lakeshore 335 temperature controller driver."""

    def read_temperature(self, channel: str = "A") -> float:
        """Read temperature in Kelvin from specified channel."""
        return self.read_float(f"KRDG? {channel}")

    def set_setpoint(self, temp_k: float, loop: int = 1) -> None:
        """Set temperature setpoint."""
        self.write(f"SETP {loop},{temp_k}")

    def set_heater_range(self, range_val: int, loop: int = 1) -> None:
        """Set heater range (0=off, 1=low, 2=medium, 3=high)."""
        self.write(f"RANGE {loop},{range_val}")

    def set_ramp(self, rate_k_per_min: float, loop: int = 1, enable: bool = True) -> None:
        """Set temperature ramp rate."""
        self.write(f"RAMP {loop},{int(enable)},{rate_k_per_min}")

    def read_heater_output(self, loop: int = 1) -> float:
        """Read heater output percentage."""
        return self.read_float(f"HTR? {loop}")

    def is_stable(self, channel: str = "A", tolerance_k: float = 0.1) -> bool:
        """Check if temperature is stable within tolerance."""
        temp = self.read_temperature(channel)
        setpoint = self.read_float("SETP? 1")
        return abs(temp - setpoint) < tolerance_k

    def shutdown(self) -> None:
        try:
            self.set_heater_range(0)
        except Exception:
            pass
        self.disconnect()

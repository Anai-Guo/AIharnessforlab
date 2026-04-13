"""Keithley 6221 AC/DC Current Source driver."""

from __future__ import annotations

from dataclasses import dataclass

from lab_harness.drivers.base import VisaDriver


@dataclass
class Keithley6221(VisaDriver):
    """Keithley 6221 current source with delta mode support."""

    def set_current(self, amps: float) -> None:
        self.write(f"CURR {amps}")

    def enable_output(self) -> None:
        self.write("OUTP ON")

    def disable_output(self) -> None:
        self.write("CURR 0")
        self.write("OUTP OFF")

    def configure_delta(self, high_current: float, delay: float = 0.002) -> None:
        """Configure delta mode (paired with K2182A nanovoltmeter)."""
        self.write(f"SOUR:DELT:HIGH {high_current}")
        self.write(f"SOUR:DELT:DEL {delay}")

    def arm_delta(self) -> None:
        self.write("SOUR:DELT:ARM")

    def start_delta(self) -> None:
        self.write("INIT:IMM")

    def abort_delta(self) -> None:
        self.write("SOUR:SWE:ABOR")

    def read_delta(self) -> float:
        """Read latest delta mode measurement."""
        return float(self.query(":SENS:DATA:FRESH?").split(",")[0])

    def shutdown(self) -> None:
        try:
            self.disable_output()
        except Exception:
            pass
        self.disconnect()

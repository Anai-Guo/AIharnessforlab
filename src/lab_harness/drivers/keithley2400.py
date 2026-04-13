"""Keithley 2400 SourceMeter driver."""
from __future__ import annotations

from dataclasses import dataclass

from lab_harness.drivers.base import VisaDriver


@dataclass
class Keithley2400(VisaDriver):
    """Keithley 2400 series SourceMeter driver.

    Supports current sourcing with voltage measurement (most common mode
    for transport measurements).
    """

    compliance_v: float = 20.0

    def configure_source_current(self, compliance_v: float | None = None) -> None:
        """Set up as current source with voltage compliance."""
        self.write(":SOUR:FUNC CURR")
        self.write(":SOUR:CURR:RANG:AUTO ON")
        self.write(":SENS:FUNC 'VOLT'")
        self.write(":SENS:VOLT:RANG:AUTO ON")
        self.write(f":SENS:VOLT:PROT {compliance_v or self.compliance_v}")
        self.write(":FORM:ELEM VOLT,CURR")

    def set_current(self, amps: float) -> None:
        """Set source current in amps."""
        self.write(f":SOUR:CURR {amps}")

    def enable_output(self) -> None:
        self.write(":OUTP ON")

    def disable_output(self) -> None:
        self.write(":SOUR:CURR 0")
        self.write(":OUTP OFF")

    def measure_voltage(self) -> float:
        """Trigger measurement and return voltage."""
        response = self.query(":READ?")
        parts = response.split(",")
        return float(parts[0])  # First element is voltage

    def measure_iv(self) -> tuple[float, float]:
        """Return (voltage, current) tuple."""
        response = self.query(":READ?")
        parts = response.split(",")
        return float(parts[0]), float(parts[1])

    def shutdown(self) -> None:
        """Safe shutdown: zero current, disable output, disconnect."""
        try:
            self.disable_output()
        except Exception:
            pass
        self.disconnect()

"""Shared fixtures for lab_harness tests."""

from __future__ import annotations

import pytest

from lab_harness.models.instrument import InstrumentBus, InstrumentRecord, LabInventory
from lab_harness.models.measurement import (
    DataChannel,
    MeasurementPlan,
    MeasurementType,
    SweepAxis,
)
from lab_harness.models.safety import SafetyPolicy


@pytest.fixture()
def sample_instruments() -> list[InstrumentRecord]:
    """Five typical lab instruments."""
    return [
        InstrumentRecord(
            resource="GPIB0::5::INSTR",
            vendor="KEITHLEY INSTRUMENTS INC.",
            model="MODEL 2400",
            serial="1234567",
            bus=InstrumentBus.GPIB,
        ),
        InstrumentRecord(
            resource="GPIB0::2::INSTR",
            vendor="KEITHLEY INSTRUMENTS INC.",
            model="MODEL 2000",
            serial="2000001",
            bus=InstrumentBus.GPIB,
        ),
        InstrumentRecord(
            resource="GPIB0::3::INSTR",
            vendor="KEITHLEY INSTRUMENTS INC.",
            model="MODEL 2000",
            serial="2000002",
            bus=InstrumentBus.GPIB,
        ),
        InstrumentRecord(
            resource="COM3",
            vendor="LAKESHORE",
            model="MODEL 425",
            serial="LS0001",
            bus=InstrumentBus.SERIAL,
        ),
        InstrumentRecord(
            resource="GPIB0::12::INSTR",
            vendor="KEITHLEY INSTRUMENTS INC.",
            model="MODEL 6221",
            serial="6221001",
            bus=InstrumentBus.GPIB,
        ),
    ]


@pytest.fixture()
def sample_inventory(sample_instruments: list[InstrumentRecord]) -> LabInventory:
    """LabInventory wrapping the five sample instruments."""
    return LabInventory(instruments=sample_instruments)


@pytest.fixture()
def sample_ahe_plan() -> MeasurementPlan:
    """A standard AHE measurement plan."""
    return MeasurementPlan(
        measurement_type=MeasurementType.AHE,
        name="Test AHE",
        description="Hall effect sweep",
        x_axis=SweepAxis(
            label="Magnetic Field",
            unit="Oe",
            start=-5000,
            stop=5000,
            step=50,
            role="magnet",
        ),
        y_channels=[
            DataChannel(label="V_xy", unit="V", role="dmm"),
            DataChannel(label="V_xx", unit="V", role="dmm_secondary"),
        ],
        max_current_a=0.0001,
        max_field_oe=10000.0,
        max_temperature_k=300.0,
        num_averages=3,
    )


@pytest.fixture()
def default_safety_policy() -> SafetyPolicy:
    """Default safety policy with factory values."""
    return SafetyPolicy()

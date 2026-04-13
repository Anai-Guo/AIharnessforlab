"""Tests for driver base classes and registry."""
from unittest.mock import MagicMock, patch
from lab_harness.drivers.base import retry, InstrumentDriver, VisaDriver
from lab_harness.drivers.registry import DriverRegistry

def test_retry_succeeds_first_try():
    @retry(max_attempts=3, delay=0.01)
    def ok():
        return "success"
    assert ok() == "success"

def test_retry_succeeds_after_failure():
    call_count = 0
    @retry(max_attempts=3, delay=0.01)
    def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("flaky")
        return "ok"
    assert flaky() == "ok"
    assert call_count == 3

def test_retry_exhausted():
    @retry(max_attempts=2, delay=0.01)
    def always_fail():
        raise ConnectionError("down")
    try:
        always_fail()
        assert False, "should have raised"
    except ConnectionError:
        pass

def test_registry_from_yaml(tmp_path):
    config = tmp_path / "instruments.yaml"
    config.write_text("""
instruments:
  source_meter:
    driver: keithley2400
    resource: "GPIB0::5::INSTR"
    settings:
      compliance_v: 10.0
""")
    reg = DriverRegistry.from_yaml(config)
    assert "source_meter" in reg.list_roles()

def test_registry_unknown_driver(tmp_path):
    config = tmp_path / "instruments.yaml"
    config.write_text("""
instruments:
  unknown:
    driver: nonexistent_driver
    resource: "GPIB0::1::INSTR"
""")
    reg = DriverRegistry.from_yaml(config)
    try:
        reg.get_driver("unknown")
        assert False
    except ValueError as e:
        assert "nonexistent_driver" in str(e)

def test_registry_missing_role():
    reg = DriverRegistry(configs={})
    try:
        reg.get_driver("nonexistent")
        assert False
    except KeyError:
        pass

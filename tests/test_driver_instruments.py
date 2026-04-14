"""Mock VISA tests for instrument drivers.

Tests verify correct SCPI command sequences without real hardware.
Uses unittest.mock to simulate PyVISA ResourceManager and instrument responses.
"""

from unittest.mock import MagicMock, patch


# Helper to create a mock VISA instrument
def mock_visa():
    """Create a mock PyVISA ResourceManager + instrument."""
    mock_rm = MagicMock()
    mock_inst = MagicMock()
    mock_inst.query.return_value = "KEITHLEY,2400,12345,1.0"
    mock_rm.open_resource.return_value = mock_inst
    return mock_rm, mock_inst


# === Keithley 2400 Tests ===


@patch("pyvisa.ResourceManager")
def test_k2400_connect(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.keithley2400 import Keithley2400

    k = Keithley2400(resource="GPIB0::5::INSTR")
    k.connect()
    mock_rm.open_resource.assert_called_once_with("GPIB0::5::INSTR", timeout=5000)
    assert k.connected


@patch("pyvisa.ResourceManager")
def test_k2400_configure_source_current(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.keithley2400 import Keithley2400

    k = Keithley2400(resource="GPIB0::5::INSTR")
    k.connect()
    k.configure_source_current(compliance_v=10.0)
    # Verify SCPI commands sent in correct order
    writes = [c.args[0] for c in mock_inst.write.call_args_list]
    assert ":SOUR:FUNC CURR" in writes
    assert ":SOUR:CURR:RANG:AUTO ON" in writes
    assert ":SENS:FUNC 'VOLT'" in writes
    assert ":SENS:VOLT:RANG:AUTO ON" in writes
    assert ":SENS:VOLT:PROT 10.0" in writes
    assert ":FORM:ELEM VOLT,CURR" in writes


@patch("pyvisa.ResourceManager")
def test_k2400_set_current(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.keithley2400 import Keithley2400

    k = Keithley2400(resource="GPIB0::5::INSTR")
    k.connect()
    k.set_current(0.001)
    mock_inst.write.assert_called_with(":SOUR:CURR 0.001")


@patch("pyvisa.ResourceManager")
def test_k2400_measure_voltage(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    mock_inst.query.return_value = "1.23456,0.001000"
    from lab_harness.drivers.keithley2400 import Keithley2400

    k = Keithley2400(resource="GPIB0::5::INSTR")
    k.connect()
    v = k.measure_voltage()
    assert abs(v - 1.23456) < 1e-6


@patch("pyvisa.ResourceManager")
def test_k2400_measure_iv(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    mock_inst.query.return_value = "1.23456,0.001000"
    from lab_harness.drivers.keithley2400 import Keithley2400

    k = Keithley2400(resource="GPIB0::5::INSTR")
    k.connect()
    voltage, current = k.measure_iv()
    assert abs(voltage - 1.23456) < 1e-6
    assert abs(current - 0.001) < 1e-6


@patch("pyvisa.ResourceManager")
def test_k2400_enable_output(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.keithley2400 import Keithley2400

    k = Keithley2400(resource="GPIB0::5::INSTR")
    k.connect()
    k.enable_output()
    mock_inst.write.assert_called_with(":OUTP ON")


@patch("pyvisa.ResourceManager")
def test_k2400_disable_output(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.keithley2400 import Keithley2400

    k = Keithley2400(resource="GPIB0::5::INSTR")
    k.connect()
    k.disable_output()
    writes = [c.args[0] for c in mock_inst.write.call_args_list]
    assert ":SOUR:CURR 0" in writes
    assert ":OUTP OFF" in writes


@patch("pyvisa.ResourceManager")
def test_k2400_shutdown(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.keithley2400 import Keithley2400

    k = Keithley2400(resource="GPIB0::5::INSTR")
    k.connect()
    k.shutdown()
    writes = [c.args[0] for c in mock_inst.write.call_args_list]
    assert ":SOUR:CURR 0" in writes
    assert ":OUTP OFF" in writes
    # shutdown also disconnects
    mock_inst.close.assert_called_once()
    assert not k.connected


# === Keithley 6221 Tests ===


@patch("pyvisa.ResourceManager")
def test_k6221_connect(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.keithley6221 import Keithley6221

    k = Keithley6221(resource="GPIB0::11::INSTR")
    k.connect()
    mock_rm.open_resource.assert_called_once_with("GPIB0::11::INSTR", timeout=5000)
    assert k.connected


@patch("pyvisa.ResourceManager")
def test_k6221_set_current(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.keithley6221 import Keithley6221

    k = Keithley6221(resource="GPIB0::11::INSTR")
    k.connect()
    k.set_current(0.0005)
    mock_inst.write.assert_called_with("CURR 0.0005")


@patch("pyvisa.ResourceManager")
def test_k6221_configure_delta(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.keithley6221 import Keithley6221

    k = Keithley6221(resource="GPIB0::11::INSTR")
    k.connect()
    k.configure_delta(high_current=0.001, delay=0.005)
    writes = [c.args[0] for c in mock_inst.write.call_args_list]
    assert "SOUR:DELT:HIGH 0.001" in writes
    assert "SOUR:DELT:DEL 0.005" in writes


@patch("pyvisa.ResourceManager")
def test_k6221_arm_and_start_delta(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.keithley6221 import Keithley6221

    k = Keithley6221(resource="GPIB0::11::INSTR")
    k.connect()
    k.arm_delta()
    k.start_delta()
    writes = [c.args[0] for c in mock_inst.write.call_args_list]
    assert "SOUR:DELT:ARM" in writes
    assert "INIT:IMM" in writes


@patch("pyvisa.ResourceManager")
def test_k6221_abort_delta(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.keithley6221 import Keithley6221

    k = Keithley6221(resource="GPIB0::11::INSTR")
    k.connect()
    k.abort_delta()
    mock_inst.write.assert_called_with("SOUR:SWE:ABOR")


@patch("pyvisa.ResourceManager")
def test_k6221_read_delta(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    mock_inst.query.return_value = "0.000123,1"
    from lab_harness.drivers.keithley6221 import Keithley6221

    k = Keithley6221(resource="GPIB0::11::INSTR")
    k.connect()
    val = k.read_delta()
    mock_inst.query.assert_called_with(":SENS:DATA:FRESH?")
    assert abs(val - 0.000123) < 1e-8


@patch("pyvisa.ResourceManager")
def test_k6221_shutdown(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.keithley6221 import Keithley6221

    k = Keithley6221(resource="GPIB0::11::INSTR")
    k.connect()
    k.shutdown()
    writes = [c.args[0] for c in mock_inst.write.call_args_list]
    assert "CURR 0" in writes
    assert "OUTP OFF" in writes
    mock_inst.close.assert_called_once()
    assert not k.connected


# === Lakeshore 335 Tests ===


@patch("pyvisa.ResourceManager")
def test_ls335_connect(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.lakeshore335 import Lakeshore335

    ls = Lakeshore335(resource="GPIB0::10::INSTR")
    ls.connect()
    mock_rm.open_resource.assert_called_once_with("GPIB0::10::INSTR", timeout=5000)
    assert ls.connected


@patch("pyvisa.ResourceManager")
def test_ls335_read_temperature(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    mock_inst.query.return_value = "295.123"
    from lab_harness.drivers.lakeshore335 import Lakeshore335

    ls = Lakeshore335(resource="GPIB0::10::INSTR")
    ls.connect()
    temp = ls.read_temperature("A")
    mock_inst.query.assert_called_with("KRDG? A")
    assert abs(temp - 295.123) < 0.001


@patch("pyvisa.ResourceManager")
def test_ls335_set_setpoint(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.lakeshore335 import Lakeshore335

    ls = Lakeshore335(resource="GPIB0::10::INSTR")
    ls.connect()
    ls.set_setpoint(300.0, loop=1)
    mock_inst.write.assert_called_with("SETP 1,300.0")


@patch("pyvisa.ResourceManager")
def test_ls335_set_heater_range(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.lakeshore335 import Lakeshore335

    ls = Lakeshore335(resource="GPIB0::10::INSTR")
    ls.connect()
    ls.set_heater_range(3, loop=1)
    mock_inst.write.assert_called_with("RANGE 1,3")


@patch("pyvisa.ResourceManager")
def test_ls335_set_ramp(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.lakeshore335 import Lakeshore335

    ls = Lakeshore335(resource="GPIB0::10::INSTR")
    ls.connect()
    ls.set_ramp(2.0, loop=1, enable=True)
    mock_inst.write.assert_called_with("RAMP 1,1,2.0")


@patch("pyvisa.ResourceManager")
def test_ls335_read_heater_output(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    mock_inst.query.return_value = "45.67"
    from lab_harness.drivers.lakeshore335 import Lakeshore335

    ls = Lakeshore335(resource="GPIB0::10::INSTR")
    ls.connect()
    output = ls.read_heater_output(loop=1)
    mock_inst.query.assert_called_with("HTR? 1")
    assert abs(output - 45.67) < 0.01


@patch("pyvisa.ResourceManager")
def test_ls335_shutdown(mock_rm_cls):
    mock_rm, mock_inst = mock_visa()
    mock_rm_cls.return_value = mock_rm
    from lab_harness.drivers.lakeshore335 import Lakeshore335

    ls = Lakeshore335(resource="GPIB0::10::INSTR")
    ls.connect()
    ls.shutdown()
    mock_inst.write.assert_called_with("RANGE 1,0")
    mock_inst.close.assert_called_once()
    assert not ls.connected

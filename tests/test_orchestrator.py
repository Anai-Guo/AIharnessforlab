"""Tests for orchestrator flow."""

from lab_harness.orchestrator.decider import _rule_based_decision
from lab_harness.orchestrator.folder import prepare_data_folder
from lab_harness.orchestrator.session import ExperimentSession


def test_session_folder_name():
    s = ExperimentSession()
    s.material = "Si wafer"
    s.measurement_type = "IV"
    name = s.folder_name
    assert "Si_wafer" in name
    assert "IV" in name


def test_session_slug_special_chars():
    s = ExperimentSession()
    s.material = "Fe/MgO heterostructure"
    s.measurement_type = "AHE"
    name = s.folder_name
    assert "AHE" in name
    assert "/" not in name


def test_prepare_data_folder(tmp_path):
    folder = prepare_data_folder(tmp_path, "test_folder")
    assert folder.exists()
    assert folder.is_dir()


def test_session_save_summary(tmp_path):
    s = ExperimentSession()
    s.direction = "transport"
    s.material = "Si"
    s.measurement_type = "IV"
    s.instruments = [{"vendor": "KEITHLEY", "model": "2400", "resource": "GPIB0::5"}]
    s.save_summary(tmp_path)
    assert (tmp_path / "experiment_summary.json").exists()
    assert (tmp_path / "README.md").exists()
    content = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "Si" in content
    assert "IV" in content


def test_rule_based_decision_hall():
    instruments = [
        {"vendor": "KEITHLEY", "model": "2400"},
        {"vendor": "LAKESHORE", "model": "425"},
    ]
    decision = _rule_based_decision("transport", "silicon", instruments)
    assert decision["measurement_type"] in ("HALL", "AHE")


def test_rule_based_decision_default_iv():
    instruments = [{"vendor": "KEITHLEY", "model": "2400"}]
    decision = _rule_based_decision("general", "sample", instruments)
    assert decision["measurement_type"] == "IV"


def test_rule_based_decision_magnetic_ahe():
    instruments = [
        {"vendor": "KEITHLEY", "model": "2400"},
        {"vendor": "LAKESHORE", "model": "425"},
    ]
    decision = _rule_based_decision("magnetic films", "CoFeB ferromagnet", instruments)
    assert decision["measurement_type"] == "AHE"

"""Driver registry: discovers and instantiates instrument drivers from config.

Inspired by PyGMI's configuration-driven instrument initialization.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from lab_harness.drivers.base import InstrumentDriver

logger = logging.getLogger(__name__)

# Map driver names to classes (lazy imports)
DRIVER_MAP: dict[str, str] = {
    "keithley2400": "lab_harness.drivers.keithley2400:Keithley2400",
    "keithley6221": "lab_harness.drivers.keithley6221:Keithley6221",
    "lakeshore335": "lab_harness.drivers.lakeshore335:Lakeshore335",
}


def _import_driver(driver_spec: str) -> type[InstrumentDriver]:
    """Import a driver class from a 'module:ClassName' spec."""
    module_path, class_name = driver_spec.rsplit(":", 1)
    import importlib

    module = importlib.import_module(module_path)
    return getattr(module, class_name)


@dataclass
class DriverRegistry:
    """Registry of configured instrument drivers.

    Loads instrument configurations from YAML and provides
    lazy instantiation of driver objects.
    """

    configs: dict[str, dict] = field(default_factory=dict)
    _instances: dict[str, InstrumentDriver] = field(default_factory=dict, init=False)

    @classmethod
    def from_yaml(cls, path: Path) -> DriverRegistry:
        """Load instrument config from YAML file."""
        with open(path) as f:
            raw = yaml.safe_load(f) or {}
        instruments = raw.get("instruments", {})
        return cls(configs=instruments)

    def get_driver(self, role: str) -> InstrumentDriver:
        """Get or create a driver instance for the given role."""
        if role in self._instances:
            return self._instances[role]

        if role not in self.configs:
            raise KeyError(f"No instrument configured for role '{role}'")

        config = self.configs[role]
        driver_name = config["driver"]
        resource = config["resource"]
        settings = config.get("settings", {})

        if driver_name not in DRIVER_MAP:
            raise ValueError(f"Unknown driver '{driver_name}'. Available: {list(DRIVER_MAP.keys())}")

        driver_cls = _import_driver(DRIVER_MAP[driver_name])
        instance = driver_cls(resource=resource, **settings)
        self._instances[role] = instance
        logger.info("Created %s driver for role '%s' at %s", driver_name, role, resource)
        return instance

    def connect_all(self) -> dict[str, InstrumentDriver]:
        """Connect all configured instruments."""
        connected = {}
        for role in self.configs:
            try:
                driver = self.get_driver(role)
                driver.connect()
                connected[role] = driver
            except Exception as e:
                logger.error("Failed to connect %s: %s", role, e)
        return connected

    def disconnect_all(self) -> None:
        """Safely disconnect all instruments."""
        for role, driver in self._instances.items():
            try:
                driver.disconnect()
            except Exception as e:
                logger.warning("Error disconnecting %s: %s", role, e)
        self._instances.clear()

    def list_roles(self) -> list[str]:
        """List all configured instrument roles."""
        return list(self.configs.keys())

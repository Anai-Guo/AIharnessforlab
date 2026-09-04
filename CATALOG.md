# LabAgent - Catalog

## Measurement Templates

Templates define what to measure. Located in `src/lab_harness/planning/templates/`.
46 templates: 45 across the 9 disciplines below plus one general-purpose custom sweep.
The Instruments column lists the instrument roles referenced by each template's
sweep axis and data channels.

### Electrical Characterization (7)
| Template | Description | Instruments |
|----------|-------------|-------------|
| `iv.yaml` | Sweep source current and measure voltage | Source meter |
| `rt.yaml` | Measure resistance as a function of temperature | Temp controller + DMM |
| `delta.yaml` | Sweep DC current and measure nanovoltage for ultra-low resistance samples | AC/pulse current source + Nanovoltmeter |
| `high_r.yaml` | Sweep voltage and measure picoamp current for high-resistance samples | Electrometer |
| `transfer.yaml` | Sweep gate voltage and measure drain current for transistor characterization | Source meter (gate) + Source meter (drain) |
| `output.yaml` | Sweep drain voltage at fixed gate voltage for transistor output characterization | Source meter (drain) + Source meter (gate) |
| `breakdown.yaml` | Ramp voltage until dielectric breakdown, monitoring leakage current | Electrometer |

### Magnetic Measurements (condensed-matter) (8)
| Template | Description | Instruments |
|----------|-------------|-------------|
| `hall.yaml` | Sweep magnetic field and measure Hall voltage for carrier density and mobility | Magnet + DMM + DMM (secondary) |
| `mr.yaml` | Sweep magnetic field and measure longitudinal resistance | Magnet + DMM |
| `ahe.yaml` | Sweep magnetic field and measure transverse Hall resistance | Magnet + DMM + DMM (secondary) |
| `sot.yaml` | Sweep field at each pulse current to measure current-induced switching | Magnet + DMM + AC/pulse current source |
| `fmr.yaml` | Sweep magnetic field and measure microwave absorption for FMR spectroscopy | Magnet + Lock-in amplifier |
| `hysteresis.yaml` | Sweep magnetic field and measure magnetization (M-H loop via VSM/SQUID) | Magnet + Magnetometer (VSM/SQUID) |
| `magnetostriction.yaml` | Magnetic field sweep, measure strain or length change | Magnet + Strain gauge + Gaussmeter |
| `nernst.yaml` | Magnetic field sweep, measure transverse thermoelectric voltage | Magnet + Nanovoltmeter + Temp controller |

### Thermoelectric (2)
| Template | Description | Instruments |
|----------|-------------|-------------|
| `seebeck.yaml` | Sweep temperature gradient and measure Seebeck voltage | Temp controller + Nanovoltmeter + Temp controller (secondary) |
| `thermal_conductivity.yaml` | Sweep heater power and measure temperature difference for thermal conductivity | Source meter + Temp controller + Temp controller (secondary) |

### Superconductivity (2)
| Template | Description | Instruments |
|----------|-------------|-------------|
| `tc.yaml` | Sweep temperature and measure resistance to find superconducting Tc | Temp controller + DMM + Nanovoltmeter |
| `jc.yaml` | Sweep current at fixed temperature and field to determine critical current Ic | Source meter + Nanovoltmeter + Temp controller |

### Electrochemistry (4)
| Template | Description | Instruments |
|----------|-------------|-------------|
| `cyclic_voltammetry.yaml` | Triangle wave voltage sweep, measure current for redox reaction analysis | Potentiostat |
| `eis.yaml` | Frequency sweep at fixed DC bias, measure complex impedance (Z real/imaginary) | Impedance analyzer |
| `chronoamperometry.yaml` | Step voltage and measure current vs time for diffusion studies | Potentiostat |
| `potentiometry.yaml` | Measure open circuit potential vs time for corrosion or battery studies | Electrometer |

### Dielectric & Ferroelectric (4)
| Template | Description | Instruments |
|----------|-------------|-------------|
| `cv.yaml` | Capacitance-Voltage characterization at multiple frequencies | LCR meter |
| `pe_loop.yaml` | Sweep electric field and measure polarization for ferroelectric P-E loop | HV amplifier + Ferroelectric tester |
| `pyroelectric.yaml` | Ramp temperature and measure pyroelectric current for Curie temperature determination | Temp controller + Electrometer |
| `capacitance_frequency.yaml` | Frequency sweep at fixed DC bias, measure capacitance for trap analysis | LCR meter |

### Semiconductor & Optoelectronics (5)
| Template | Description | Instruments |
|----------|-------------|-------------|
| `photo_iv.yaml` | Solar cell IV curve under illumination, extract power characteristics | Source meter |
| `dlts.yaml` | Temperature sweep, measure capacitance transients for deep trap characterization | Temp controller + LCR meter |
| `photocurrent.yaml` | Sweep illumination wavelength and measure photocurrent for spectral response | Monochromator + Source meter |
| `photoresponse.yaml` | Measure photocurrent vs time under pulsed illumination for response dynamics | Source meter |
| `tunneling.yaml` | Voltage sweep, measure differential conductance dI/dV for tunnel junction analysis | Source meter + Lock-in amplifier |

### Sensors, Materials & Environmental (7)
| Template | Description | Instruments |
|----------|-------------|-------------|
| `gas_sensor.yaml` | Gas concentration sweep, measure resistance change for sensor characterization | Gas controller + DMM |
| `humidity_response.yaml` | Humidity sweep, measure resistance or capacitance change of sensor | Humidity chamber + DMM + LCR meter |
| `impedance_biosensor.yaml` | Impedance vs analyte concentration for biosensor calibration curves | Impedance analyzer |
| `cell_counting.yaml` | Voltage pulse detection and event counting for particle/cell sizing | Source meter |
| `ph_calibration.yaml` | pH buffer sweep, measure electrode voltage for calibration curve | pH meter + Electrometer |
| `strain_gauge.yaml` | Strain sweep, measure resistance change for piezoresistive characterization | Strain controller + DMM |
| `fatigue.yaml` | Cyclic stress loading, measure resistance degradation over cycles | Strain controller + DMM + Load cell |

### Quantum Design PPMS/MPMS (6)
| Template | Description | Instruments |
|----------|-------------|-------------|
| `ppms_rt.yaml` | Four-probe resistance measurement as a function of temperature using Quantum Design PPMS | PPMS (MultiPyVu) |
| `ppms_mr.yaml` | Field-dependent resistance measurement at fixed temperature using Quantum Design PPMS | PPMS (MultiPyVu) |
| `ppms_hall.yaml` | Hall resistance vs field for carrier density and mobility using PPMS | PPMS (MultiPyVu) |
| `ppms_hc.yaml` | Specific heat measurement as a function of temperature using PPMS relaxation method | PPMS (MultiPyVu) |
| `mpms_mh.yaml` | DC magnetization measurement as a function of applied field using Quantum Design MPMS/SQUID | MPMS (MultiPyVu) |
| `mpms_mt.yaml` | Zero-field-cooled and field-cooled magnetization vs temperature using MPMS | MPMS (MultiPyVu) |

### General Purpose (1)
| Template | Description | Instruments |
|----------|-------------|-------------|
| `custom_sweep.yaml` | Generic X-Y sweep measurement with user-defined axes and channels | Source meter + DMM (defaults, user-configurable) |

---

## Instrument Reference Procedures

Command sequences (SCPI, ASCII-line, or vendor-API) for common instruments. Located
in `src/lab_harness/reference/instrument_procedures.py`. Currently 33 procedures
spanning electrical, signals/RF, optics, electrochemistry, biology/analytical,
gas/flow, and cryogenic instruments.

### Electrical / source-measure / DMM
| Procedure | Instruments | Use Case |
|-----------|------------|----------|
| `IV_K2400` | Keithley 2400 | Standard IV curve |
| `DELTA_K6221` | K6221 + K2182A | Ultra-low resistance |
| `HIGH_R_K6517B` | Keithley 6517B | High impedance materials |
| `NANOVOLT_K2182A` | Keithley 2182A | Low-noise voltage |
| `DMM_K2000` | Keithley 2000 | General voltage/resistance |
| `DMM_A34401` | Agilent 34401A / Keysight 34461A | General purpose DMM |

### Signals / RF / waveform
| Procedure | Instruments | Use Case |
|-----------|------------|----------|
| `SCOPE_CAPTURE_TEK` | Tektronix TDS/DPO/MSO | Waveform capture |
| `SCOPE_CAPTURE_KEYSIGHT` | Keysight DSOX/MSOX | Waveform capture |
| `FGEN_KEYSIGHT` | Keysight 33500B/33622A | Arbitrary waveform output |
| `PSU_KEYSIGHT_E36300` | Keysight E36313A | Programmable DC supply |
| `LOCKIN_SR830` | SRS SR830 | AC / small-signal detection |
| `LOCKIN_SR860` | SRS SR860/SR865A | AC / small-signal detection (SCPI) |
| `LOCKIN_ZURICH_MFLI` | Zurich Instruments MFLI | High-end lock-in via zhinst-toolkit |

### Optics / photonics / spectroscopy
| Procedure | Instruments | Use Case |
|-----------|------------|----------|
| `OPTICAL_POWER_PM100D` | Thorlabs PM100D / PM400 | Optical power at wavelength |
| `UV_VIS_OCEAN_INSIGHT` | Ocean Insight USB2000/QEPro | UV-Vis absorbance spectrum |

### Electrochemistry
| Procedure | Instruments | Use Case |
|-----------|------------|----------|
| `CV_E4980A` | Keysight E4980A | Capacitance characterization |
| `CV_BIOLOGIC` | BioLogic SP-200/VSP/VMP3 | Cyclic voltammetry via easy-biologic |
| `CV_GAMRY` | Gamry Reference 600+/Interface 1010B | CV via COM/ActiveX |
| `CV_CHI` | CH Instruments CHI760E/CHI660E | CV via hardpotato macro driver |

### Gas / flow / pressure
| Procedure | Instruments | Use Case |
|-----------|------------|----------|
| `GAS_FLOW_ALICAT` | Alicat MC-series MFC | Gas flow setpoint |

### Analytical / biology
| Procedure | Instruments | Use Case |
|-----------|------------|----------|
| `WEIGH_METTLER` | Mettler Toledo XS/XP | Stable mass readout (MT-SICS) |
| `WEIGH_OHAUS` | Ohaus Adventurer | Mass readout over RS-232 |
| `PH_ORION` | Thermo Orion Star A221 | pH / ISE / mV readout |

### Temperature / cryogenic
| Procedure | Instruments | Use Case |
|-----------|------------|----------|
| `RT_LS350` | Lakeshore 350 | Temperature-dependent measurements |
| `TEMP_OXFORD_ITC` | Oxford Mercury iTC | Cryostat temperature control |

### DAQ
| Procedure | Instruments | Use Case |
|-----------|------------|----------|
| `DAQ_NI_AO` | NI USB-6351/6001/6009 | Analog voltage output |
| `DAQ_NI_AI` | NI USB-6351/6001/6009 | Analog voltage input |

### Condensed-matter specialty (Quantum Design)
| Procedure | Instruments | Use Case |
|-----------|------------|----------|
| `PPMS_RT` | QD PPMS (MultiPyVu) | R-T measurement |
| `PPMS_MR` | QD PPMS (MultiPyVu) | Magnetoresistance |
| `PPMS_HALL` | QD PPMS (MultiPyVu) | Hall effect |
| `PPMS_HC` | QD PPMS (MultiPyVu) | Heat capacity |
| `MPMS_MH` | QD MPMS (MultiPyVu) | M-H loop (SQUID) |
| `MPMS_MT` | QD MPMS (MultiPyVu) | M-T ZFC/FC |

**Can't find your instrument?** Call the `manual_lookup` MCP tool (or
`labharness`'s AI chat) with the make and model — it will return the
manufacturer's programming manual URL plus any open-source Python driver it
knows about, before writing new command sequences.

---

## How to Contribute

### Add a New Measurement Template
1. Create a YAML file in `src/lab_harness/planning/templates/`
2. Follow the format of existing templates (see `iv.yaml` for reference)
3. Add the measurement type to `MeasurementType` enum in `src/lab_harness/models/measurement.py`
4. Add required roles to `MEASUREMENT_ROLES` in `src/lab_harness/discovery/classifier.py`
5. Submit a pull request

### Add an Instrument Driver Reference
1. Add SCPI sequences to `src/lab_harness/reference/instrument_procedures.py`
2. Include init, measure, and shutdown sequences
3. Document default parameters
4. Submit a pull request

### Add an Analysis Template
1. Create a Python script in `src/lab_harness/analysis/templates/`
2. Use `{{DATA_PATH}}` and `{{OUTPUT_DIR}}` placeholders
3. Save figures as PNG (300 dpi) and PDF
4. Submit a pull request

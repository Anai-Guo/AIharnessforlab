---
name: R-T Measurement
description: Resistance vs temperature measurement for phase transitions and TCR characterization
measurement_type: RT
instruments: [source_meter, dmm, temperature_controller]
version: "1.0"
---

## Protocol

1. **Connect** instruments and verify identity via *IDN?
2. **Configure** source meter: DC current mode, set compliance voltage to {compliance} V
3. **Set** excitation current to {current} A (small enough to avoid self-heating)
4. **Configure** temperature controller: set ramp rate to {ramp_rate} K/min
5. **Ramp** temperature from {t_start} K to {t_stop} K:
   - At each temperature point (step = {t_step} K or continuous logging):
     a. Wait for temperature stabilization (within {t_tolerance} K for {dwell_time} s)
     b. Read actual temperature from sensor
     c. Measure voltage across sample (4-wire preferred)
     d. Calculate R = V / I
     e. Record timestamp, T, V, I, R
6. **Optional**: Cool-down sweep for hysteresis detection
7. **Disable** source output
8. **Set** temperature controller to safe standby temperature
9. **Save** data to {output_dir} as CSV

## Expected Output

- R vs T curve (warming and optional cooling)
- TCR = (1/R) * dR/dT at specified temperature
- Transition temperature T_c (if applicable, from dR/dT peak)
- Residual resistance ratio RRR = R(300K) / R(base)
- Activation energy E_a from Arrhenius fit (if semiconducting)

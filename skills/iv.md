---
name: IV Curve Measurement
description: Current-voltage characteristic measurement for devices and junctions
measurement_type: IV
instruments: [source_meter, dmm]
version: "1.0"
---

## Protocol

1. **Connect** instruments and verify identity via *IDN?
2. **Configure** source meter: voltage source mode, set compliance current to {compliance} A
3. **Set** measurement speed/integration time (NPLC = {nplc}, typical: 1-10)
4. **Sweep** voltage from {v_start} V to {v_stop} V in {v_step} V steps:
   - At each voltage point:
     a. Set source voltage
     b. Wait {settling_time} s for stabilization
     c. Measure current (average {num_averages} readings)
     d. Record voltage readback and current
5. **Optional**: Reverse sweep from {v_stop} to {v_start} for hysteresis check
6. **Optional**: Repeat sweep at different temperatures for T-dependent IV
7. **Disable** source meter output
8. **Save** data to {output_dir} as CSV

## Expected Output

- I vs V curve (forward and optional reverse)
- Differential conductance dI/dV vs V
- For diodes: ideality factor n, series resistance R_s, saturation current I_0
- For resistors: resistance R from linear fit slope
- For tunneling junctions: barrier height from Simmons/Brinkman fit

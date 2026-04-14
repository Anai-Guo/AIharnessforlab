---
name: Magnetoresistance Measurement
description: Magnetoresistance measurement for field-dependent transport characterization
measurement_type: MR
instruments: [source_meter, dmm, gaussmeter, electromagnet_supply]
version: "1.0"
---

## Protocol

1. **Connect** instruments and verify identity via *IDN?
2. **Configure** source meter: DC current mode, set compliance voltage
3. **Set** source current to {current} A (typical: 10 uA - 1 mA for thin films)
4. **Configure** electromagnet power supply for field sweep
5. **Sweep** magnetic field from {field_start} to {field_stop} Oe in {field_step} Oe steps:
   - At each field point:
     a. Set field and wait {settling_time} s for stabilization
     b. Read actual field from gaussmeter
     c. Measure longitudinal voltage V_xx (4-wire)
     d. Calculate R_xx = V_xx / I
     e. Record field, R_xx
6. **Reverse** sweep direction (field_stop -> field_start) and repeat
7. **Optional**: Rotate sample for angular-dependent MR (AMR)
8. **Optional**: Measure at multiple temperatures for T-dependent MR
9. **Zero** magnetic field
10. **Disable** source meter output
11. **Save** data to {output_dir} as CSV

## Expected Output

- R vs H curve (up-sweep and down-sweep)
- MR ratio = [R(H) - R(0)] / R(0) * 100 (%)
- Coercive field H_c from resistance switching
- For AMR: R vs angle plot, AMR ratio
- For GMR/TMR: parallel and antiparallel resistance states, MR ratio

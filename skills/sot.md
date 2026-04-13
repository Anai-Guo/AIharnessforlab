---
name: SOT Loop Shift
description: Spin-orbit torque characterization via current-induced loop shift
measurement_type: SOT
instruments: [source_meter, ac_current_source, dmm, gaussmeter]
version: "1.0"
---

## Protocol

1. **Connect** all instruments and verify identity
2. For each pulse current amplitude I_pulse in {pulse_start} to {pulse_stop} mA:
   a. Configure K6221 for pulse: amplitude={I_pulse}, width=1ms
   b. Sweep field from {field_start} to {field_stop} Oe:
      - Apply pulse
      - Wait settling time
      - Read V_xy (Hall voltage)
   c. Reverse sweep and repeat
   d. Save loop data for this current
3. **Zero** field and disable all outputs
4. **Analyze**: Extract loop center shift vs I_pulse

## Expected Output

- Family of R_xy vs H loops at different I_pulse
- Loop shift (H_shift) vs I_pulse → linear slope gives SOT efficiency

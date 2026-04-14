---
name: Delta Mode Measurement
description: Ultra-low resistance measurement using K6221+K2182A delta mode for thermal EMF elimination
measurement_type: Delta
instruments: [k6221_current_source, k2182a_nanovoltmeter]
version: "1.0"
---

## Protocol

1. **Connect** K6221 and K2182A via Trigger Link cable and RS-232/GPIB
2. **Verify** identity of both instruments via *IDN?
3. **Configure** K2182A nanovoltmeter:
   - Range: auto or fixed {voltage_range} V (typical: 10 mV for low-R)
   - NPLC = {nplc} (typical: 5 for noise rejection)
   - Analog filter: ON
4. **Configure** K6221 delta mode:
   - Current amplitude: {current} A (typical: 1-100 mA)
   - Delta delay: {delta_delay} s (typical: auto or 2-5 ms)
   - Number of delta readings: {count} (typical: 100)
   - Compliance voltage: {compliance} V
5. **Arm** K6221 delta mode: `SOUR:DELT:ARM`
6. **Start** measurement: K6221 alternates +I / -I, K2182A captures voltage at each polarity
7. **Read** delta values: V_delta = (V(+I) - V(-I)) / 2 eliminates thermal EMF
8. **Calculate** resistance: R = V_delta / I
9. **Repeat** or sweep external parameter (temperature, field) as needed
10. **Disable** output on K6221
11. **Save** data to {output_dir} as CSV

## Expected Output

- Mean resistance R with standard deviation
- Individual delta readings for noise assessment
- R vs time (for stability monitoring)
- Thermal EMF estimate: V_offset = (V(+I) + V(-I)) / 2
- Resistance resolution typically < 1 uOhm with proper setup

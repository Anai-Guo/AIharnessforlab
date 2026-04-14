---
name: CV Measurement
description: Capacitance-voltage profiling for semiconductor doping and interface characterization
measurement_type: CV
instruments: [lcr_meter, dc_bias_source]
version: "1.0"
---

## Protocol

1. **Connect** instruments and verify identity via *IDN?
2. **Configure** LCR meter:
   - AC test signal: frequency = {frequency} Hz (typical: 1 MHz for standard CV)
   - AC amplitude = {ac_level} V (typical: 10-50 mV, small-signal regime)
   - Measurement mode: Cp-D or Cs-Rs (parallel or series model)
3. **Configure** DC bias source or LCR internal bias
4. **Sweep** DC bias from {v_start} V to {v_stop} V in {v_step} V steps:
   - At each bias point:
     a. Set DC bias voltage
     b. Wait {settling_time} s for depletion region equilibration
     c. Measure capacitance C and dissipation factor D (or conductance G)
     d. Record bias voltage, C, D
5. **Optional**: Reverse sweep for hysteresis (interface traps indicator)
6. **Optional**: Multi-frequency CV sweep at {freq_list} Hz for frequency dispersion
7. **Zero** DC bias
8. **Save** data to {output_dir} as CSV

## Expected Output

- C vs V curve showing accumulation, depletion, and inversion regions
- 1/C^2 vs V (Mott-Schottky plot) with linear fit
- Doping concentration N_d or N_a from Mott-Schottky slope
- Built-in potential V_bi from x-intercept
- Oxide capacitance C_ox and oxide thickness (for MOS structures)
- Flatband voltage V_fb and interface trap density D_it (if multi-frequency)

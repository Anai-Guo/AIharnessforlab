---
name: Hall Effect Measurement
description: Standard Hall effect measurement for carrier density and mobility extraction
measurement_type: Hall
instruments: [source_meter, dmm, gaussmeter, switch_matrix]
version: "1.0"
---

## Protocol

1. **Connect** instruments and verify identity via *IDN?
2. **Configure** switch matrix for van der Pauw geometry (or Hall bar contacts)
3. **Set** source current to {current} A (typical: 10-100 uA for semiconductors)
4. **Apply** perpendicular magnetic field {field} Oe (fixed or swept)
5. For each measurement configuration:
   a. Source current I+ through contacts 1-3, measure V across 2-4 (V_24)
   b. Reverse current I- through contacts 3-1, measure V across 2-4
   c. Average: V_H = (V_24(+I) - V_24(-I)) / 2
6. **Repeat** at reversed field (-B) for offset elimination:
   - R_H = [V_H(+B) - V_H(-B)] / (2 * I * B) * d
7. **Optional**: Sweep field from {field_start} to {field_stop} for linearity check
8. **Measure** sheet resistance via van der Pauw method (rotate contacts)
9. **Disable** source output and zero field
10. **Save** data to {output_dir} as CSV

## Expected Output

- Hall coefficient R_H (m^3/C)
- Carrier density n = 1 / (R_H * e) (cm^-3)
- Sheet resistance R_s (Ohm/sq)
- Hall mobility mu_H = R_H / (rho * d) (cm^2/V-s)
- V_H vs B plot for linearity verification

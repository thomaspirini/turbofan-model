# Turbojet Engine Model

A one-dimensional thermodynamic model of a turbojet engine implemented in Python, based on the Brayton cycle with real component efficiencies and pressure losses.

## Description

This project simulates the thermodynamic cycle of a turbojet engine, modelling each component individually: inlet/diffuser, compressor, combustion chamber, turbine, and nozzle. The model accounts for real-gas irreversibilities through isentropic efficiencies and total-pressure recovery factors.

The simulation supports a Mach number sweep (M0 < 1) to analyse how flight conditions affect engine performance.

## Features

- Inlet ram compression as a function of flight Mach number
- Real compressor and turbine modelling with isentropic efficiency
- Fuel-to-air ratio from energy balance in the combustion chamber
- Choked nozzle detection and pressure thrust contribution
- Output: thrust, specific thrust, SFC for each Mach number

## Main outputs

- Thrust F [N]
- Specific thrust F/ṁa [N·kg⁻¹·s]
- Specific Fuel Consumption SFC [kg/(N·s)]
- Full thermodynamic state at each engine station (T, P)

## How to run

```bash
python turbojet_model.py
```

The script will ask whether to use default parameters or custom input values.

**Default configuration:**
- T_amb = 288 K, P_amb = 101325 Pa
- Compressor pressure ratio β = 10
- Turbine inlet temperature T4 = 1200 K
- Air mass flow ṁa = 1 kg/s
- Mach sweep: M0 = 0.0, 0.5, 0.9

## Theory

Full derivation of each component model is documented in `turbojet_model(theory).pdf`, including governing equations, assumptions, and thermodynamic relations.

## Author

Thomas Pirini — Mechanical Engineering, Politecnico di Milano

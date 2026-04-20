# Pirini Thomas

import math

# Gas constants (air)
GAMMA = 1.4
CP    = 1004.0   # J/(kg·K)
R     = 287.0    # J/(kg·K)

# Fixed component parameters
SIGMA_D = 0.98   # diffuser total-pressure ratio
SIGMA_B = 0.95   # combustor total-pressure ratio

ETA_C   = 0.85   # compressor isentropic efficiency
ETA_T   = 0.90   # turbine isentropic efficiency
ETA_N   = 0.98   # nozzle efficiency
ETA_M   = 0.99   # shaft mechanical efficiency

ETA_B   = 0.99   # combustor efficiency
PCI     = 43e6   # J/kg  kerosene LHV


def float_conversion(m):
    while True:
        text = input(m).strip()
        try:
            return float(text)
        except ValueError:
            print("Invalid value, please try again.")


def data():
    use_defaults = input("Use default data? (y/n): ").strip().lower()

    if use_defaults == 'n':
        print('use realistic values')
        T_amb = float_conversion("Ambient temperature T_amb [K]: ")
        P_amb = float_conversion("Ambient pressure P_amb [Pa]: ")
        beta = float_conversion("Compressor pressure ratio beta: ")
        T4 = float_conversion("Turbine inlet total temperature T4 [K]: ")
        m_a = float_conversion("Air mass flow m_a [kg/s]: ")

        # Ask how many Mach values the user wants to test
        n_mach = int(float_conversion("How many Mach numbers do you want to test (mach number<1.0)? (0.0) "))
        M0_list = []
        for i in range(n_mach):
            M0_list.append(float_conversion(f"Mach number M0 #{i+1}: "))

    else:
        T_amb = 288.0        # K
        P_amb = 101325.0     # Pa
        beta = 10.0          # compressor pressure ratio
        T4 = 1200.0          # K (turbine inlet total temperature)
        m_a = 1.0            # kg/s
        M0_list = [0.0, 0.5, 0.9]

    return T_amb, P_amb, beta, T4, m_a, M0_list


# main
T_amb, P_amb, beta, T4, m_a, mach_sweep = data()

for M0 in mach_sweep:

    # ---- Inlet: convert ambient static -> inlet totals (ram)
    Tt1 = T_amb * (1.0 + (GAMMA - 1.0) / 2.0 * M0**2)
    Pt1 = P_amb * (1.0 + (GAMMA - 1.0) / 2.0 * M0**2) ** (GAMMA / (GAMMA - 1.0))

    # Flight speed (uses AMBIENT STATIC temperature)
    V0 = M0 * math.sqrt(GAMMA * R * T_amb)

    # 1 -> 2 Diffuser (TOTAL quantities)
    T2 = Tt1
    P2 = SIGMA_D * Pt1

    # 2 -> 3 Compressor (REAL, TOTAL)
    P3 = P2 * beta

    # ideal isentropic temperature
    T3s = T2 * (beta ** ((GAMMA - 1.0) / GAMMA))

    # real temperature with compressor efficiency
    T3 = T2 + (T3s - T2) / ETA_C

    # 3 -> 4 Combustor (TOTAL)
    P4 = SIGMA_B * P3

    # Fuel-to-air ratio f from energy balance
    den = ETA_B * PCI - CP * T4
    if den <= 0:
        raise ValueError("Denominator <= 0: Tt4 too high (CP*T4 >= ETA_B*PCI).")

    f = CP * (T4 - T3) / den
    if f <= 0:
        raise ValueError("f <= 0: check parameters (need Tt4 > Tt3).")

    m_g = (1.0 + f) * m_a  # gas mass flow

    # 4 -> 5 Turbine (power balance + mechanical efficiency)
    T5 = T4 - (T3 - T2) / ((1.0 + f) * ETA_M)
    if T5 <= 1.0:
        raise ValueError("Tt5 not physical (too low). Check parameters.")

    # Turbine efficiency -> equivalent isentropic temperature
    T5s = T4 - (T4 - T5) / ETA_T
    if T5s <= 1.0:
        raise ValueError("Tt5s not physical: check ETA_T and parameters.")

    # Turbine outlet TOTAL pressure using isentropic relation
    P5 = P4 * ((T5s / T4) ** (GAMMA / (GAMMA - 1.0)))

    # ---- Nozzle with choking (compare against ambient static back pressure)
    P_star = P5 * (2.0 / (GAMMA + 1.0)) ** (GAMMA / (GAMMA - 1.0))

    if P_amb <= P_star:
        choked = True
        Pe = P_star
    else:
        choked = False
        Pe = P_amb

    # Exit temperature from isentropic expansion to Pe
    Te = T5 * (Pe / P5) ** ((GAMMA - 1.0) / GAMMA)

    # Ideal exit speed
    Ve_ideal = math.sqrt(max(0.0, 2.0 * CP * (T5 - Te)))

    # Real exit speed with nozzle efficiency
    Ve = math.sqrt(ETA_N) * Ve_ideal

    # Exit area from continuity
    rho_e = Pe / (R * Te)
    Ae = m_g / (rho_e * Ve)

    # Performance
    specific_thrust_simplified = (1.0 + f) * Ve

    # Full thrust (momentum + pressure thrust)
    F = m_g * Ve - m_a * V0 + (Pe - P_amb) * Ae
    specific_thrust_full = F / m_a

    if F > 0:
        m_f = f * m_a
        SFC = m_f / F
        SFC_h = SFC * 3600.0
    else:
        SFC = float("inf")
        SFC_h = float("inf")

    # ---- Prints
    print(f"""===================================

        Turbojet operating conditions:
        M0 = {M0:.2f}   V0 = {V0:.2f} m/s

        Ambient conditions: T_amb = {T_amb:.2f} K   P_amb = {P_amb:.0f} Pa
        Inlet total conditions: Tt1 = {Tt1:.2f} K   Pt1 = {Pt1:.0f} Pa

        Pressure losses: sigma_d = {SIGMA_D}   sigma_b = {SIGMA_B}
        Efficiencies: eta_c = {ETA_C}   eta_t = {ETA_T}   eta_n = {ETA_N}   eta_m = {ETA_M}

        Diffuser outlet: Tt2 = {T2:.2f} K   Pt2 = {P2:.0f} Pa
        Compressor isentropic outlet temperature: Tt3s = {T3s:.2f} K
        Compressor real outlet: Tt3 = {T3:.2f} K   Pt3 = {P3:.0f} Pa

        Combustor: Tt4 = {T4:.2f} K   Pt4 = {P4:.0f} Pa   f = {f:.5f}

        Turbine real outlet: Tt5 = {T5:.2f} K
        Turbine isentropic equivalent: Tt5s = {T5s:.2f} K
        Turbine outlet pressure: Pt5 = {P5:.0f} Pa

        Nozzle choked? {choked}   Pe = {Pe:.0f} Pa   (P* = {P_star:.0f} Pa)
        Exit static temperature (isentropic): Te = {Te:.2f} K

        Exit velocity: Ve_ideal = {Ve_ideal:.2f} m/s   Ve_real = {Ve:.2f} m/s
        Exit area: Ae = {Ae:.6e} m^2

        Performance:
        Thrust (full) = {F:.2f} N   (for m_a = {m_a:.2f} kg/s)
        Specific thrust (full) F/m_a = {specific_thrust_full:.2f} N/(kg/s)
        Specific thrust (approx.) ~(1+f)*Ve = {specific_thrust_simplified:.2f} N/(kg/s)

        SFC (full) = {SFC:.6e} kg/(N·s)   |   {SFC_h:.6e} kg/(N·h)
        """)

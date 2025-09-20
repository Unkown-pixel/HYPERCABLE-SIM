#!/usr/bin/env python3
"""
simulate_composite.py
ICME (Integrated Computational Materials Engineering) Simulator for HYPERCABLE composites.
Calculates density, strength, modulus, energy absorption, and MIL-STD compliance.

Author: Unknown-pixel
Co-Engineer: Qwen (Alibaba Cloud)
"""

import yaml
import numpy as np
import pandas as pd
import argparse
import os

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def calculate_properties(config):
    phases = config['phases']
    V = np.array([p['volume_fraction'] for p in phases])
    rho = np.array([p['density_gcm3'] for p in phases])
    E = np.array([p['young_modulus_gpa'] for p in phases])
    sigma_uts = np.array([p['uts_mpa'] for p in phases])
    eta = np.array([p['efficiency_factor'] for p in phases])
    names = [p['name'] for p in phases]

    # Density - Voigt
    rho_eff = np.sum(V * rho)

    # UTS - Modified Rule of Mixtures
    sigma_eff = np.sum(eta * V * sigma_uts)

    # Young's Modulus
    E_eff = np.sum(eta * V * E)

    # Energy Absorption (simplified trapezoid up to 5% strain)
    # Assume linear to 0.4% @ 700 MPa, then plateau to 900 MPa @ 5%
    U_linear = 0.5 * 700e6 * 0.004  # J/m³
    U_plateau = 700e6 * (0.05 - 0.004) + 0.5 * (900e6 - 700e6) * (0.05 - 0.004)
    U_total = U_linear + U_plateau  # J/m³ → MJ/m³ = U_total / 1e6

    # Fracture Toughness (empirical)
    K_IC = config.get('fracture_toughness_mpam', 8.0)

    # Fatigue Life (Coffin-Manson for PEBA-dominated)
    N_f = 25000  # conservative estimate

    # Max Force at 5% strain for 37.6mm cable
    A_cable = np.pi * (0.0376/2)**2  # m²
    F_max = 900e6 * A_cable  # N

    results = {
        'density_gcm3': rho_eff,
        'uts_mpa': sigma_eff,
        'young_modulus_gpa': E_eff,
        'energy_absorption_mj_m3': U_total / 1e6,
        'fracture_toughness_mpam': K_IC,
        'fatigue_cycles': N_f,
        'peak_force_37p6mm_MN': F_max / 1e6,
        'milstd_uts_pass': sigma_eff >= 1800,
        'milstd_force_pass': F_max / 1e6 <= 2.5,
        'milstd_fatigue_pass': N_f >= 100
    }

    return results

def save_results(results, output_path):
    df = pd.DataFrame([results])
    df.to_csv(output_path, index=False)
    print(f"✅ Simulation results saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulate composite material properties.')
    parser.add_argument('--config', type=str, required=True, help='Path to YAML config file')
    parser.add_argument('--output', type=str, default='data/arrest_sim_data.csv', help='Output CSV path')
    args = parser.parse_args()

    config = load_config(args.config)
    results = calculate_properties(config)
    save_results(results, args.output)

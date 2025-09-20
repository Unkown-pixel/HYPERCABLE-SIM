#!/usr/bin/env python3
"""
simulate_monte_carlo.py
Monte Carlo simulation of material properties with ±5% composition tolerance.
Generates distribution of UTS, modulus, density.

Author: Unknown-pixel
Co-Engineer: Qwen
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yaml
import argparse

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def monte_carlo_properties(config, n_samples=1000):
    base_phases = config['phases']
    results = []

    for _ in range(n_samples):
        # Perturb volume fractions ±5%
        perturbed_vols = []
        for p in base_phases:
            v = p['volume_fraction']
            v_pert = np.clip(v * np.random.uniform(0.95, 1.05), 0, 1)
            perturbed_vols.append(v_pert)
        
        # Normalize to 1.0
        total = sum(perturbed_vols)
        perturbed_vols = [v / total for v in perturbed_vols]

        # Recalculate properties
        rho = np.array([p['density_gcm3'] for p in base_phases])
        E = np.array([p['young_modulus_gpa'] for p in base_phases])
        sigma_uts = np.array([p['uts_mpa'] for p in base_phases])
        eta = np.array([p['efficiency_factor'] for p in base_phases])

        rho_eff = np.sum(np.array(perturbed_vols) * rho)
        sigma_eff = np.sum(eta * np.array(perturbed_vols) * sigma_uts)
        E_eff = np.sum(eta * np.array(perturbed_vols) * E)

        results.append({
            'density_gcm3': rho_eff,
            'uts_mpa': sigma_eff,
            'young_modulus_gpa': E_eff
        })

    return pd.DataFrame(results)

def plot_distributions(df, save_path):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Density
    axes[0].hist(df['density_gcm3'], bins=30, color='blue', alpha=0.7, edgecolor='black')
    axes[0].axvline(2.0, color='red', linestyle='--', label='Target: 2.0 g/cm³')
    axes[0].set_title('Density Distribution (g/cm³)')
    axes[0].legend()

    # UTS
    axes[1].hist(df['uts_mpa'], bins=30, color='green', alpha=0.7, edgecolor='black')
    axes[1].axvline(2246, color='red', linestyle='--', label='Target: 2,246 MPa')
    axes[1].set_title('UTS Distribution (MPa)')
    axes[1].legend()

    # Modulus
    axes[2].hist(df['young_modulus_gpa'], bins=30, color='orange', alpha=0.7, edgecolor='black')
    axes[2].axvline(173.3, color='red', linestyle='--', label='Target: 173 GPa')
    axes[2].set_title('Young’s Modulus Distribution (GPa)')
    axes[2].legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()
    print(f"✅ Monte Carlo distributions saved to: {save_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Monte Carlo simulation on composite properties.')
    parser.add_argument('--config', type=str, required=True, help='Path to YAML config file')
    parser.add_argument('--samples', type=int, default=1000, help='Number of Monte Carlo samples')
    parser.add_argument('--save', type=str, default='docs/figures/monte_carlo.png', help='Output image path')
    args = parser.parse_args()

    config = load_config(args.config)
    df_results = monte_carlo_properties(config, args.samples)
    df_results.to_csv('data/monte_carlo_results.csv', index=False)
    plot_distributions(df_results, args.save)

Run 
python src/simulate_monte_carlo.py --config configs/hypercable_4113_mod1.yaml --save docs/figures/monte_carlo.png

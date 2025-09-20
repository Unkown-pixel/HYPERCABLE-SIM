#!/usr/bin/env python3
"""
plot_stress_strain.py
Generates stress-strain curve for HYPERCABLE material (0-5% strain).

Author: Unknown-pixel
Co-Engineer: Qwen
"""

import pandas as pd
import matplotlib.pyplot as plt
import argparse
import numpy as np

def plot_curve(save_path):
    # Simulated stress-strain data (0 to 5% strain)
    strain = np.linspace(0, 0.05, 100)
    stress = np.zeros_like(strain)

    # Linear elastic: 0-0.4%
    mask1 = strain <= 0.004
    stress[mask1] = (173e9) * strain[mask1]  # E = 173 GPa

    # Nonlinear plateau: 0.4%-5.0%
    mask2 = strain > 0.004
    stress[mask2] = 700e6 + (900e6 - 700e6) * (strain[mask2] - 0.004) / (0.05 - 0.004)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(strain * 100, stress / 1e6, 'b-', linewidth=3, label='HYPERCABLE-4113-MOD1')
    plt.axvline(x=5, color='r', linestyle='--', label='Strain Limiter (5%)')
    plt.axhline(y=2246, color='g', linestyle=':', label='UTS (2,246 MPa)')
    plt.title('Stress-Strain Curve — HYPERCABLE Composite (0–5% Strain)', fontsize=14)
    plt.xlabel('Strain (%)', fontsize=12)
    plt.ylabel('Stress (MPa)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()
    print(f"✅ Stress-strain plot saved to: {save_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot stress-strain curve.')
    parser.add_argument('--data', type=str, help='Not used — for future expansion')
    parser.add_argument('--save', type=str, required=True, help='Output image path')
    args = parser.parse_args()

    plot_curve(args.save)

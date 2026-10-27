import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# Resolve paths dynamically relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'outputs')
OUTPUT_PLOT = os.path.join(OUTPUT_DIR, 'transient_report.png')

def analyze_step_response():
    print("--- Simulating and Analyzing Transient Step Response ---")
    
    # 1. Generate Dummy Transient Data (RC Delay + Noise)
    t = np.linspace(0, 0.0001, 10000)  # 100 microseconds
    v_final = 3.3
    tau = 0.00001  # 10us time constant
    v = v_final * (1 - np.exp(-t / tau))
    v_noisy = v + np.random.normal(0, 0.02, len(t))

    # 2. Calculate 10% to 90% Rise Time
    v_10 = 0.10 * v_final
    v_90 = 0.90 * v_final
    
    idx_10 = np.where(v_noisy >= v_10)[0][0]
    idx_90 = np.where(v_noisy >= v_90)[0][0]
    
    t_10 = t[idx_10]
    t_90 = t[idx_90]
    rise_time_us = (t_90 - t_10) * 1e6

    # 3. Calculate Slew Rate (dV/dt in V/us)
    delta_v = v_noisy[idx_90] - v_noisy[idx_10]
    delta_t_us = rise_time_us
    slew_rate = delta_v / delta_t_us

    print(f"Rise Time (10-90%): {rise_time_us:.2f} µs")
    print(f"Slew Rate:          {slew_rate:.2f} V/µs")

    # 4. Plotting & Export
    plt.figure(figsize=(8, 4))
    plt.plot(t * 1e6, v_noisy, color='green', label='Measured Transient')
    plt.axvline(t_10 * 1e6, color='r', linestyle='--', label='10% Mark')
    plt.axvline(t_90 * 1e6, color='b', linestyle='--', label='90% Mark')
    plt.title(f'Transient Step Response | Slew Rate: {slew_rate:.2f} V/µs')
    plt.xlabel('Time [µs]')
    plt.ylabel('Voltage [V]')
    plt.legend()
    plt.grid(True)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plt.savefig(OUTPUT_PLOT)
    print(f"Transient report saved to: {OUTPUT_PLOT}")

if __name__ == "__main__":
    analyze_step_response()
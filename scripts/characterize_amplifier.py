import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_FILE = os.path.join(PROJECT_ROOT, 'data', 'raw_oscilloscope_trace.csv')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'outputs')

def process_bench_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        print("Please run the data generation script first!")
        return

    # 1. Load Data
    print(f"Loading bench data from {file_path}...")
    df = pd.read_csv(file_path)
    t = df['Time (s)'].values
    v = df['Voltage (V)'].values
    
    # Calculate sample rate
    dt = t[1] - t[0]
    fs = 1 / dt
    N = len(v)

    # 2. Perform FFT (Time to Frequency Domain)
    print("Running FFT analysis...")
    yf = fft(v)
    xf = fftfreq(N, dt)[:N//2]
    magnitude = 2.0/N * np.abs(yf[0:N//2])
    
    # Convert magnitude to Decibels (dB)
    magnitude_db = 20 * np.log10(magnitude + 1e-12)

    # 3. Calculate Advanced Datasheet Metrics (SNR, THD, SFDR)
    # Find fundamental frequency peak
    peak_idx = np.argmax(magnitude)
    fundamental_power = magnitude[peak_idx]**2
    fundamental_db = magnitude_db[peak_idx]

    # Calculate Noise Floor and SNR
    noise_mask = magnitude < (np.max(magnitude) * 0.1)
    noise_power = np.mean(magnitude[noise_mask])**2
    snr_db = 10 * np.log10(fundamental_power / noise_power)

    # Calculate SFDR (Difference between fundamental and next highest spur)
    spurs = magnitude_db.copy()
    spurs[max(0, peak_idx-5) : min(len(spurs), peak_idx+5)] = -100 # Mask fundamental
    sfdr_db = fundamental_db - np.max(spurs)

    # Calculate THD (Simplified: summing power of first 5 harmonics)
    harmonics_power = 0
    for i in range(2, 6):
        harm_idx = min(peak_idx * i, len(magnitude)-1)
        harmonics_power += magnitude[harm_idx]**2
    thd_percent = np.sqrt(harmonics_power) / np.sqrt(fundamental_power) * 100

    print(f"Calculated SNR:  {snr_db:.2f} dB")
    print(f"Calculated SFDR: {sfdr_db:.2f} dB")
    print(f"Calculated THD:  {thd_percent:.4f} %")

    # 4. Generate Automated Test Report (Plots)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # Time Domain Plot
    ax1.plot(t[:500], v[:500], color='blue')
    ax1.set_title('Oscilloscope Time-Domain Trace (Zoomed)')
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Voltage [V]')
    ax1.grid(True)

    # Frequency Domain Plot (FFT)
    ax2.plot(xf, magnitude_db, color='red')
    ax2.set_title(f'Frequency Spectrum (FFT) | SNR: {snr_db:.2f} dB')
    ax2.set_xlabel('Frequency [Hz]')
    ax2.set_ylabel('Magnitude [dB]')
    ax2.set_xlim(0, 5000)
    ax2.grid(True)

    plt.tight_layout()
    output_plot = os.path.join(OUTPUT_DIR, 'test_report.png')
    plt.savefig(output_plot)
    print(f"Test report saved to: {output_plot}")

if __name__ == "__main__":
    process_bench_data(DATA_FILE)
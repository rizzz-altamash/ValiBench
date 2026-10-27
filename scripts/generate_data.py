import numpy as np
import pandas as pd
import os

# Resolve paths dynamically relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'raw_oscilloscope_trace.csv')

# Bench setup parameters
sample_rate = 100000  # 100 kHz sampling rate
duration = 0.05       # 50 milliseconds of data
frequency = 1000      # 1 kHz test signal

# Generate time axis
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

# Generate signal (ideal amplifier output) + thermal noise
clean_signal = 2.5 * np.sin(2 * np.pi * frequency * t) # 2.5V amplitude
noise = np.random.normal(0, 0.2, clean_signal.shape)   # 200mV noise floor
noisy_signal = clean_signal + noise

# Save to CSV (mimicking a Tektronix or Keysight oscilloscope export)
os.makedirs(DATA_DIR, exist_ok=True)
df = pd.DataFrame({'Time (s)': t, 'Voltage (V)': noisy_signal})
df.to_csv(OUTPUT_FILE, index=False)
print(f"Oscilloscope data successfully created at: {OUTPUT_FILE}")

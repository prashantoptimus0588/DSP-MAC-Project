"""
STEP 1 - Audio Preparation
Reads .flac audio, converts to 16-bit PCM integers,
exports .hex file (for Verilog) and .npy file (for Python golden model)
"""

import os

import numpy as np
import soundfile as sf

# Config - change filename if needed
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
INPUT_FILE = os.path.join(PROJECT_DIR, "Audio", "84-121123-0002.flac")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "Output")
OUTPUT_HEX = os.path.join(OUTPUT_DIR, "audio_samples.hex")
OUTPUT_NPY = os.path.join(OUTPUT_DIR, "audio_samples.npy")
NUM_SAMPLES = 256
START_SAMPLE = 5376


def choose_start_index(data_int16, requested_start, window_size):
    """Fall back to the highest-energy window if the requested window is silent."""
    max_start = len(data_int16) - window_size
    if max_start < 0:
        raise ValueError(
            f"Audio file has only {len(data_int16)} samples, fewer than NUM_SAMPLES={window_size}."
        )

    start = min(max(requested_start, 0), max_start)
    requested_window = data_int16[start : start + window_size]
    if np.count_nonzero(requested_window) > 0:
        return start, requested_window, False

    best_start = 0
    best_score = -1
    for idx in range(max_start + 1):
        window = data_int16[idx : idx + window_size]
        score = int(np.sum(np.abs(window), dtype=np.int64))
        if score > best_score:
            best_score = score
            best_start = idx

    best_window = data_int16[best_start : best_start + window_size]
    return best_start, best_window, True


os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Read FLAC file
data_float, sample_rate = sf.read(INPUT_FILE)
if data_float.ndim > 1:
    # Convert stereo or multi-channel input to mono for a single-stream MAC test.
    data_float = np.mean(data_float, axis=1)

print(f"Loaded: {os.path.basename(INPUT_FILE)}")
print(f"   Sample Rate  : {sample_rate} Hz")
print(f"   Total Samples: {len(data_float)}")
print(f"   Duration     : {len(data_float) / sample_rate:.2f} seconds")

# 2. Convert float64 -> 16-bit signed integer
data_int16 = np.clip(np.round(data_float * 32767), -32768, 32767).astype(np.int16)
start_index, samples, used_fallback = choose_start_index(data_int16, START_SAMPLE, NUM_SAMPLES)

print(f"\nUsing {NUM_SAMPLES} samples starting at index {start_index}")
if used_fallback:
    print(f"   Requested window at {START_SAMPLE} was silent, so a non-silent window was selected.")
print(f"   Min value : {samples.min()}")
print(f"   Max value : {samples.max()}")
print(f"   Non-zero  : {int(np.count_nonzero(samples))} / {len(samples)}")
print(f"   First 10  : {samples[:10].tolist()}")

# 3. Save .hex file for Verilog testbench
with open(OUTPUT_HEX, "w") as f:
    for s in samples:
        f.write(f"{int(s) & 0xFFFF:04X}\n")
print(f"\nSaved: {OUTPUT_HEX}")

# 4. Save .npy file for Python golden model
np.save(OUTPUT_NPY, samples)
print(f"Saved: {OUTPUT_NPY}")

print("\nStep 1 complete.")
print("Next -> run step2_golden_model.py")

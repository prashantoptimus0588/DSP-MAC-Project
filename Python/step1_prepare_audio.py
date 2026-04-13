"""
STEP 1 - Audio Preparation (FULL AUDIO FIXED)
Reads .flac audio, converts to 16-bit PCM integers,
exports FULL .hex file and .npy file
"""

import os
import numpy as np
import soundfile as sf

# Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

INPUT_FILE = os.path.join(PROJECT_DIR, "Audio", "84-121123-0003.flac")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "Output")
OUTPUT_HEX = os.path.join(OUTPUT_DIR, "audio_samples.hex")
OUTPUT_NPY = os.path.join(OUTPUT_DIR, "audio_samples.npy")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Read FLAC file
data_float, sample_rate = sf.read(INPUT_FILE)

# Convert to mono if stereo
if data_float.ndim > 1:
    data_float = np.mean(data_float, axis=1)

print(f"Loaded: {os.path.basename(INPUT_FILE)}")
print(f"   Sample Rate  : {sample_rate} Hz")
print(f"   Total Samples: {len(data_float)}")
print(f"   Duration     : {len(data_float) / sample_rate:.2f} seconds")

# 2. Convert float -> int16
data_int16 = np.clip(np.round(data_float * 32767), -32768, 32767).astype(np.int16)

# ✅ USE FULL AUDIO (FIX)
samples = data_int16

print("\nUsing FULL audio")
print(f"   Total samples : {len(samples)}")
print(f"   Min value     : {samples.min()}")
print(f"   Max value     : {samples.max()}")
print(f"   First 10      : {samples[:10].tolist()}")

# 3. Save HEX file (FULL)
with open(OUTPUT_HEX, "w") as f:
    for s in samples:
        f.write(f"{int(s) & 0xFFFF:04X}\n")

print(f"\nSaved FULL HEX: {OUTPUT_HEX}")

# 4. Save NPY file
np.save(OUTPUT_NPY, samples)
print(f"Saved FULL NPY: {OUTPUT_NPY}")

print("\n✅ Step 1 complete (FULL AUDIO)")
print("Next -> run step2_golden_model.py")
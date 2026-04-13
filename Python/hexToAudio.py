"""
hexToAudio.py  —  FIXED
Converts the Verilog filtered output back to a playable WAV file.
FIX: path was '../output/' (lowercase) — Linux is case-sensitive, must be '../Output/'
"""

import numpy as np
import soundfile as sf
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
root       = os.path.join(script_dir, "..")
out_dir    = os.path.join(root, "Output")   # capital O — matches actual folder

hex_path = os.path.join(out_dir, "audio_samples.hex")   # original input samples
wav_path = os.path.join(out_dir, "output.wav")

hex_values = []
with open(hex_path, "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        val = int(line, 16)
        # Two's complement: convert unsigned 16-bit → signed
        if val >= 0x8000:
            val -= 0x10000
        hex_values.append(val)

audio_int16 = np.array(hex_values, dtype=np.int16)
audio_float = audio_int16 / 32768.0

sf.write(wav_path, audio_float, 16000)
print(f"✅ Audio saved as {wav_path}  ({len(audio_int16)} samples)")
"""
STEP 2 - Python Golden Model (FIXED)
3-tap FIR filter with correct MAC arithmetic
"""

import os

import matplotlib.pyplot as plt
import numpy as np

# Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
OUTPUT_DIR = os.path.join(PROJECT_DIR, "Output")
INPUT_NPY = os.path.join(OUTPUT_DIR, "audio_samples.npy")
OUTPUT_TXT = os.path.join(OUTPUT_DIR, "golden_output.txt")
OUTPUT_PLOT = os.path.join(OUTPUT_DIR, "golden_plot.png")

# FIR Filter Coefficients (simple low-pass averaging filter)
# Using small integers so multiplication stays in range
B0 = 1
B1 = 2
B2 = 1
SCALE = 4   # divide by 4 at end (B0+B1+B2 = 4, keeps energy same)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Load samples
samples = np.load(INPUT_NPY).astype(np.int32)
print(f"Loaded {len(samples)} samples")
print(f"   Sample values (first 10): {samples[:10].tolist()}")
print(f"   Coefficients: B0={B0}, B1={B1}, B2={B2}, SCALE=/{SCALE}")


# 2. MAC function - correct version
def mac_operation(x, b, acc):
    """
    One MAC step:
    - Multiply x * b (both integers)
    - Add to accumulator
    - NO saturation here - accumulate freely
    Returns new accumulator value
    """
    product = int(x) * int(b)
    return acc + product


# 3. Saturation - applied ONCE on final result only
def saturate_16bit(value):
    """Clamp to 16-bit signed range: -32768 to +32767"""
    if value > 32767:
        return 32767
    if value < -32768:
        return -32768
    return value


# 4. Run 3-tap FIR filter
print("\nRunning FIR filter...")
output = []

for n in range(len(samples)):
    x0 = int(samples[n])
    x1 = int(samples[n - 1]) if n >= 1 else 0
    x2 = int(samples[n - 2]) if n >= 2 else 0

    # Three MAC operations
    acc = 0
    acc = mac_operation(x0, B0, acc)
    acc = mac_operation(x1, B1, acc)
    acc = mac_operation(x2, B2, acc)

    # Scale down then saturate
    acc = acc // SCALE
    acc = saturate_16bit(acc)

    output.append(acc)

output = np.array(output, dtype=np.int32)

print("Filter complete!")
print(f"   Input  range : {samples.min()} to {samples.max()}")
print(f"   Output range : {output.min()} to {output.max()}")
print(f"   First 10 input : {samples[:10].tolist()}")
print(f"   First 10 output: {output[:10].tolist()}")

# 5. Save golden output
with open(OUTPUT_TXT, "w") as f:
    f.write("# 3-Tap FIR Filter Golden Output\n")
    f.write(f"# Coefficients: B0={B0} B1={B1} B2={B2} SCALE={SCALE}\n")
    f.write("# Format: [index]  [decimal]  [hex]\n")
    f.write("#\n")
    for i, val in enumerate(output):
        f.write(f"{i:4d}  {val:8d}  {int(val) & 0xFFFF:04X}\n")
print(f"\nSaved: {OUTPUT_TXT}")

# 6. Plot
fig, axes = plt.subplots(3, 1, figsize=(12, 9))
fig.suptitle("DSP MAC Unit - 3-Tap FIR Filter (Python Golden Model)", fontsize=14)

axes[0].plot(samples, color="steelblue", linewidth=0.8)
axes[0].set_title("Input Signal (all 256 samples)")
axes[0].set_ylabel("Amplitude")
axes[0].grid(True, alpha=0.3)

axes[1].plot(output, color="darkorange", linewidth=0.8)
axes[1].set_title("FIR Filter Output  y[n] = (x[n] + 2*x[n-1] + x[n-2]) / 4")
axes[1].set_ylabel("Amplitude")
axes[1].grid(True, alpha=0.3)

axes[2].plot(samples, color="steelblue", linewidth=0.8, label="Input", alpha=0.7)
axes[2].plot(output, color="darkorange", linewidth=0.8, label="Output", alpha=0.7)
axes[2].set_title("Overlay - Input vs Output (smoothing effect visible)")
axes[2].set_xlabel("Sample Index")
axes[2].set_ylabel("Amplitude")
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_PLOT, dpi=150)
print(f"Saved plot: {OUTPUT_PLOT}")
print("\nStep 2 complete. Golden model is ready.")
print("Next -> Step 3: Verilog Booth's Multiplier")

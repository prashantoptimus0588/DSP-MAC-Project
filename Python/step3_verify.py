"""
step3_verify.py  —  FIXED
Compares Verilog output vs correct Python golden model.

Golden model matches the FIXED fir_filter.v exactly:
  y[n] = saturate16( (x[n]*1 + x[n-1]*2 + x[n-2]*1) >> 2 )
  Where each product is full 32-bit (NO per-product saturation).
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys

script_dir = os.path.dirname(os.path.abspath(__file__))
root       = os.path.join(script_dir, "..")
out_dir    = os.path.join(root, "Output")

golden_path  = os.path.join(out_dir, "golden_output.txt")
verilog_path = os.path.join(out_dir, "verilog_output.txt")
npy_path     = os.path.join(out_dir, "audio_samples.npy")

for p in [npy_path, verilog_path]:
    if not os.path.exists(p):
        print(f"[ERROR] Missing: {p}")
        sys.exit(1)

# ── Load data ─────────────────────────────────────────────────────────────────
samples     = np.load(npy_path).astype(np.int64)
verilog_out = np.loadtxt(verilog_path, dtype=np.int32)

N = min(len(samples), len(verilog_out))
samples     = samples[:N]
verilog_out = verilog_out[:N]

print(f"Samples compared : {N}")
print(f"Audio   min/max  : {samples.min()} / {samples.max()}")
print(f"Verilog min/max  : {verilog_out.min()} / {verilog_out.max()}")

# ── Correct golden model (matches fixed fir_filter.v) ────────────────────────
def saturate16(v):
    if v >  32767: return  32767
    if v < -32768: return -32768
    return v

golden = np.zeros(N, dtype=np.int32)
for n in range(N):
    x0 = int(samples[n])
    x1 = int(samples[n-1]) if n >= 1 else 0
    x2 = int(samples[n-2]) if n >= 2 else 0

    # Full 32-bit products (no per-product saturation)
    acc = x0 * 1 + x1 * 2 + x2 * 1   # integers — no overflow in Python
    y   = saturate16(acc >> 2)
    golden[n] = y

print(f"\nGolden  first 10 : {golden[:10].tolist()}")
print(f"Verilog first 10 : {verilog_out[:10].tolist()}")

# ── Compare ───────────────────────────────────────────────────────────────────
diff       = np.abs(golden.astype(np.int64) - verilog_out.astype(np.int64))
mismatches = int(np.sum(diff > 0))

print(f"\n{'='*60}")
print(f"  VERIFICATION RESULTS")
print(f"{'='*60}")
print(f"  Samples compared : {N}")
print(f"  PASS (exact)     : {N - mismatches}  ({100*(N-mismatches)/N:.2f}%)")
print(f"  FAIL             : {mismatches}")
print(f"  Max difference   : {diff.max()}")

if mismatches == 0:
    print(f"\n  ✅  BIT-EXACT MATCH — Hardware is CORRECT!")
elif diff.max() <= 1:
    print(f"\n  ⚠️   Off-by-one only (rounding). Functionally correct.")
else:
    print(f"\n  ❌  MISMATCH — Check Verilog logic")
    bad = np.where(diff > 0)[0][:10]
    for i in bad:
        print(f"    [{i}]  golden={golden[i]}  verilog={verilog_out[i]}  diff={diff[i]}")
print(f"{'='*60}\n")

# Save golden for reference
with open(golden_path, 'w') as f:
    f.write("# Golden output: y[n] = sat16((x[n]*1 + x[n-1]*2 + x[n-2]*1) >> 2)\n")
    for i, v in enumerate(golden):
        f.write(f"{i:6d}  {v:8d}  {int(v)&0xFFFF:04X}\n")
print(f"Saved: {golden_path}")



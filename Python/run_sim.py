#!/usr/bin/env python3
"""
run_sim.py  —  One script to run the entire Verilog simulation.

Usage (from project root):
    python Python/run_sim.py

What it does:
  1. Counts exact number of samples in Output/audio_samples.hex
  2. Compiles Verilog with -DN_SAMPLES=<count>  (no array size mismatch)
  3. Runs vvp simulation
  4. Prints result

Works for ANY audio file — 100 samples or 500,000 samples.
"""

import os, sys, subprocess

ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HEX     = os.path.join(ROOT, "Output", "audio_samples.hex")
VVP_OUT = os.path.join(ROOT, "Output", "fir_sim.vvp")

VERILOG_FILES = [
    "Verilog/booth_multiplier.v",
    "Verilog/saturation.v",
    "Verilog/mac_unit.v",
    "Verilog/fir_filter.v",
    "Verilog/tb_fir_filter.v",
]

# ── Step 1: Count samples ─────────────────────────────────────────────────────
if not os.path.exists(HEX):
    print(f"[ERROR] {HEX} not found. Run step1_prepare_audio.py first.")
    sys.exit(1)

with open(HEX) as f:
    n_samples = sum(1 for line in f if line.strip())

print(f"[INFO] Audio file: {n_samples} samples")

# ── Step 2: Compile ───────────────────────────────────────────────────────────
vfiles = [os.path.join(ROOT, v) for v in VERILOG_FILES]
cmd_compile = [
    "iverilog", "-g2001",
    f"-DN_SAMPLES={n_samples}",
    "-o", VVP_OUT,
] + vfiles

print(f"[RUN]  {' '.join(cmd_compile)}")
r = subprocess.run(cmd_compile, cwd=ROOT)
if r.returncode != 0:
    print("[ERROR] Compilation failed.")
    sys.exit(1)
print("[OK]   Compiled successfully.")

# ── Step 3: Simulate ──────────────────────────────────────────────────────────
print(f"[RUN]  vvp {VVP_OUT}")
print(f"       (simulating {n_samples} samples — this may take a minute...)")
r = subprocess.run(["vvp", VVP_OUT], cwd=ROOT)
if r.returncode != 0:
    print("[ERROR] Simulation failed.")
    sys.exit(1)
print("[OK]   Simulation complete.")
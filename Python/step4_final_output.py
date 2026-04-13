"""
step4_final_output.py — Final Output Comparison
================================================
Compares ORIGINAL INPUT audio vs FIR FILTERED OUTPUT (from Verilog simulation).

Shows:
  1. Time-domain overlay
  2. Difference signal  (input - output → shows what the filter removed)
  3. Frequency spectrum  (FFT of both → clearly shows low-pass effect)
  4. Saves filtered audio as output_filtered.wav

Run AFTER:
    step1_prepare_audio.py
    step2_golden_model.py
    python Python/run_sim.py        ← generates verilog_output.txt
"""

import os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import soundfile as sf

# ── Paths ──────────────────────────────────────────────────────────────────────
script_dir  = os.path.dirname(os.path.abspath(__file__))
root        = os.path.join(script_dir, "..")
out_dir     = os.path.join(root, "Output")

npy_path     = os.path.join(out_dir, "audio_samples.npy")
verilog_path = os.path.join(out_dir, "verilog_output.txt")
wav_in_path  = os.path.join(out_dir, "input_original.wav")
wav_out_path = os.path.join(out_dir, "output_filtered.wav")
plot_path    = os.path.join(out_dir, "final_comparison.png")

SAMPLE_RATE = 16000   # Hz — change if your audio uses a different rate

# ── Load files ─────────────────────────────────────────────────────────────────
for p in [npy_path, verilog_path]:
    if not os.path.exists(p):
        print(f"[ERROR] Missing file: {p}")
        sys.exit(1)

inp = np.load(npy_path).astype(np.int32)          # original input
out = np.loadtxt(verilog_path, dtype=np.int32)     # Verilog FIR output

N = min(len(inp), len(out))
inp = inp[:N]
out = out[:N]

print(f"Loaded {N} samples")
print(f"  Input  — min: {inp.min():7d}  max: {inp.max():7d}")
print(f"  Output — min: {out.min():7d}  max: {out.max():7d}")

# ── Difference signal ──────────────────────────────────────────────────────────
diff = inp.astype(np.int64) - out.astype(np.int64)  # what the filter removed
print(f"  Diff   — min: {diff.min():7d}  max: {diff.max():7d}")
print(f"  Samples where input != output : {np.sum(diff != 0)} / {N}")

# ── FFT (first 4096 samples for speed) ────────────────────────────────────────
FFT_N   = min(N, 4096)
window  = np.hanning(FFT_N)
freqs   = np.fft.rfftfreq(FFT_N, d=1.0 / SAMPLE_RATE)

fft_inp = np.abs(np.fft.rfft(inp[:FFT_N] * window))
fft_out = np.abs(np.fft.rfft(out[:FFT_N] * window))

# Convert to dB (avoid log(0))
fft_inp_db = 20 * np.log10(fft_inp + 1e-9)
fft_out_db = 20 * np.log10(fft_out + 1e-9)

# ── Plot ───────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(4, 1, figsize=(14, 14))
fig.suptitle(
    "DSP Pipelined MAC — 3-Tap FIR Filter: Input vs Hardware Output",
    fontsize=14, fontweight='bold'
)

# --- Plot 1: Time domain — first 500 samples for clarity ---
VIEW = min(N, 500)
t = np.arange(VIEW) / SAMPLE_RATE * 1000  # ms

axes[0].plot(t, inp[:VIEW], color='steelblue', linewidth=0.9, label='Original Input', alpha=0.9)
axes[0].plot(t, out[:VIEW], color='darkorange', linewidth=0.9, label='FIR Output (Verilog)', alpha=0.9)
axes[0].set_title(f"Time Domain — First {VIEW} Samples")
axes[0].set_xlabel("Time (ms)")
axes[0].set_ylabel("Amplitude")
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)

# --- Plot 2: Difference signal (what was removed) ---
axes[1].plot(t, diff[:VIEW], color='crimson', linewidth=0.8, alpha=0.85)
axes[1].axhline(0, color='black', linewidth=0.5, linestyle='--')
axes[1].set_title("Difference Signal: Input − Output  (High-frequency components removed by filter)")
axes[1].set_xlabel("Time (ms)")
axes[1].set_ylabel("Amplitude Diff")
axes[1].grid(True, alpha=0.3)

# --- Plot 3: Frequency spectrum ---
axes[2].plot(freqs / 1000, fft_inp_db, color='steelblue', linewidth=1.0, label='Input Spectrum', alpha=0.85)
axes[2].plot(freqs / 1000, fft_out_db, color='darkorange', linewidth=1.0, label='Output Spectrum', alpha=0.85)
axes[2].set_title("Frequency Spectrum (FFT) — Low-Pass Effect Clearly Visible")
axes[2].set_xlabel("Frequency (kHz)")
axes[2].set_ylabel("Magnitude (dB)")
axes[2].legend(loc='upper right')
axes[2].grid(True, alpha=0.3)
axes[2].set_xlim(0, SAMPLE_RATE / 2000)

# --- Plot 4: Spectrum difference (attenuation applied by filter) ---
attenuation = fft_inp_db - fft_out_db
axes[3].fill_between(freqs / 1000, attenuation, alpha=0.5, color='purple', label='Attenuation (dB)')
axes[3].axhline(0, color='black', linewidth=0.5, linestyle='--')
axes[3].set_title("Filter Attenuation = Input dB − Output dB  (Positive = filter reduced that frequency)")
axes[3].set_xlabel("Frequency (kHz)")
axes[3].set_ylabel("Attenuation (dB)")
axes[3].legend(loc='upper right')
axes[3].grid(True, alpha=0.3)
axes[3].set_xlim(0, SAMPLE_RATE / 2000)

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig(plot_path, dpi=150)
print(f"\nSaved plot : {plot_path}")

# ── Save WAV files ─────────────────────────────────────────────────────────────
sf.write(wav_in_path,  inp.astype(np.int16) / 32768.0, SAMPLE_RATE)
sf.write(wav_out_path, out.astype(np.int16) / 32768.0, SAMPLE_RATE)
print(f"Saved WAV  : {wav_in_path}")
print(f"Saved WAV  : {wav_out_path}")

# ── Text summary ───────────────────────────────────────────────────────────────
print(f"""
{'='*60}
  FINAL OUTPUT SUMMARY
{'='*60}
  Total samples compared : {N}
  Samples changed by FIR : {np.sum(diff != 0)} ({100*np.sum(diff!=0)/N:.2f}%)
  Samples unchanged      : {np.sum(diff == 0)} ({100*np.sum(diff==0)/N:.2f}%)

  Max amplitude change   : {np.abs(diff).max()}
  Mean amplitude change  : {np.abs(diff).mean():.2f}

  Input  RMS             : {np.sqrt(np.mean(inp.astype(float)**2)):.1f}
  Output RMS             : {np.sqrt(np.mean(out.astype(float)**2)):.1f}
  SNR (Output vs Input)  : {10*np.log10(np.mean(out.astype(float)**2) / (np.mean(diff.astype(float)**2)+1e-9)):.2f} dB

  Filter type            : 3-tap FIR low-pass
  Coefficients           : [1, 2, 1] / 4  (Gaussian smoothing)
{'='*60}
""")
"""Generates the episode's music + sound-design bed (no voices).

Usage: python3 tools/make_audio.py audio/soundtrack.wav
Timeline (seconds) follows the storyboard:
  0-90    warm plucked-guitar arpeggios in G, morning birds, light wind
  90-120  same guitar, minor chords (the warning scene)
  120-150 guitar fades, low pad, crickets come in at dusk
  150-175 night: drone, crickets stop when Junjun stops, whisper textures, heartbeat
  175     sting on the woman's face, hard silence at the cut to black (177.5)
"""
import sys, os, subprocess
import numpy as np

SR = 48000
DUR = 180.0
N = int(SR * DUR)
rng = np.random.default_rng(42)


def t_idx(t):
    return int(round(t * SR))


def env_lin(points):
    """Piecewise-linear envelope over the whole track: [(time, gain), ...]."""
    ts = np.array([p[0] for p in points]); gs = np.array([p[1] for p in points])
    return np.interp(np.arange(N) / SR, ts, gs)


def fft_filter(x, lo=None, hi=None):
    """Brick-ish band filter in the frequency domain with soft edges."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    g = np.ones_like(f)
    if hi: g *= 1 / (1 + (f / hi) ** 4)
    if lo: g *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(X * g, n)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


_pluck_cache = {}


def pluck(midi, length=3.0, bright=0.5):
    """Karplus-Strong plucked string, computed one period at a time."""
    key = (midi, length, bright)
    if key in _pluck_cache: return _pluck_cache[key]
    f = midi_hz(midi)
    P = int(round(SR / f))
    total = int(SR * length)
    out = np.zeros(total + P)
    burst = rng.uniform(-1, 1, P)
    burst = bright * burst + (1 - bright) * np.convolve(burst, np.ones(4) / 4, "same")
    out[:P] = burst
    decay = 0.996 if f < 200 else 0.993
    k = 1
    while k * P < total:
        prev = out[(k - 1) * P:k * P]
        out[k * P:(k + 1) * P] = decay * 0.5 * (prev + np.roll(prev, 1))
        k += 1
    out = out[:total]
    out *= np.minimum(1, np.linspace(0, length, total) * 400)  # tiny attack
    out *= np.exp(-np.linspace(0, length, total) * 1.1)
    _pluck_cache[key] = out
    return out


def add(buf, sig, t, gain=1.0):
    i = t_idx(t)
    if i >= len(buf): return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[:j - i] * gain


def reverb(x, seconds=1.6, mix=0.25):
    ir_n = int(SR * seconds)
    ir = rng.normal(0, 1, ir_n) * np.exp(-np.linspace(0, 6, ir_n))
    ir = fft_filter(ir, hi=5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    size = 1 << int(np.ceil(np.log2(len(x) + ir_n)))
    wet = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:len(x)]
    return (1 - mix) * x + mix * wet


# ---------------- music: guitar ----------------
guitar = np.zeros(N)
bass = np.zeros(N)
BPM = 72
eighth = 60 / BPM / 2
bar = eighth * 8
major = {  # chord: notes low->high (MIDI)
    "G":  [43, 50, 55, 59, 62, 67],
    "D/F#": [42, 50, 54, 57, 62, 66],
    "Em": [40, 47, 52, 55, 59, 64],
    "C":  [48, 52, 55, 60, 64, 67],
    "Am": [45, 52, 57, 60, 64, 69],
    "B7": [47, 51, 54, 57, 59, 63],
}
pattern = [0, 2, 3, 4, 5, 4, 3, 2]
prog_warm = ["G", "D/F#", "Em", "C"]
prog_warn = ["Em", "C", "Am", "B7"]

t = 0.6
bar_i = 0
while t < 124:
    prog = prog_warm if t < 89 else prog_warn
    chord = major[prog[bar_i % 4]]
    for k, idx in enumerate(pattern):
        nt = t + k * eighth + 0.012 * np.sin(bar_i * 3 + k)  # human timing
        vel = 0.55 + 0.25 * (k == 0) + 0.08 * np.sin(k * 1.3 + bar_i)
        add(guitar, pluck(chord[idx], 2.6, 0.45), nt, vel)
    # soft sine bass on the root
    root = midi_hz(chord[0] - 12 if chord[0] > 45 else chord[0])
    n_b = int(bar * SR)
    tb = np.arange(n_b) / SR
    add(bass, np.sin(2 * np.pi * root * tb) * np.exp(-tb * 0.9), t, 0.35)
    t += bar
    bar_i += 1

music = guitar * 0.9 + bass
music = reverb(music, 1.8, 0.28)
music_env = env_lin([(0, 0), (0.6, 0.0), (2.5, 1), (88, 1), (90, 0.8), (118, 0.8), (124, 0.0), (180, 0)])
# duck under dialogue/narration so voices can be added later
duck = np.ones(N)
for a, b in [(21, 29.6), (45.3, 54.8), (55.3, 59.7), (75.3, 84.9), (95.3, 115.5), (140.3, 149.8)]:
    duck = np.minimum(duck, 1 - 0.35 * np.clip(np.minimum((np.arange(N) / SR - a + 0.4) / 0.4,
                                                           (b + 0.4 - np.arange(N) / SR) / 0.4), 0, 1))
music *= music_env * duck

# ---------------- dusk pad ----------------
tt = np.arange(N) / SR
pad = np.zeros(N)
for m, g in [(45, 0.5), (52, 0.35), (57, 0.3), (60, 0.22), (64, 0.16)]:
    f = midi_hz(m)
    pad += g * (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 1.003 * tt))
pad *= 1 + 0.15 * np.sin(2 * np.pi * 0.2 * tt)
pad = fft_filter(pad, hi=1800)
pad *= env_lin([(0, 0), (118, 0), (126, 0.07), (146, 0.07), (152, 0.0), (180, 0)])

# ---------------- ambience: wind / leaves ----------------
noise = rng.normal(0, 1, N)
wind = fft_filter(noise, lo=150, hi=900)
wind *= 1 + 0.5 * np.sin(2 * np.pi * 0.07 * tt) * np.sin(2 * np.pi * 0.013 * tt + 1)
wind /= np.max(np.abs(wind))
wind *= env_lin([(0, 0), (1, 0.06), (148, 0.06), (152, 0.09), (175, 0.11), (177.5, 0.11), (177.52, 0), (180, 0)])

# ---------------- birds (day) ----------------
birds = np.zeros(N)
bt = 1.5
while bt < 122:
    n_chirps = rng.integers(2, 5)
    base = rng.uniform(2600, 4200)
    for c in range(n_chirps):
        L = rng.uniform(0.05, 0.11)
        n = int(L * SR)
        x = np.arange(n) / SR
        f = base + rng.uniform(600, 1400) * (x / L) * rng.choice([1, -1])
        ph = 2 * np.pi * np.cumsum(f) / SR
        add(birds, np.sin(ph) * np.sin(np.pi * x / L) ** 2, bt + c * rng.uniform(0.11, 0.18), rng.uniform(0.3, 0.6))
    bt += rng.uniform(1.2, 4.0)
birds *= env_lin([(0, 0), (1, 0.08), (110, 0.08), (122, 0.0), (180, 0)])

# ---------------- crickets (dusk -> night, stop at 156.8) ----------------
crk = np.zeros(N)
for voice_f, rate, phase in [(4300, 14, 0), (4650, 17, 1.3), (3900, 12, 2.1)]:
    chirp_gate = (np.sin(2 * np.pi * rate * tt + phase) > 0.2).astype(float)
    group = (np.sin(2 * np.pi * 0.7 * tt + phase * 2) > -0.3).astype(float)
    crk += np.sin(2 * np.pi * voice_f * tt) * chirp_gate * group
crk = fft_filter(crk, hi=7000)
crk /= np.max(np.abs(crk))
crk *= env_lin([(0, 0), (122, 0), (132, 0.025), (150, 0.03), (156.75, 0.03), (156.85, 0), (180, 0)])

# ---------------- night: drone, tension, whispers, heartbeat ----------------
drone = (np.sin(2 * np.pi * 41.2 * tt) + np.sin(2 * np.pi * 43.65 * tt) + 0.4 * np.sin(2 * np.pi * 110 * tt + np.sin(2 * np.pi * 0.1 * tt)))
drone *= env_lin([(0, 0), (148, 0), (154, 0.035), (165, 0.05), (175, 0.07), (177.5, 0.07), (177.52, 0), (180, 0)])

tension = np.sin(2 * np.pi * 1244.5 * tt) + np.sin(2 * np.pi * 1318.5 * tt) + 0.6 * np.sin(2 * np.pi * 932.3 * tt)
tension *= 1 + 0.4 * np.sin(2 * np.pi * 5.5 * tt)
tension *= env_lin([(0, 0), (158, 0), (166, 0.006), (175, 0.022), (177.5, 0.022), (177.52, 0), (180, 0)])

whisper = np.zeros(N)
breath = fft_filter(rng.normal(0, 1, N), lo=1200, hi=4500)
breath /= np.max(np.abs(breath))
for a, b, syll in [(160.9, 162.9, 3), (165.7, 169.4, 9)]:
    i0, i1 = t_idx(a), t_idx(b)
    x = np.linspace(0, 1, i1 - i0)
    shape = np.sin(np.pi * x) * (0.55 + 0.45 * np.abs(np.sin(np.pi * syll * x)))
    whisper[i0:i1] += breath[i0:i1] * shape
whisper = reverb(whisper, 2.5, 0.5) * 0.10

heart = np.zeros(N)
beat = 60 / 66
hb = 164.0
while hb < 175:
    n = int(0.25 * SR); x = np.arange(n) / SR
    thump = np.sin(2 * np.pi * 52 * x) * np.exp(-x * 22)
    add(heart, thump, hb, 0.45)
    add(heart, thump, hb + 0.24, 0.30)
    hb += beat
    beat *= 0.985  # speeds up
heart *= env_lin([(0, 1), (180, 1)])

# ---------------- sting at 175 ----------------
sting = np.zeros(N)
n = int(2.5 * SR); x = np.arange(n) / SR
boom = np.sin(2 * np.pi * np.cumsum(80 * np.exp(-x * 1.2) + 28) / SR) * np.exp(-x * 1.4)
hit = sum(np.sin(2 * np.pi * f * x) for f in (220, 233.1, 311.1, 466.2)) * np.exp(-x * 1.8) * 0.25
air = fft_filter(rng.normal(0, 1, n), lo=2000) * np.exp(-x * 4) * 0.25
add(sting, boom * 0.9 + hit + air, 175.0, 0.8)

# ---------------- mix ----------------
mono_music = music * 0.30 + pad
mono_amb = wind + birds + crk * 0.7 + drone + tension + heart + sting + whisper

# Hard silence at the cut to black.
cut = env_lin([(0, 1), (177.48, 1), (177.5, 0), (180, 0)])

# Simple stereo width: delay the ambience slightly on one side, pan birds/crickets a bit.
L = (mono_music + mono_amb) * cut
d = int(0.012 * SR)
amb_r = np.concatenate([np.zeros(d), mono_amb[:-d]])
R = (mono_music * 0.98 + amb_r) * cut
stereo = np.stack([L, R], axis=1)
stereo /= np.max(np.abs(stereo)) * 1.12

out = sys.argv[1] if len(sys.argv) > 1 else "audio/soundtrack.wav"
os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
raw = out + ".raw.wav"
pcm = (stereo * 32767).astype("<i2").tobytes()
import wave
with wave.open(raw, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm)

# FFmpeg loudness normalisation to a web/streaming level (-16 LUFS).
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw,
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), out], check=True)
os.remove(raw)
print("wrote", out)
